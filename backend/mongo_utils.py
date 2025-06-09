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


def get_user_brokerApi_credentials(username):
    document = users_collection.find_one({"username": username})

    if document:
        return {
            "api_key": document.get("brokerApiKey"),
            "api_secret": document.get("brokerApiSecret")
        }
    return None

def get_all_users_with_credentials():
    users = []

    for user in users_collection.find({}):
        username = user.get("username")
        risk = user.get("risk_level")
        api_key = user.get("brokerApiKey")
        api_secret = user.get("brokerApiSecret")

        users.append({
            "username": username,
            "risk": risk,
            "api_key": api_key,
            "api_secret": api_secret,
        })

    return users
