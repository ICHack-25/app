import requests
import json

BASE_URL = "https://ichack25-flask.containers.uwcs.co.uk/"  # Adjust if your Flask server runs elsewhere
API_KEY = "testkey123"

# Use a session to maintain consistent headers (including our API key)
session = requests.Session()
session.headers.update({
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
})

def print_response(resp):
    print("Status:", resp.status_code)
    try:
        print("Response:", json.dumps(resp.json(), indent=2))
    except Exception:
        print("Non-JSON response:", resp.text)

def main():
    print("=== Testing Flask Endpoints ===")

    # 1) GET /
    print("\n1) GET /")
    resp = session.get(f"{BASE_URL}/")
    print_response(resp)

    # 2) POST /protected-endpoint
    print("\n2) POST /protected-endpoint")
    data = {"message": "Hello from protected endpoint"}
    resp = session.post(f"{BASE_URL}/protected-endpoint", json=data)
    print_response(resp)

    # 3) POST /adduser
    print("\n3) POST /adduser")
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password_hash": "hashedpassword",
        "role": "user"
    }
    resp = session.post(f"{BASE_URL}/adduser", json=user_data)
    print_response(resp)
    user_id = None
    if resp.status_code == 201:
        user_id = resp.json().get("user_id")

    # 4) GET /users (new flexible endpoint)
    print("\n4) GET /users")
    resp = session.get(f"{BASE_URL}/users")
    print_response(resp)

    # 5) PUT /users/<user_id>
    if user_id:
        print(f"\n5) PUT /users/{user_id} (update role to 'admin')")
        update_data = {"role": "admin"}
        resp = session.put(f"{BASE_URL}/users/{user_id}", json=update_data)
        print_response(resp)

    # 6) DELETE /users/<user_id>
    if user_id:
        print(f"\n6) DELETE /users/{user_id}")
        resp = session.delete(f"{BASE_URL}/users/{user_id}")
        print_response(resp)

    # 7) POST /classification-results
    print("\n7) POST /classification-results")
    classification_data = {
        "classification_type": "sample-type",
        "confidence_score": 0.99,
        "model_version": "v1.0",
        "prompt": "Sample prompt text",
        "user_id": user_id if user_id else "dummy"
    }
    resp = session.post(f"{BASE_URL}/classification-results", json=classification_data)
    print_response(resp)
    class_result_id = None
    if resp.status_code == 201:
        class_result_id = resp.json().get("_id")

    # 8) GET /classification-results
    print("\n8) GET /classification-results")
    resp = session.get(f"{BASE_URL}/classification-results")
    print_response(resp)

    # 9) PUT /classification-results/<result_id>
    if class_result_id:
        print(f"\n9) PUT /classification-results/{class_result_id} (update confidence_score to 0.95)")
        update_data = {"confidence_score": 0.95}
        resp = session.put(f"{BASE_URL}/classification-results/{class_result_id}", json=update_data)
        print_response(resp)

    # 10) DELETE /classification-results/<result_id>
    if class_result_id:
        print(f"\n10) DELETE /classification-results/{class_result_id}")
        resp = session.delete(f"{BASE_URL}/classification-results/{class_result_id}")
        print_response(resp)

    # 11) POST /rag-knowledge-bases
    print("\n11) POST /rag-knowledge-bases")
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

    # 12) GET /rag-knowledge-bases
    print("\n12) GET /rag-knowledge-bases")
    resp = session.get(f"{BASE_URL}/rag-knowledge-bases")
    print_response(resp)

    # 13) PUT /rag-knowledge-bases/<entry_id>
    if rag_entry_id:
        print(f"\n13) PUT /rag-knowledge-bases/{rag_entry_id} (update source)")
        update_data = {"source": "updated_source"}
        resp = session.put(f"{BASE_URL}/rag-knowledge-bases/{rag_entry_id}", json=update_data)
        print_response(resp)

    # 14) DELETE /rag-knowledge-bases/<entry_id>
    if rag_entry_id:
        print(f"\n14) DELETE /rag-knowledge-bases/{rag_entry_id}")
        resp = session.delete(f"{BASE_URL}/rag-knowledge-bases/{rag_entry_id}")
        print_response(resp)

    # 15) POST /text-analyses
    print("\n15) POST /text-analyses")
    text_data = {
        "user_id": user_id if user_id else "dummy",
        "text_content": "This is some sample text for analysis",
        "classification_result_id": class_result_id if class_result_id else "dummy"
    }
    resp = session.post(f"{BASE_URL}/text-analyses", json=text_data)
    print_response(resp)
    text_analysis_id = None
    if resp.status_code == 201:
        text_analysis_id = resp.json().get("_id")

    # 16) GET /text-analyses
    print("\n16) GET /text-analyses")
    resp = session.get(f"{BASE_URL}/text-analyses")
    print_response(resp)

    # 17) PUT /text-analyses/<analysis_id>
    if text_analysis_id:
        print(f"\n17) PUT /text-analyses/{text_analysis_id} (update text_content)")
        update_data = {"text_content": "Updated text content"}
        resp = session.put(f"{BASE_URL}/text-analyses/{text_analysis_id}", json=update_data)
        print_response(resp)

    # 18) DELETE /text-analyses/<analysis_id>
    if text_analysis_id:
        print(f"\n18) DELETE /text-analyses/{text_analysis_id}")
        resp = session.delete(f"{BASE_URL}/text-analyses/{text_analysis_id}")
        print_response(resp)

    # 19) POST /url-analyses
    print("\n19) POST /url-analyses")
    url_data = {
        "user_id": user_id if user_id else "dummy",
        "url": "https://www.example.com",
        "classification_result_id": class_result_id if class_result_id else "dummy"
    }
    resp = session.post(f"{BASE_URL}/url-analyses", json=url_data)
    print_response(resp)
    url_analysis_id = None
    if resp.status_code == 201:
        url_analysis_id = resp.json().get("_id")

    # 20) GET /url-analyses
    print("\n20) GET /url-analyses")
    resp = session.get(f"{BASE_URL}/url-analyses")
    print_response(resp)

    # 21) PUT /url-analyses/<analysis_id>
    if url_analysis_id:
        print(f"\n21) PUT /url-analyses/{url_analysis_id} (update url)")
        update_data = {"url": "https://www.updated-example.com"}
        resp = session.put(f"{BASE_URL}/url-analyses/{url_analysis_id}", json=update_data)
        print_response(resp)

    # 22) DELETE /url-analyses/<analysis_id>
    if url_analysis_id:
        print(f"\n22) DELETE /url-analyses/{url_analysis_id}")
        resp = session.delete(f"{BASE_URL}/url-analyses/{url_analysis_id}")
        print_response(resp)

    # 23) POST /feedback
    print("\n23) POST /feedback")
    feedback_data = {
        "user_id": user_id if user_id else "dummy",
        "classification_result": class_result_id if class_result_id else "dummy",
        "feedback_text": "This is a sample feedback",
        "helpful": True
    }
    resp = session.post(f"{BASE_URL}/feedback", json=feedback_data)
    print_response(resp)
    feedback_id = None
    if resp.status_code == 201:
        feedback_id = resp.json().get("_id")

    # 24) GET /feedback
    print("\n24) GET /feedback")
    resp = session.get(f"{BASE_URL}/feedback")
    print_response(resp)

    # 25) PUT /feedback/<feedback_id>
    if feedback_id:
        print(f"\n25) PUT /feedback/{feedback_id} (update feedback_text)")
        update_data = {"feedback_text": "Updated feedback text"}
        resp = session.put(f"{BASE_URL}/feedback/{feedback_id}", json=update_data)
        print_response(resp)

    # 26) DELETE /feedback/<feedback_id>
    if feedback_id:
        print(f"\n26) DELETE /feedback/{feedback_id}")
        resp = session.delete(f"{BASE_URL}/feedback/{feedback_id}")
        print_response(resp)

    # 27) POST /upload with text only (no file)
    print("\n27) POST /upload with text only")
    upload_data = {
        "user_id": user_id if user_id else "test",
        "text": "Just a text sample, no file"
    }
    resp = session.post(f"{BASE_URL}/upload", data=upload_data)
    print_response(resp)
    upload_id = None
    if resp.status_code == 201:
        upload_id = resp.json().get("upload_id")

    # 28) POST /upload with a file
    print("\n28) POST /upload with a file")
    file_content = b"Hello, this is a test file."
    files = {"file": ("testfile.txt", file_content)}
    form_fields = {"user_id": user_id if user_id else "test"}
    # Note: when sending files we set headers separately
    resp = requests.post(
        f"{BASE_URL}/upload",
        headers={"X-API-Key": API_KEY},
        files=files,
        data=form_fields
    )
    print_response(resp)
    upload_id_2 = None
    if resp.status_code == 201:
        upload_id_2 = resp.json().get("upload_id")

    # 29) GET /upload/<upload_id>
    if upload_id:
        print(f"\n29) GET /upload/{upload_id}")
        resp = session.get(f"{BASE_URL}/upload/{upload_id}")
        print_response(resp)

        print(f"\n30) PUT /upload/{upload_id} (update text field)")
        update_data = {"text": "Updated text for upload"}
        resp = session.put(f"{BASE_URL}/upload/{upload_id}", json=update_data)
        print_response(resp)

        print(f"\n31) DELETE /upload/{upload_id}")
        resp = session.delete(f"{BASE_URL}/upload/{upload_id}")
        print_response(resp)

    # 32) GET, PUT, DELETE for second upload if exists
    if upload_id_2:
        print(f"\n32) GET /upload/{upload_id_2}")
        resp = session.get(f"{BASE_URL}/upload/{upload_id_2}")
        print_response(resp)

        print(f"\n33) PUT /upload/{upload_id_2} (update text field)")
        update_data = {"text": "Updated text for second upload"}
        resp = session.put(f"{BASE_URL}/upload/{upload_id_2}", json=update_data)
        print_response(resp)

        print(f"\n34) DELETE /upload/{upload_id_2}")
        resp = session.delete(f"{BASE_URL}/upload/{upload_id_2}")
        print_response(resp)

    # 35) DELETE all RAG knowledge base entries
    print("\n35) DELETE /rag-knowledge-bases (delete all entries)")
    resp = session.delete(f"{BASE_URL}/rag-knowledge-bases")
    print_response(resp)

    print("\n=== Testing complete ===")

if __name__ == "__main__":
    main()
