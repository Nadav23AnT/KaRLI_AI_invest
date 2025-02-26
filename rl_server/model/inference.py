def get_recommendation(input_data):
    # TODO: Load your model and process input_data for inference.
    # For now, return a mock recommendation.
    return {
        "actions": [
            {"asset": "AAPL", "action": "BUY"},
            {"asset": "TSLA", "action": "HOLD"}
        ]
    }
