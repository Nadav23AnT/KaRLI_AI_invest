import numpy as np
import pandas as pd

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

