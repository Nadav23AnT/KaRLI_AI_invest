import datetime as dt, numpy as np, pandas as pd, yfinance as yf, ta
from typing import Union
from mongo_utils import load_stats, insert_daily_data


def _series(x):
    return x.squeeze() if isinstance(x, pd.DataFrame) else x

# Indicator computation + normalisation
def fetch_daily_ticker_data_normalised(ticker:str, stats:dict,
                             on: Union[dt.date, None] = None) -> pd.Series:
    if on is None:
        on = dt.date.today()
    df = yf.download(
            ticker,
            start=(on - dt.timedelta(days=120)).strftime("%Y-%m-%d"),
            end  =(on + dt.timedelta(days=1 )).strftime("%Y-%m-%d"),
            progress=False, auto_adjust=True, multi_level_index=False
    ).reset_index().rename(columns=str.lower)
    if df.empty:
        raise ValueError("Yahoo returned no data")
    df = df[['date','open','high','low','close','volume']]
    # indicators
    df['rsi']         = _series(ta.momentum.rsi(df['close'], window=14))
    df['tsi']         = _series(ta.momentum.tsi(df['close']))
    df['stochastic']  = _series(ta.momentum.stoch(df['high'], df['low'], df['close']))
    df['roc']         = _series(ta.momentum.roc(df['close']))
    df['cci']         = _series(ta.trend.cci(df['high'], df['low'], df['close']))
    df['trix']        = _series(ta.trend.trix(df['close']))
    df['mfi']         = _series(ta.volume.money_flow_index(df['high'], df['low'], df['close'], df['volume']))
    df['cmf']         = _series(ta.volume.chaikin_money_flow(df['high'], df['low'], df['close'], df['volume']))
    df['bb_percent']  = _series(ta.volatility.bollinger_pband(df['close']))
    df['adx']         = _series(ta.trend.adx(df['high'], df['low'], df['close']))
    df['vi_pos']      = _series(ta.trend.vortex_indicator_pos(df['high'], df['low'], df['close']))
    df.dropna(inplace=True)
    row = df.iloc[-1].copy()
    # normalise
    for feat, (μ, σ) in stats.items():
        z = (row[feat]-μ)/σ if σ>0 else 0.0
        row[feat] = np.clip(z, -3, 3)/3.0
    return row


def set_daily_finance_data(tickers):
    all_ticker_data = []

    for ticker in tickers:
        try:
            ticker_stats = load_stats(ticker)
            ticker_normalised_data = fetch_daily_ticker_data_normalised(ticker, ticker_stats)
            ticker_normalised_data['ticker'] = ticker
            all_ticker_data.append(ticker_normalised_data)
        except Exception as e:
            print(f"Failed to process {ticker}: {e}")

    if all_ticker_data:
        df = pd.DataFrame(all_ticker_data)
        print(df)
        insert_daily_data(df)
