import anthropic
import os
import mimetypes
import base64
import httpx
from dotenv import load_dotenv
import json
from typing import List, Dict
import asyncio
import numpy as np


load_dotenv()



def anthropicSetup():
    """Setup api reference to the Anthropic AI, return the client"""    
    api_key=os.environ.get("ANTHROPIC_API_KEY")
    if api_key is None:
        raise Exception(f"Failed to load the Anthropic API from flask/parsing/.env file.")
    else:
        client = anthropic.Anthropic() # init the client NOTE need to load the .env file with api key
        return client

VOYAGE_API_KEY = os.environ.get("VOYAGE_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")


from datasets import load_dataset
import pandas as pd

# Make sure you have an Hugging Face token(HF_TOKEN) in your development environment before running the code below
# How to get a token: https://huggingface.co/docs/hub/en/security-tokens

# https://huggingface.co/datasets/MongoDB/tech-news-embeddings
dataset = load_dataset("MongoDB/tech-news-embeddings", split="train", streaming=True)
combined_df = dataset.take(500)

# Convert the dataset to a pandas dataframe
combined_df = pd.DataFrame(combined_df)


# Remove the _id coloum from the intital dataset
combined_df = combined_df.drop(columns=['_id'])

# Convert each numpy array in the 'embedding' column to a normal Python list
combined_df['embedding'] = combined_df['embedding'].apply(lambda x: x.tolist())




import voyageai

vo = voyageai.Client(api_key=VOYAGE_API_KEY)

def get_embedding(text: str) -> list[float]:
    if not text.strip():
      print("Attempted to get embedding for empty text.")
      return []

    embedding = vo.embed(text, model="voyage-large-2", input_type="document")

    return embedding.embeddings[0]

combined_df["embedding"] = combined_df["description"].apply(get_embedding)

combined_df.head()



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
{
 "fields": [{
     "numDimensions": 256,
     "path": "embedding",
     "similarity": "cosine",
     "type": "vector"
   }]
}
import pymongo


class RAG_DB():
   def __init__(self) -> None:
      pass
   def add():
      pass
   def get():
      pass
   def clear():
      pass

def get_mongo_client(mongo_uri):
  """Establish and validate connection to the MongoDB."""

  client = pymongo.MongoClient(mongo_uri, appname="devrel.showcase.anthropic_rag.python")

  # Validate the connection
  ping_result = client.admin.command('ping')
  if ping_result.get('ok') == 1.0:
    # Connection successful
    print("Connection to MongoDB successful")
    return client
  else:
    print("Connection to MongoDB failed")
  return None

mongo_uri = os.environ["MONGO_URI"]

if not mongo_uri:
  print("MONGO_URI not set in environment variables")

mongo_client = get_mongo_client(mongo_uri)

DB_NAME = "knowledge"
COLLECTION_NAME = "research_papers"

db = mongo_client.get_database(DB_NAME)
collection = db.get_collection(COLLECTION_NAME)
# To ensure we are working with a fresh collection
# delete any existing records in the collection
# collection.delete_many({})
# Data Ingestion
# combined_df_json = combined_df.to_dict(orient='records')
# collection.insert_many(combined_df_json)



def vector_search(user_query, collection):
    """
    Perform a vector search in the MongoDB collection based on the user query.

    Args:
    user_query (str): The user's query string.
    collection (MongoCollection): The MongoDB collection to search.

    Returns:
    list: A list of matching documents.
    """

    # Generate embedding for the user query
    query_embedding = get_embedding(user_query)

    if query_embedding is None:
        return "Invalid query or embedding generation failed."

    # Define the vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 150,  # Number of candidate matches to consider
                "limit": 5  # Return top 5 matches
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "embedding": 0,  # Exclude the embedding field
                "score": {
                    "$meta": "vectorSearchScore"  # Include the search score
                }
            }
        }
    ]

    # Execute the search
    results = collection.aggregate(pipeline)
    return list(results)


# class DataLoader:
#     def __init__(self) -> None:
#         pass
