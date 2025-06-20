from pathlib import Path

import numpy as np
import pandas as pd
import datetime as dt
from stable_baselines3 import PPO
from Enums import rl_variables
from mongo_utils import fetch_data_for_inference

# Build today’s observation window (29 hist + 1 today)
def build_obs(ticker:str) -> np.ndarray:
    hist = pd.DataFrame(list(
        fetch_data_for_inference(ticker, 30)
    ))[::-1]                             # oldest→newest
    if len(hist) < rl_variables.WINDOW-1:
        raise ValueError("Not enough history in DB")

    hist_features = hist[rl_variables.FEATURE_COLS]
    hist_features = hist_features.reset_index(drop=True)
    obs = hist_features.values.astype(np.float32).flatten()
    obs = np.concatenate([obs, [rl_variables.ACCOUNT_FLAG]], dtype=np.float32)
    return obs.reshape(1, -1)


def predict_stocks_actions(tickers):
    tickers_actions = []

    script_dir = Path(__file__).parent
    model_dir = script_dir / "best_models"

    for ticker in tickers:
        model_path = model_dir / f"{ticker}_best_model"
        model = PPO.load(model_path, device="cpu")
        print(f"load model {ticker}")

        obs = build_obs(ticker)
        print("!!!!!!")
        action, _ = model.predict(obs, deterministic=True)
        action_int = int(action.item())
        label = {0: "HOLD", 1: "BUY", 2: "SELL"}[action_int]
        print(f"🗓 {dt.date.today()}   {ticker}:  {label}  (action={action_int})")
        tickers_actions.append((ticker, label))

    return tickers_actions