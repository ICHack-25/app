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


prompt_data = {
    "query":"Donald Trump is the new president of Ukraine!!",
    "links": ["https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg", "https://www.facebook.com/TheProjectTV/posts/rapper-50-cent-has-posted-a-photoshopped-album-cover-replacing-his-head-with-don/1045944933561837/"],
    "files": ["parsing/media/wasted.jpeg", "parsing/media/test1.png", "parsing/media/test.pdf"]
}
resp = session.post(f"{BASE_URL}/submit-prompt", json=prompt_data)

print_response(resp)