import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"  # or wherever your Flask app is running
API_KEY = "testkey123"

# Use a session to keep headers consistent
session = requests.Session()
session.headers.update({
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
})

def main():
    print("=== Testing Flask Endpoints ===")

    # 1) GET /
    print("\n1) GET /")
    resp = session.get(f"{BASE_URL}/")
    print("Status:", resp.status_code)
    print("Response:", resp.text)

    # 2) POST /protected-endpoint
    print("\n2) POST /protected-endpoint")
    data_to_send = {"test": "value"}
    resp = session.post(f"{BASE_URL}/protected-endpoint", json=data_to_send)
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except:
        print("Non-JSON response:", resp.text)

    # 3) POST /adduser
    print("\n3) POST /adduser")
    new_user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password_hash": "hashedpassword",
        "role": "user"
    }
    resp = session.post(f"{BASE_URL}/adduser", json=new_user_data)
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
        if resp.status_code == 201:
            new_user_id = resp.json().get("user_id")
        else:
            new_user_id = None
    except:
        print("Non-JSON response:", resp.text)
        new_user_id = None

    # 4) GET /dbtest (list users)
    print("\n4) GET /dbtest")
    resp = session.get(f"{BASE_URL}/dbtest")
    print("Status:", resp.status_code)
    print("Response:", resp.text)

    # 5) POST /classification-results
    #    Adjust to match the ClassificationResult model’s fields:
    #    classification_type, confidence_score, model_version, prompt, reviewed_by
    print("\n5) POST /classification-results")
    classification_data = {
        "classification_type": "test-label",
        "confidence_score": 0.95,
        "model_version": "test-model",
        "prompt": "some sample prompt",
        "user_id": new_user_id if new_user_id else "some_user_id"
    }
    resp = session.post(f"{BASE_URL}/classification-results", json=classification_data)
    print("Status:", resp.status_code)
    try:
        classification_resp = resp.json()
        print("Response:", classification_resp)
        if resp.status_code == 201:
            classification_result_id = classification_resp.get("_id")
        else:
            classification_result_id = None
    except:
        print("Non-JSON response:", resp.text)
        classification_result_id = None

    # 6) GET /classification-results
    print("\n6) GET /classification-results")
    resp = session.get(f"{BASE_URL}/classification-results")
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except:
        print("Non-JSON response:", resp.text)

    # 7) GET /classification-results/<result_id>
    if classification_result_id:
        print(f"\n7) GET /classification-results/{classification_result_id}")
        resp = session.get(f"{BASE_URL}/classification-results/{classification_result_id}")
        print("Status:", resp.status_code)
        try:
            print("Response:", resp.json())
        except:
            print("Non-JSON response:", resp.text)
    else:
        print("\n7) Skipping GET /classification-results/<result_id> because we have no ID.")

    # 8) POST /rag-knowledge-bases
    #    Your RAGKnowledgeBase model requires: data, datatype, embeddings, source, time_published
    print("\n8) POST /rag-knowledge-bases")
    rag_entry_data = {
        "data": "Sample RAG knowledge base text",
        "datatype": "text",  # or whatever fits your app
        "embeddings": [0.1, 0.2, 0.3],
        "source": "sample_source",
        # time_published is not optional in your model,
        # so supply a datetime in ISO or a string your server can parse:
        "time_published": "2025-01-01T00:00:00Z"
    }
    resp = session.post(f"{BASE_URL}/rag-knowledge-bases", json=rag_entry_data)
    print("Status:", resp.status_code)
    try:
        rag_resp = resp.json()
        print("Response:", rag_resp)
        if resp.status_code == 201:
            rag_entry_id = rag_resp.get("_id")
        else:
            rag_entry_id = None
    except:
        print("Non-JSON response:", resp.text)
        rag_entry_id = None

    # 9) GET /rag-knowledge-bases
    print("\n9) GET /rag-knowledge-bases")
    resp = session.get(f"{BASE_URL}/rag-knowledge-bases")
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except:
        print("Non-JSON response:", resp.text)

    # 10) GET /rag-knowledge-bases/<entry_id>
    if rag_entry_id:
        print(f"\n10) GET /rag-knowledge-bases/{rag_entry_id}")
        resp = session.get(f"{BASE_URL}/rag-knowledge-bases/{rag_entry_id}")
        print("Status:", resp.status_code)
        try:
            print("Response:", resp.json())
        except:
            print("Non-JSON response:", resp.text)
    else:
        print("\n10) Skipping GET /rag-knowledge-bases/<entry_id> because we have no ID.")

    # 11) POST /text-analyses
    #     Model expects: user_id, text_content, classification_result_id (optional).
    print("\n11) POST /text-analyses")
    text_analysis_data = {
        "user_id": new_user_id if new_user_id else "some_user_id",
        "text_content": "Sample text content for analysis",
        # classification_result_id references the doc from step 5:
        "classification_result_id": classification_result_id  
    }
    resp = session.post(f"{BASE_URL}/text-analyses", json=text_analysis_data)
    print("Status:", resp.status_code)
    try:
        text_analysis_resp = resp.json()
        print("Response:", text_analysis_resp)
        if resp.status_code == 201:
            text_analysis_id = text_analysis_resp.get("_id")
        else:
            text_analysis_id = None
    except:
        print("Non-JSON response:", resp.text)
        text_analysis_id = None

    # 12) GET /text-analyses
    print("\n12) GET /text-analyses")
    resp = session.get(f"{BASE_URL}/text-analyses")
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except:
        print("Non-JSON response:", resp.text)

    # 13) GET /text-analyses/<analysis_id>
    if text_analysis_id:
        print(f"\n13) GET /text-analyses/{text_analysis_id}")
        resp = session.get(f"{BASE_URL}/text-analyses/{text_analysis_id}")
        print("Status:", resp.status_code)
        try:
            print("Response:", resp.json())
        except:
            print("Non-JSON response:", resp.text)
    else:
        print("\n13) Skipping GET /text-analyses/<analysis_id> because we have no ID.")

    # 14) POST /url-analyses
    #     Model expects: user_id, url, classification_result_id (optional).
    print("\n14) POST /url-analyses")
    url_analysis_data = {
        "user_id": new_user_id if new_user_id else "some_user_id",
        "url": "https://www.example.com",
        "classification_result_id": classification_result_id  # optional
    }
    resp = session.post(f"{BASE_URL}/url-analyses", json=url_analysis_data)
    print("Status:", resp.status_code)
    try:
        url_analysis_resp = resp.json()
        print("Response:", url_analysis_resp)
        if resp.status_code == 201:
            url_analysis_id = url_analysis_resp.get("_id")
        else:
            url_analysis_id = None
    except:
        print("Non-JSON response:", resp.text)
        url_analysis_id = None

    # 15) GET /url-analyses
    print("\n15) GET /url-analyses")
    resp = session.get(f"{BASE_URL}/url-analyses")
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except:
        print("Non-JSON response:", resp.text)

    # 16) GET /url-analyses/<analysis_id>
    if url_analysis_id:
        print(f"\n16) GET /url-analyses/{url_analysis_id}")
        resp = session.get(f"{BASE_URL}/url-analyses/{url_analysis_id}")
        print("Status:", resp.status_code)
        try:
            print("Response:", resp.json())
        except:
            print("Non-JSON response:", resp.text)
    else:
        print("\n16) Skipping GET /url-analyses/<analysis_id> because we have no ID.")

    # 17) POST /feedback
    #     You only get here if classification_result_id is set.
    #     Model expects: user_id, classification_result (the doc ID), feedback_text, helpful
    print("\n17) POST /feedback")
    if classification_result_id:
        feedback_data = {
            "user_id": new_user_id if new_user_id else "some_user_id",
            "classification_result": classification_result_id,  # from step 5
            "feedback_text": "This is a piece of feedback",
            "helpful": True
        }
        resp = session.post(f"{BASE_URL}/feedback", json=feedback_data)
        print("Status:", resp.status_code)
        try:
            feedback_resp = resp.json()
            print("Response:", feedback_resp)
            if resp.status_code == 201:
                feedback_id = feedback_resp.get("_id")
            else:
                feedback_id = None
        except:
            print("Non-JSON response:", resp.text)
            feedback_id = None
    else:
        print("No classification_result_id. Skipping feedback test.")
        feedback_id = None

    # 18) GET /feedback
    print("\n18) GET /feedback")
    resp = session.get(f"{BASE_URL}/feedback")
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except:
        print("Non-JSON response:", resp.text)

    # 19) GET /feedback/<feedback_id>
    if feedback_id:
        print(f"\n19) GET /feedback/{feedback_id}")
        resp = session.get(f"{BASE_URL}/feedback/{feedback_id}")
        print("Status:", resp.status_code)
        try:
            print("Response:", resp.json())
        except:
            print("Non-JSON response:", resp.text)
    else:
        print("\n19) Skipping GET /feedback/<feedback_id> because we have no ID.")

    # 20) POST /rag-add (form-data approach)
    print("\n20) POST /rag-add (form-data)")
    form_data = {
        "data": "some data here",
        "embeddings": "[1.0, 2.0]",
        "source": "test_source",
        "time_published": "2025-01-01"
    }
    resp = requests.post(
        f"{BASE_URL}/rag-add",
        headers={"X-API-Key": API_KEY},  # keep the API key
        data=form_data                  # sending as form data
    )
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except:
        print("Non-JSON response:", resp.text)

    # 21) POST /upload with text only
    #     Server must fix the Uploads validator so it doesn’t crash under Pydantic v2
    print("\n21) POST /upload with text only (no file)")
    upload_data = {
        "user_id": new_user_id if new_user_id else "test",
        "text": "Just a text sample, no file"
    }
    resp = requests.post(
        f"{BASE_URL}/upload",
        headers={"X-API-Key": API_KEY},
        data=upload_data  # or json=upload_data if the endpoint expects JSON
    )
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except:
        print("Non-JSON response:", resp.text)

    # 22) POST /upload with file
    print("\n22) POST /upload with a file")
    file_content = b"Hello, this is a test file"
    files = {
        "file": ("testfile.txt", file_content)
    }
    form_fields = {
        "user_id": new_user_id if new_user_id else "test"
    }
    resp = requests.post(
        f"{BASE_URL}/upload",
        headers={"X-API-Key": API_KEY},  # include the API key
        files=files,
        data=form_fields
    )
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except:
        print("Non-JSON response:", resp.text)

    print("\n=== Testing complete ===")

if __name__ == "__main__":
    main()
