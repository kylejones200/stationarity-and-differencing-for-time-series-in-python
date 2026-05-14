"""Stationarity and differencing using Polars and DuckDB.

Successive differences replace pandas .diff() with DuckDB LAG() window functions.
ADF summary statistics are computed via DuckDB rather than returned as raw statsmodels output.
"""

import duckdb
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict

from statsmodels.tsa.stattools import adfuller


def compute_differences(
    df: pl.DataFrame, date_col: str, value_col: str, max_order: int
) -> List[pl.DataFrame]:
    """Return list of DataFrames: original + successive differences via DuckDB LAG()."""
    results = [df.select([date_col, value_col])]
    current = df.select([date_col, value_col])

    for order in range(1, max_order + 1):
        current = duckdb.sql(f"""
            SELECT
                "{date_col}",
                "{value_col}" - LAG("{value_col}", 1) OVER (ORDER BY "{date_col}") AS "{value_col}"
            FROM current
            ORDER BY "{date_col}"
        """).pl().drop_nulls()
        pd.concat([results, current])

    return results


def adf_summary(series: pl.Series) -> Dict:
    """Run ADF test on a Polars Series; summarise p-value and statistic via DuckDB."""
    values = series.drop_nulls().to_numpy()
    stat, pval, lags, nobs, *_ = adfuller(values, autolag="AIC")

    df = pl.DataFrame({
        "adf_statistic": [stat],
        "p_value":       [pval],
        "lags_used":     [float(lags)],
        "n_obs":         [float(nobs)],
    })
    # Round through DuckDB for uniform formatting
    return duckdb.sql("""
        SELECT
            ROUND(adf_statistic, 4) AS adf_statistic,
            ROUND(p_value,       6) AS p_value,
            lags_used,
            n_obs
        FROM df
    """).pl().row(0, named=True)


def plot_differences(
    series_list: List[pl.DataFrame],
    date_col: str,
    value_col: str,
    adf_results: List[Dict],
    output_path: Path,
):
    n = len(series_list)
    if plot:
        fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n), sharex=False)
        if n == 1:
            axes = [axes]

        for idx, (df, ax) in enumerate(zip(series_list, axes)):
            ax.plot(df[date_col].to_list(), df[value_col].to_list(),
                    color="#4A90A4", linewidth=1.2, alpha=0.85)
            info = adf_results[idx]
            label = "Original" if idx == 0 else f"Order-{idx} difference"
            ax.set_title(f"{label}  |  ADF: {info['adf_statistic']}  p={info['p_value']}")
            ax.set_ylabel("Value")

        axes[-1].set_xlabel("Index")
        plt.tight_layout()
        plt.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close()
