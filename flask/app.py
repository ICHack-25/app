import json

from flask import Flask, request, jsonify, send_file
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from models import *
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime
import gridfs
import io
from bson import ObjectId


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
uploads_collection = db["uploads"]
# classification_results_collection = db["collection_results"]

fs = gridfs.GridFS(db)

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password_hash: str

@app.route("/fileupload")
def FileUpload():
    return '''
    <h1>Upload File to MongoDB GridFS</h1>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file" />
        <input type="submit" value="Upload" />
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get("file")
    url = request.form.get("url")
    text = request.form.get("text")

    # Store file in GridFS if provided
    image_id = None
    if file:
        image_id = str(fs.put(file, filename=file.filename))

    # Validate using Pydantic
    try:
        upload_data = Uploads(url=url, image_id=image_id, text=text).dict()
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    # Save to Uploads collection
    upload_id = uploads_collection.insert_one(upload_data).inserted_id

    return jsonify({
        "message": "Upload saved successfully",
        "upload_id": str(upload_id),
        "data": upload_data
    }), 201

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Find the file in GridFS by filename
    grid_out = fs.find_one({"filename": filename})
    if not grid_out:
        return jsonify({"error": "File not found"}), 404
    
    # Use send_file with an in-memory BytesIO buffer
    return send_file(
        io.BytesIO(grid_out.read()),
        attachment_filename=grid_out.filename,
        mimetype="application/octet-stream"  # or the appropriate content type
    )

@app.route("/dbtest")
def DBTest():
    users = list(users_collection.find({}))
    return json.dumps({"users":users}, default=str)

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
