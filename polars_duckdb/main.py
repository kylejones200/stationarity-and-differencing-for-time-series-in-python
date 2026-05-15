#!/usr/bin/env python3
"""Stationarity and differencing — Polars + DuckDB rewrite."""

import argparse
import logging
from pathlib import Path

import numpy as np
import polars as pl
import yaml
from core import adf_summary, compute_differences, plot_differences

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_config(config_path: Path = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Stationarity & differencing — Polars + DuckDB"
    )
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    config = load_config(args.config)

    # output dir: fall back gracefully if the config key is missing
    output_cfg = config.get("output", {})
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else Path(output_cfg.get("output_dir", "outputs"))
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # synthetic non-stationary series: random walk with drift
    rng = np.random.default_rng(42)
    n = 200
    values = np.cumsum(rng.normal(0.05, 1.0, n))
    df = pl.DataFrame(
        {
            "date": list(range(n)),
            "value": values.tolist(),
        }
    )

    max_order = config.get("model", {}).get("max_difference_order", 2)
    series_list = compute_differences(df, "date", "value", max_order)

    adf_results = [adf_summary(s["value"]) for s in series_list]
    for i, r in enumerate(adf_results):
        label = "Original" if i == 0 else f"Order-{i} diff"
        logging.info(f"{label}: ADF={r['adf_statistic']}  p={r['p_value']}")

    # save ADF table
    pl.DataFrame(adf_results).write_csv(output_dir / "adf_results.csv")
    logging.info(f"ADF results saved → {output_dir / 'adf_results.csv'}")

    plot_differences(
        series_list, "date", "value", adf_results, output_dir / "differencing_plot.png"
    )

    logging.info(f"Analysis complete. Figures saved to {output_dir}")


if __name__ == "__main__":
    main()
