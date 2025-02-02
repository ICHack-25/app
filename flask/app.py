import json
from functools import wraps
from flask import Flask, request, jsonify, send_file, abort
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from models import *
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime
import gridfs
import io
from bson import ObjectId
from confluent_kafka import Producer
from bson.json_util import dumps


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
classification_results_collection = db["collection_results"]
text_analysis_collection = db["text_analysis"]
url_analysis_collection = db["url_analysis"]
feedback_collection = db["feedback"]
api_keys_collection = db["api_keys"]
rag_knowledge_base_collection = db["rag_knowledge_base"]

confluent_config = {
    'bootstrap.servers':'pkc-619z3.us-east1.gcp.confluent.cloud:9092',
    'security.protocol':'SASL_SSL',
    'sasl.mechanisms':'PLAIN',
    'sasl.username':'3N4YVM73XOUBVCEP',
    'sasl.password':'/LEZpcAf1SkGqYRN0jx1ekMHB74MVCArS2DnbnxCQ/Rdkgw1P9s7qMj1+3XFKlZJ'
    # Optional: You can set additional configs such as message timeout or logging
}
producer = Producer(confluent_config)

fs = gridfs.GridFS(db)

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password_hash: str

def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result.
       Triggered by poll() or flush()."""
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get the API key from the request header
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            abort(401, description="API key required")
        
        # Validate the API key in MongoDB
        key_doc = api_keys_collection.find_one({"key": api_key, "active": True})
        if not key_doc:
            abort(403, description="Invalid or inactive API key")
        
        # If you want to attach user info to the request context, you can do so here.
        return f(*args, **kwargs)
    return decorated


'''
command to test:

$headers = @{
    "Content-Type" = "application/json"
    "X-API-Key"    = "testkey123"
}

$body = '{"message": "Hello from Flask to Confluent Cloud!"}'

Invoke-RestMethod -Uri "http://localhost:5000/protected-endpoint" -Method Post -Headers $headers -Body $body

'''
@app.route('/protected-endpoint', methods=['POST'])
@require_api_key
def protected_endpoint():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    topic_name = 'topic_0'  # Ensure this topic exists in your Confluent Cloud cluster
    
    try:
        # Produce a message. Note: This is asynchronous.
        producer.produce(topic=topic_name, value=json.dumps(data), callback=delivery_report)
        # Poll for delivery reports (optional here, but recommended to flush periodically)
        producer.poll(0)
        # Optionally, flush the producer to ensure message delivery (synchronous)
        producer.flush()
    except Exception as e:
        return jsonify({"error": f"Failed to send message to Kafka: {str(e)}"}), 500

    return jsonify({"message": "Request processed and data sent to Kafka"}), 200

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

class RAGKnowledgeBaseCreate(BaseModel):
    data: str
    embeddings: List[float]
    source: str
    datatype: str
    time_published: datetime

@app.route("/rag-add", methods=['POST'])
def RAGAdd():     
    try:
        rag_data = RAGKnowledgeBaseCreate(**request.json)

        new_rag = {
            "data": rag_data.data,
            "embeddings": rag_data.embeddings,
            "source": rag_data.source,
            "datatype": rag_data.datatype,
            "time_published": rag_data.time_published
        }
        result = rag_knowledge_base_collection.insert_one(new_rag)
        return jsonify({"message": "Data added successfull", "data_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/rag-clear")
def RAGClear():
    try:
        rag_knowledge_base_collection.drop()
        return jsonify({"message": "Dropped all RAG entries"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/rag-get-all")
def RAGGetAll():
    return dumps(rag_knowledge_base_collection)

@app.route("/rag-delete", methods=['POST'])
def RAGDelete():
    try:
        rag_data = RAGKnowledgeBaseCreate(**request.json)

        result = rag_knowledge_base_collection.delete_one({
            "data": rag_data.data,
            "embeddings": rag_data.embeddings,
            "source": rag_data.source,
            "datatype": rag_data.datatype,
            "time_published": rag_data.time_published
        })
        return jsonify({"message": "Delete successfull", "num_deleted": str(result.deleted_count)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
