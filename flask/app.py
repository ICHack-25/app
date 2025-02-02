import base64
import mimetypes
import json
from flask import Flask, request, jsonify, send_file, abort
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from models import *  # This imports your Pydantic models
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime
import gridfs
import io
from bson import ObjectId
from confluent_kafka import Producer
from dotenv import load_dotenv
from pathlib import Path
import os
from bson.json_util import dumps

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# --- MongoDB Setup ---
uri = os.getenv("MONGO_URI", "")
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["db"]

# Collections
users_collection = db["users"]
uploads_collection = db["uploads"]
classification_results_collection = db["collection_results"]
text_analysis_collection = db["text_analysis"]
url_analysis_collection = db["url_analysis"]
feedback_collection = db["feedback"]
api_keys_collection = db["api_keys"]
rag_knowledge_base_collection = db["rag_knowledge_base"]

# --- Confluent Kafka Setup ---
confluent_config = {
    'bootstrap.servers': os.getenv("BOOTSTRAP_SERVERS", ""),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv("SASL_USERNAME", ""),
    'sasl.password': os.getenv("SASL_PASSWORD", "")
}
producer = Producer(confluent_config)

def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

# --- GridFS Setup ---
fs = gridfs.GridFS(db)

# --- Pydantic Model for Creating Users (to handle request payload) ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password_hash: str
    role: str = "user"

# ─── GLOBAL API KEY CHECK ─────────────────────────────────────────────
@app.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        abort(401, description="API key required")
    key_doc = api_keys_collection.find_one({"key": api_key, "active": True})
    if not key_doc:
        abort(403, description="Invalid or inactive API key")
# ─── END GLOBAL API KEY CHECK ─────────────────────────────────────────

@app.route('/protected-endpoint', methods=['POST'])
def protected_endpoint():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    topic_name = 'topic_0'
    try:
        producer.produce(topic=topic_name, value=json.dumps(data), callback=delivery_report)
        producer.poll(0)
        producer.flush()
    except Exception as e:
        return jsonify({"error": f"Failed to send message to Kafka: {str(e)}"}), 500

    return jsonify({"message": "Request processed and data sent to Kafka"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Accepts file uploads and/or a URL or text.
    At least one of `url`, `image_id`, or `text` must be provided.
    """
    file = request.files.get("file")
    url = request.form.get("url")
    text = request.form.get("text")
    user_id = request.form.get("user_id", "test")
    
    # Initialize variables for the file-related data.
    encoded_image = None
    file_type = None
    image_id = None

    if file:
        # Read the file data into memory
        file_data = file.read()
        # Encode the file in base64 so that it remains in the same format
        # for clients like Claude (Anthropic Vision API) to read.
        encoded_image = base64.standard_b64encode(file_data).decode("utf-8")
        # Determine the file’s MIME type.
        file_type = file.mimetype or mimetypes.guess_type(file.filename)[0]
        # Save the binary file to GridFS using a BytesIO stream.
        image_id = str(fs.put(io.BytesIO(file_data), filename=file.filename))
    
    try:
        # Create the Uploads model instance.
        upload_model = Uploads(
            url=url,
            image_id=image_id,
            text=text,
            user_id=user_id
        )
        
        # Convert the model to a dict using aliases.
        upload_dict = upload_model.dict(by_alias=True, exclude_unset=True)
        # Add the encoded image and file type if available.
        if encoded_image is not None:
            upload_dict["encoded_image"] = encoded_image
            upload_dict["file_type"] = file_type
        
        # Insert the document into the uploads collection.
        inserted_id = uploads_collection.insert_one(upload_dict).inserted_id
        
        # Add the generated id into our dict (as a string).
        upload_dict["_id"] = str(inserted_id)
        
        return jsonify({
            "message": "Upload saved successfully",
            "upload_id": str(inserted_id),
            "data": upload_dict
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    grid_out = fs.find_one({"filename": filename})
    if not grid_out:
        return jsonify({"error": "File not found"}), 404

    return send_file(
        io.BytesIO(grid_out.read()),
        attachment_filename=grid_out.filename,
        mimetype="application/octet-stream"
    )

@app.route("/dbtest", methods=['GET'])
def DBTest():
    users = list(users_collection.find({}))
    for user in users:
        user["_id"] = str(user["_id"])
    return json.dumps({"users": users}, default=str)

@app.route("/adduser", methods=['POST'])
def AddUser():
    """
    Creates a new user in the database.
    """
    try:
        user_data = UserCreate(**request.json)
        new_user = {
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": user_data.password_hash,
            "role": user_data.role,
            "created_at": datetime.utcnow()
        }
        result = users_collection.insert_one(new_user)
        return jsonify({"message": "User created successfully", "user_id": str(result.inserted_id)}), 201
    except ValidationError as ve:
        return jsonify({"error": ve.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- ClassificationResult Endpoints ---
@app.route("/classification-results", methods=['POST'])
def add_classification_result():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    try:
        result_model = ClassificationResult.parse_obj(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    # Exclude the 'id' field so we never pass _id=None
    result_dict = result_model.dict(by_alias=True, exclude={"id"})
    inserted = classification_results_collection.insert_one(result_dict)
    # Attach the real inserted _id
    result_dict["_id"] = str(inserted.inserted_id)
    return jsonify(result_dict), 201

@app.route("/classification-results", methods=['GET'])
def get_classification_results():
    results = list(classification_results_collection.find())
    for result in results:
        result["_id"] = str(result["_id"])
    return jsonify(results), 200

@app.route("/classification-results/<result_id>", methods=['GET'])
def get_classification_result(result_id):
    try:
        result = classification_results_collection.find_one({"_id": ObjectId(result_id)})
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400

    if not result:
        return jsonify({"error": "Classification result not found"}), 404

    result["_id"] = str(result["_id"])
    return jsonify(result), 200

# --- RAGKnowledgeBase Endpoints ---
@app.route("/rag-knowledge-bases", methods=['POST'])
def add_rag_knowledge_base():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    try:
        entry = RAGKnowledgeBase.parse_obj(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    entry_dict = entry.dict(by_alias=True, exclude={"id"})
    inserted = rag_knowledge_base_collection.insert_one(entry_dict)
    entry_dict["_id"] = str(inserted.inserted_id)
    return jsonify(entry_dict), 201

@app.route("/rag-knowledge-bases", methods=['GET'])
def get_rag_knowledge_bases():
    entries = list(rag_knowledge_base_collection.find())
    for entry in entries:
        entry["_id"] = str(entry["_id"])
    return jsonify(entries), 200

@app.route("/rag-knowledge-bases/<entry_id>", methods=['GET'])
def get_rag_knowledge_base(entry_id):
    try:
        entry = rag_knowledge_base_collection.find_one({"_id": ObjectId(entry_id)})
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400

    if not entry:
        return jsonify({"error": "RAG Knowledge Base entry not found"}), 404

    entry["_id"] = str(entry["_id"])
    return jsonify(entry), 200

# --- TextAnalysis Endpoints ---
@app.route("/text-analyses", methods=['POST'])
def add_text_analysis():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    try:
        analysis = TextAnalysis.parse_obj(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    analysis_dict = analysis.dict(by_alias=True, exclude={"id"})
    inserted = text_analysis_collection.insert_one(analysis_dict)
    analysis_dict["_id"] = str(inserted.inserted_id)
    return jsonify(analysis_dict), 201
#

@app.route("/text-analyses", methods=['GET'])
def get_text_analyses():
    analyses = list(text_analysis_collection.find())
    for analysis in analyses:
        analysis["_id"] = str(analysis["_id"])
    return jsonify(analyses), 200

@app.route("/text-analyses/<analysis_id>", methods=['GET'])
def get_text_analysis(analysis_id):
    try:
        analysis = text_analysis_collection.find_one({"_id": ObjectId(analysis_id)})
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400

    if not analysis:
        return jsonify({"error": "Text analysis not found"}), 404

    analysis["_id"] = str(analysis["_id"])
    return jsonify(analysis), 200

# --- URLAnalysis Endpoints ---
@app.route("/url-analyses", methods=['POST'])
def add_url_analysis():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    try:
        analysis = URLAnalysis.parse_obj(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    analysis_dict = analysis.dict(by_alias=True, exclude={"id"})
    inserted = url_analysis_collection.insert_one(analysis_dict)
    analysis_dict["_id"] = str(inserted.inserted_id)
    return jsonify(analysis_dict), 201

@app.route("/url-analyses", methods=['GET'])
def get_url_analyses():
    analyses = list(url_analysis_collection.find())
    for analysis in analyses:
        analysis["_id"] = str(analysis["_id"])
    return jsonify(analyses), 200

@app.route("/url-analyses/<analysis_id>", methods=['GET'])
def get_url_analysis(analysis_id):
    try:
        analysis = url_analysis_collection.find_one({"_id": ObjectId(analysis_id)})
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400

    if not analysis:
        return jsonify({"error": "URL analysis not found"}), 404

    analysis["_id"] = str(analysis["_id"])
    return jsonify(analysis), 200

# --- Feedback Endpoints ---
@app.route("/feedback", methods=['POST'])
def add_feedback():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    try:
        fb_model = Feedback.parse_obj(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    fb_dict = fb_model.dict(by_alias=True, exclude={"id"})
    inserted = feedback_collection.insert_one(fb_dict)
    fb_dict["_id"] = str(inserted.inserted_id)
    return jsonify(fb_dict), 201

@app.route("/feedback", methods=['GET'])
def get_feedbacks():
    feedbacks = list(feedback_collection.find())
    for fb in feedbacks:
        fb["_id"] = str(fb["_id"])
    return jsonify(feedbacks), 200

@app.route("/feedback/<feedback_id>", methods=['GET'])
def get_feedback(feedback_id):
    try:
        fb = feedback_collection.find_one({"_id": ObjectId(feedback_id)})
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400

    if not fb:
        return jsonify({"error": "Feedback not found"}), 404

    fb["_id"] = str(fb["_id"])
    return jsonify(fb), 200

# --- Simple RAG-Add Endpoint (sample form-data approach) ---
@app.route("/rag-add", methods=['POST'])
def RAGAdd():
    data = request.form.get('data')
    embeddings = request.form.get('embeddings')
    source = request.form.get('source')
    time_published = request.form.get('time_published')
    return jsonify({
        "data": data,
        "embeddings": embeddings,
        "source": source,
        "time_published": time_published
    }), 200

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
