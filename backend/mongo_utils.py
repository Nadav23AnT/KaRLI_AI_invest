import os

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI",
                      "mongodb+srv://adm:Aa123456@karli.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")
client = MongoClient(MONGO_URI)
db = client["KaRLi"]
users_collection = db["users"]


def sign_up(username, password, age, risk, broker_api_key, broker_api_secret):
    document = users_collection.find_one({"username": username})

    if document:
        return False
    users_collection.insert_one({
        "username": username,
        "password": password,
        "age": age,
        "risk_level": risk,
        "brokerApiKey": broker_api_key,
        "brokerApiSecret": broker_api_secret
    })
    return True


def sign_in(username, password):
    document = users_collection.find_one({"username": username, "password": password})

    if document:
        return True
    return False
