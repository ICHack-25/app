from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient(host="mongodb://ichack25mongo.containers.uwcs.co.uk/", port=27017, username='admin', password='password', authSource="admin")

@app.route("/dbtest")
def DBTest():
    return client.admin.command('ping')

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
