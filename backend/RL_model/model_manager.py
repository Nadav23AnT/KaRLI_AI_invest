# model_manager.py
from pathlib import Path
from stable_baselines3 import PPO

class ModelManager:
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.models = {}

    def load_all_models(self):
        for model_path in self.model_dir.glob("*_best_model.zip"):
            ticker = model_path.stem.replace("_best_model", "")
            try:
                model = PPO.load(model_path, device="cpu")
                self.models[ticker] = model
                print(f"[LOADED] Model for {ticker}")
            except Exception as e:
                print(f"[ERROR] Could not load model for {ticker}: {e}")

    def get_model(self, ticker: str):
        return self.models.get(ticker)
