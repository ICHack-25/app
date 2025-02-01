from flask import Flask
from pymongo import MongoClient

uri = "mongodb+srv://nicholasmasonapps1:A2qZ34cttzqqrwck@cluster0.spui9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)

db = client["db"]

users_collection = db["users"]

app = Flask(__name__)

@app.route("/dbtest")
def DBTest():
    users = list(users_collection.find({}))
    return {"users":users}

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
