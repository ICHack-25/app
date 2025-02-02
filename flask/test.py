import requests
import json

from script import print_response

BASE_URL = "http://127.0.0.1:5000"
API_KEY = "testkey123"

# Use a session to keep headers consistent
session = requests.Session()
session.headers.update({
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
})


rag_data = {
    "data": "Sample RAG entry data",
    "datatype": "text",
    "embeddings": [0.1, 0.2, 0.3],
    "source": "test_source",
    "time_published": "2025-01-01T00:00:00Z"
}
resp = session.post(f"{BASE_URL}/rag-knowledge-bases", json=rag_data)

print_response(resp)

rag_entry_id = None
if resp.status_code == 201:
    rag_entry_id = resp.json().get("_id")