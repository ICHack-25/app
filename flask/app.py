from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from models import *
from pydantic import BaseModel, EmailStr
from datetime import datetime

app = Flask(__name__)

uri = "mongodb+srv://nicholasmasonapps1:PS8NCIboaZsytmgJ@cluster0.spui9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["db"]

users_collection = db["users"]

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password_hash: str



@app.route("/dbtest")
def DBTest():
    users = list(users_collection.find({}))
    return {"users":users}

'''
run with powershell cmd: Invoke-WebRequest -Uri "http://127.0.0.1:5000/users" -Method POST -Body '{"username": "john_doe", "email": "john@example.com", "password_hash": "hashed_password"}' -ContentType "application/json"
'''
@app.route("/adduser", methods=['POST'])
def AddUser():
    try:
        # Validate request body using Pydantic
        user_data = UserCreate(**request.json)
        
        # Create a new user document
        new_user = {
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": user_data.password_hash,
            "created_at": datetime.utcnow()
        }

        # Insert the new user into the collection
        result = users_collection.insert_one(new_user)
        
        return jsonify({"message": "User created successfully", "user_id": str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
