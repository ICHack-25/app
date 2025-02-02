import json
import openai
import requests
from dotenv import load_dotenv
import os
from scraper import scrape



# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("GPT_API_KEY")
API_URL = "https://api.anthropic.com/v1/messages"

url = "https://api.openai.com/v1/chat/completions"

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}',
}

link = "https://www.snopes.com/fact-check/beer-egypt-pyramids-rations/"
text = scrape(link)

message = f"Analyze this content and provide statements \
            that are easy to factually check (whether they are true or false). \
            Here is the text: {text}"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": message}
]

data = {
    "model": "gpt-3.5-turbo",  # Use "gpt-4" for GPT-4 or "gpt-3.5-turbo" for GPT-3.5
    "messages": messages,
    "max_tokens": 100,
}

response = requests.post(url, headers=headers, data=json.dumps(data))

response_data = response.json()
print(response_data['choices'][0]['message']['content'])
