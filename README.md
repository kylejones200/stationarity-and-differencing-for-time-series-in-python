# Repository

Companion code for a Medium article.

## Business context

Some time series data follows clear trends or patterns, making it hard to model accurately. Most statistical methods assume stationarity -- meaning the average level and variability of the series stay the same over time. But real-world data rarely cooperates. Temperatures rise, economies grow, and demand cycles up and down. If you don't adjust for these trends, your models will misfire.

One of the simplest ways to fix this is differencing. Instead of working with the raw values, you subtract each observation from the one before it. This removes trends and makes the data more stable.

To illustrate, consider a time series with a clear upward trend. It keeps climbing, making it obvious that some kind of transformation is needed. The first step is first-order differencing, which subtracts each value from the one before it. This flattens a linear trend into a more stable series. If the trend is more complex -- curved instead of straight -- a single difference isn't enough. A second difference, which applies the same operation again to the first differenced series, may be needed.

## Disclaimer

Educational/demo code only. Not financial, safety, or engineering advice. Use at your own risk. Verify results independently before any production or operational use.

## License

MIT — see [LICENSE](LICENSE).