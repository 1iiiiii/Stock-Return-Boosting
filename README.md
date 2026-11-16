# Can gradient boosting pick stocks? 
Findings:

- **Class experiment.** 45 teams. Intuition $101,179, indicators $103,087; mean difference +$1,909, paired t = 1.68 (p = 0.10 two-sided, 0.05 one-sided), 95% bootstrap interval −$340 to +$4,109. Indicators finished ahead for 30 of 45 teams. With this spread it would take about 62 teams for a difference of this size to reach t = 1.96.
- **The class script's own numbers are inflated.** It reports a Sharpe ratio of 8.8 and an alpha of 330% a year because it annualises monthly returns with the factors for daily returns. With the monthly factors the same numbers are 1.9 and 16%.
- **Prediction.** No model ranks stocks reliably. Average monthly rank correlation between prediction and outcome (rank IC): class model 0.045 (t = 2.1; 1.8 without the first month, whose outcomes overlap the model's training targets), improved model 0.024 (t = 0.7). Out-of-sample R²: −0.063 and +0.003.
- **Investment.** $1 became $2.50 with the improved model, $2.09 with the class model, $1.69 with all 96 stocks and $1.66 with SPY. But the improved model's portfolio is 1.6 times as sensitive to the market as SPY and twice as volatile, its Sharpe ratio (1.06) is below the class model's (1.21) and the 96-stock portfolio's (1.15), and its return in excess of the 96 stocks has t = 1.2.
- **It is a momentum bet.** A rule with no model, "buy the ten stocks with the best past year", returned +142% with a Sharpe ratio of 1.08. Its daily returns in excess of the 96 stocks have a 0.82 correlation with the improved model's.
- **Against 10,000 random ten-stock portfolios** the improved model is ahead of 99% on total return and 26% on return per unit of risk; the class model 93% and 75%.

Published post: https://1iiiiii.github.io/Personal-Website/blog/posts/post9/

## Data

| File | What it contains | Source | Period |
|---|---|---|---|
| `data/raw/prices_yahoo.csv` | daily open, high, low, close, volume and dividend-adjusted close for 96 U.S. large-cap stocks, `SPY` (S&P 500 ETF) and `^IRX` (13-week Treasury-bill yield, % a year) | Yahoo Finance chart endpoint, downloaded 13 Nov 2026 (`data/raw/fetch_log.json`); set `REFETCH = True` in notebook 01 to download again with `yfinance` | 4 Jan 2010 – 12 Nov 2026 (ABBV, META, NOW and TSLA start later) |
| `data/raw/class_experiment_results.xlsx` | one row per team: final value of the intuition portfolio (`portfolio1`) and the indicator portfolio (`portfolio2`) | the instructor's results file for the Fall 2026 class | about two months, September – November 2026 |
| `reference/original_XGBoostStockPrediction.R` | the class XGBoost script, unchanged | course materials (Yisroel Cahn) | |
| `reference/original_stockmarketgameresults.R` | the instructor's analysis of the class results, unchanged | course materials | |

## Replication

Run the notebooks in `code/` in order; each reads the previous ones' output. Paths are built from `Path.cwd().parent`, so run them from `code/` (VS Code's default).

| Notebook | Reads | Writes |
|---|---|---|
| `01_fetch.ipynb` | Yahoo Finance (only when `REFETCH = True`) | `data/raw/prices_yahoo.csv`, `fetch_log.json`; `data/processed/price_coverage.csv` |
| `02_class_experiment.ipynb` | `data/raw/class_experiment_results.xlsx` | `results/tables/class_experiment.csv`, `class_experiment_teams.csv` |
| `03_original_model.ipynb` | `data/raw/prices_yahoo.csv` | `data/processed/pred_original.csv`; `results/tables/original_as_scripted.csv`, `original_as_scripted_monthly.csv`, `original_feature_importance.csv` |
| `04_improved_model.ipynb` | `data/raw/prices_yahoo.csv` | `data/processed/calendar.csv`, `panel.csv`, `pred_clean.csv`, `pred_long.csv`, `pred_improved.csv`, `pred_linear.csv`, `pred_momentum.csv`; `results/tables/tuning_grid.csv`, `tuning_choice.json`, `improved_feature_importance.csv` |
| `05_evaluate.ipynb` | prices, `calendar.csv`, every `pred_*.csv` | `results/tables/predictive.csv`, `investment.csv`, `ic_by_period.csv`, `period_returns.csv`, `daily_returns.csv`, `daily_returns_net.csv`, `random_portfolios.csv`, `random_summary.csv`, `holdings.csv`, `most_held.csv`, `holdings_overlap.csv`, `active_return_correlation.csv`, `difficulty.csv`, `eval_settings.json` |
| `06_figures.ipynb` | `results/tables/` | `results/figures/fig1_class_experiment.html`, `fig2_growth.html`, `fig3_random_portfolios.html` (also copied into the post folder when the website repository sits next to this one) |

### The class model as written (`03_original_model.ipynb`)

What the notebook documents and the later notebooks change:

1. Raw price levels and share volume are predictors.
2. The momentum features are inverted (older price over newer price).
3. The target is the raw return, most of which is the market's move.
4. Eighteen months of training data, fitted once.
5. The last training rows have targets that end inside the test period.
6. The backtest sets a 19-day return against SPY's calendar-month return, and SPY's line starts two years earlier.
7. Sharpe ratio and alpha are annualised with daily factors applied to monthly numbers.
8. Weights proportional to the prediction concentrate the portfolio.
9. The 96 tickers were chosen in 2026, so they are companies known to be large today.

### The improvement (`04_improved_model.ipynb`)

| Model | What changes from the row above |
|---|---|
| `original` | the class script as written |
| `clean` | twelve price-based features (momentum over 12, 6 and 3 months, reversal over a month and a week, volatility over 1 and 6 months, beta, volatility not explained by the market, distance from the one-year high, largest daily gain, dollar-volume trend), each ranked across stocks every day; target = the stock's 20-day return minus the average stock's; a 21-trading-day gap between the last training row and the day being predicted. Same training window and hyperparameters as the class script |
| `long` | trained on 2011–2023, on every fifth trading day |
| `improved` | hyperparameters chosen on two validation folds before the test period (2020–21 and 2022–23), scored by rank IC; refitted on each rebalance date on everything known by then. Chosen: 100 trees, depth 2, learning rate 0.01, minimum child weight 20, row and column subsampling 0.7 (validation rank IC 0.046, against 0.027 for the class settings) |
| `linear` | ordinary least squares on the same features, refitted monthly |
| `momentum` | no model: rank by the past year's return, skipping the last month |

### The evaluation (`05_evaluate.ipynb`)

One procedure for every model: decide on the first trading day of the month, buy the ten highest-ranked stocks in equal amounts at the next day's close, hold to the next month's entry date. 34 complete periods, 3 January 2024 to 3 November 2026. Daily returns come from daily prices, so every strategy covers the same days.

- **Predictive performance:** monthly rank IC and its t-statistic; out-of-sample R² against the forecast "every stock earns the average"; the ten picks' mean return minus the average stock's; the share of picks that beat the median stock.
- **Investment performance:** annual return, volatility, Sharpe ratio over the Treasury-bill rate (daily returns, √252), maximum drawdown, alpha and beta against SPY, return in excess of the 96-stock portfolio with its t-statistic, monthly turnover, return after a cost of 10 basis points per dollar traded.
- **Random portfolios:** 10,000 portfolios that pick ten of the 96 stocks at random every month on the same calendar; each strategy's percentile on total return and on return per unit of risk.

## Results (`results/tables/`)

Out of sample, 3 January 2024 – 3 November 2026, before trading costs. Every model row is the ten highest-ranked stocks in equal amounts.

| Strategy | Rank IC (t) | Out-of-sample R² | Total return | Volatility | Sharpe ratio | Beta to SPY | Excess over the 96 stocks, a year (t) | Monthly turnover | Total return after costs | Ahead of random portfolios: return / return per unit of risk |
|---|---|---|---|---|---|---|---|---|---|---|
| SPY | | | +66% | 15.4% | 0.97 | 1.00 | −0.2% (0.0) | 0% | +66% | 50% / 72% |
| All 96 stocks, equal weight | | | +69% | 13.1% | 1.15 | 0.77 | | 3% | +68% | 53% / 90% |
| Class model (`original`) | 0.045 (2.1) | −0.063 | +109% | 19.8% | 1.21 | 0.94 | +8.8% (1.1) | 64% | +101% | 93% / 75% |
| Step 1 (`clean`) | 0.012 (0.5) | −0.121 | +64% | 23.8% | 0.68 | 1.29 | +1.0% (0.1) | 61% | +57% | 46% / 10% |
| Step 2 (`long`) | 0.000 (0.0) | −0.012 | +133% | 24.0% | 1.19 | 1.28 | +13.5% (1.4) | 57% | +124% | 99% / 42% |
| Step 3 (`improved`) | 0.024 (0.7) | +0.003 | +150% | 31.1% | 1.06 | 1.63 | +17.9% (1.2) | 24% | +145% | 99% / 26% |
| Linear regression | 0.029 (0.8) | +0.001 | +104% | 31.0% | 0.83 | 1.65 | +10.7% (0.7) | 36% | +99% | 91% / 12% |
| 12-month momentum rule | 0.041 (0.9) | | +142% | 29.0% | 1.08 | 1.43 | +16.2% (1.2) | 29% | +138% | 99% / 27% |
| Class model, the script's own weights | | | +151% | 21.8% | 1.41 | 0.97 | +15.6% (1.7) | 65% | +140% | 99% / 74% |

How noisy the problem is (`difficulty.csv`): in an average month one stock's return differs from the average stock's by 8.6 percentage points (standard deviation), and the improved model's forecasts differ from stock to stock by 0.34 points. The improved model's ten-stock portfolio strays from the 96-stock portfolio by 24.5% a year, so the excess return it showed (17.9% a year) would need to persist for about 7.5 years to reach t = 2; the test period is 2.8 years.

What the improved model held (`most_held.csv`, `holdings_overlap.csv`): MU and AMD in 31 of 34 months, INTC in 30, AVGO and TSLA in 28. It shares 4.9 of its ten stocks with the momentum rule in an average month and 2.7 with the class model. Its two most important features are six-month volatility and six-month volatility not explained by the market.

## Caveats

- The 96 stocks were picked with hindsight; results say nothing about a universe chosen in 2024.
- One test period of 34 months, most of it a rising market. A portfolio with a beta of 1.6 looks good in such a period for reasons that have nothing to do with stock selection.
- Six models were tested on the same 34 months; the largest t-statistic among them (2.1) is less convincing than a single t of 2.1 would be.
- Trades are filled at closing prices with a flat cost; no market impact, taxes or borrowing.
- The Python port of the class script is not numerically identical to the R original.

## Layout

```
code/             01_fetch … 06_figures (notebooks), plotly_style.py
data/raw/         prices_yahoo.csv, class_experiment_results.xlsx, fetch_log.json
data/processed/   calendar.csv, pred_<model>.csv, price_coverage.csv (panel.csv is written by notebook 04, not committed)
reference/        the two instructor scripts, unchanged
results/tables/   every number quoted in the post
results/figures/  the three interactive HTML figures
```
