from flask import Flask, request, jsonify
# from flask_cors import CORS

import mongo_utils
from Enums.risk import RISK

app = Flask(__name__)
# CORS(app)

RISK_LEVELS = [risk.value for risk in RISK]


@app.route('/signUp', methods=['POST'])
def sign_up():
    data = request.json
    user_name = data.get('username')
    password = data.get('password')
    age = data.get('age')
    risk_level = data.get('risk')

    if not user_name or not password or not age or risk_level not in RISK_LEVELS:
        return jsonify({"error": "Invalid input: Some fields are missing"}), 400

    if mongo_utils.sign_up(user_name, password, age, risk_level):
        return jsonify(True), 200
    return jsonify({"error": "Username already exists"}), 400


@app.route('/signIn', methods=['POST'])
def sign_in():
    data = request.json
    user_name = data.get('username')
    password = data.get('password')

    if mongo_utils.sing_in(user_name, password):
        return jsonify(True)
    return "username or password are incorrect", 401


@app.route("/risks", methods=["GET"])
def get_risk_levels():
    return jsonify({"risks": RISK_LEVELS})


if __name__ == '__main__':
    app.run(debug=True, threaded=False)
