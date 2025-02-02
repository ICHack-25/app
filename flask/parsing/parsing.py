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

# image1_url = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
# image1_media_type = "image/jpeg"
# image1_data = base64.standard_b64encode(httpx.get(image1_url).content).decode("utf-8")



def anthropicClientSetup():
    """Setup api reference to the Anthropic AI, return the client"""
    load_dotenv()
    api_key=os.environ.get("ANTHROPIC_API_KEY")
    if api_key is None:
        raise Exception(f"Failed to load the Anthropic API from flask/parsing/.env file.")
    else:
        client = anthropic.Anthropic() # init the client NOTE need to load the .env file with api key
        return client

# Anthropic LLM
class LLM:
    def __init__(self):
        self.client = anthropicClientSetup()

    async def generate(self, prompt, system="analyse this request thoroughly"):
        """Use Anthropic to generate text based on a given prompt"""
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return message.content[0].text
    

def getMisinformationCategories():
    """List of categories considered unreliable for content moderation"""
    with open(nameToPath("misinformationCategories.txt")) as f:
        return [line.strip() for line in f.readlines()]



def encode(data):
    """returns base64 encoding of a file for anthropic vision API"""
    return base64.standard_b64encode(data.read()).decode("utf-8")

def loadFile(path):
    """Load a file from the given filepath or webpath and return its type, resolution and 64-bit encoded content."""
    if path.startswith("http://") or path.startswith("https://"):
        response = httpx.get(path)
        if response.status_code != 200:
            raise Exception(f"Failed to load the file from {path}. Status code: {response.status_code}")
        fileData = response.content
    else:
        path = nameToPath(path)
        if not os.path.exists(path): raise FileNotFoundError(f"The file {path} does not exist.")
        with open(path, "rb") as f: 
            fileData = f.read()

    return getFileType(path), base64.standard_b64encode(fileData).decode("utf-8")

def getFileType(path):
    """returns the file's MIME type, e.g. image/jpeg"""
    return mimetypes.guess_type(path)[0]

def nameToPath(fileName):
    """returns absolute path of files put into the /flask/parsing/media/ folder"""
    filepath = os.path.join(os.path.dirname(__file__), fileName) #  + "/media/"
    return filepath

def imageToText(fileType, fileData):
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": fileType,
                            "data": fileData,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Describe this file."
                    }
                ],
            }
        ],
    )
    return message.content[0].text

def moderate_message(message, misinformationCategories):
    # Convert the list of unsafe categories into a string, with each category on a new line
    unsafe_category_str = '\n'.join(misinformationCategories)
    
    # Construct the prompt for Claude, including the message and unsafe categories
    assessment_prompt = f"""
    Determine whether the following message warrants moderation, 
    based on the unsafe categories outlined below.
    
    Message:
    <message>{message}</message>

    Unsafe Categories:
    <categories>
    {unsafe_category_str}
    </categories>

    Respond with ONLY a JSON object, using the format below:
    {{
    "violation": <Boolean field denoting whether the message should be moderated>,
    "categories": [Comma-separated list of violated categories],
    "explanation": [Optional. Only include if there is a violation.]
    }}"""

    # Send the request to Claude for content moderation
    response = client.messages.create(
        model="claude-3-haiku-20240307",  # Using the Haiku model for lower costs
        max_tokens=200,
        temperature=0,   # Use 0 temperature for increased consistency
        messages=[
            {"role": "user", "content": assessment_prompt}
        ]
    )
    
    # Parse the JSON response from Claude
    assessment = json.loads(response.content[0].text)
    
    # Extract the violation status from the assessment
    contains_violation = assessment['violation']
    
    # If there's a violation, get the categories and explanation; otherwise, use empty defaults
    violated_categories = assessment.get('categories', []) if contains_violation else []
    explanation = assessment.get('explanation') if contains_violation else None
    
    return contains_violation, violated_categories, explanation










# class RecursiveRetrievalModule:
#     def __init__(self, vector_store, keyword_search, llm):
#         self.vector_store = vector_store
#         self.keyword_search = keyword_search
#         self.llm = llm

#     async def iterative_retrieve(self, initial_query: str, max_steps: int = 5) -> List[Dict]:
#         context = ""
#         query = initial_query
#         retrieved_documents = []

#         for step in range(max_steps):
#             # Retrieve documents based on the current query and context
#             combined_query = f"{query}\nContext: {context}"
#             docs = await self.vector_store.similarity_search(self._embed(combined_query), top_k=10)
#             retrieved_documents.extend(docs)

#             # Generate sub-questions or refine context using LLM
#             sub_questions = await self._generate_sub_questions(docs, context)

#             if not sub_questions:
#                 break

#             # Update context and prepare for next iteration
#             context += " " + " ".join(sub_questions)
#             query = " ".join(sub_questions)

#         return retrieved_documents

#     async def _generate_sub_questions(self, docs: List[Dict], context: str) -> List[str]:
#         prompt = f"Based on the following documents and context, generate a list of sub-questions to further explore the topic:\nDocuments: {docs}\nContext: {context}"
#         response = await self.llm.generate(prompt)
#         return self._parse_sub_questions(response)


# class RecursiveReasoningModule:
#     async def process_documents(self, retrieved_docs: List[Dict], initial_query: str) -> Dict:
#         # Synthesize information from all documents
#         synthesized_info = self._synthesize(retrieved_docs, initial_query)
        
#         # Apply domain-specific logic or constraints
#         refined_insights = self._apply_domain_logic(synthesized_info)
        
#         return {"insights": refined_insights}

# class RecursiveGenerationModule:
#     async def generate_final_answer(self, reasoning_output: Dict, initial_query: str) -> str:
#         prompt = self._build_final_prompt(reasoning_output["insights"], initial_query)
#         final_answer = await self.llm.generate(prompt, parameters={"max_length": 1500})
#         return final_answer














class DataObject():
    def __init__(self, data, relevance, datatype, timestamp, source) -> None:
        self.data = data # stored data, such as "Trump was elected twice", or "this image depicts a chirstma"
        self.relevance = relevance
        self.datatype = datatype
        self.timestamp = timestamp
        self.source = source


class VectorStore:
    def __init__(self, initial_data):
        self.documents = [initial_data]
            # {"text": "Donald Trump was NOT elected president of Ukraine.", "embedding": [0.1, 0.2]},
            # {"text": "Ukraine's current president is Volodymyr Zelenskyy.", "embedding": [0.3, 0.4]},
            # {"text": "AI-generated misinformation is becoming a major problem.", "embedding": [0.5, 0.6]},

    async def similarity_search(self, query_embedding, top_k=5):
        """Returns documents that 'match' the query (mock similarity search)"""
        return self.documents[:top_k]
    
    def add_entry(self, text, embedding):
        """Adds a new document with its embedding to the store."""
        dataObject = DataObject(text, )
        self.documents.append({"text": text, "embedding": embedding})




# class DataObject:
#     def __init__(self, data, relevance, datatype, timestamp, source, embedding=None):
#         self.data = data  # Stored text/image description
#         self.relevance = relevance  # Relevance score (if applicable)
#         self.datatype = datatype  # Type of data (text, image, etc.)
#         self.timestamp = timestamp  # When the data was added
#         self.source = source  # Source of data (URL, user input, etc.)
#         self.embedding = embedding or []  # Embedding representation

#     def compute_embedding(self, llm):
#         """Generates an embedding for the data using the LLM."""
#         loop = asyncio.get_event_loop()
#         embedding_text = loop.run_until_complete(llm.generate(f"Generate an embedding vector for: {self.data}"))
#         self.embedding = np.array([float(x) for x in embedding_text.split()])

#     def cosine_similarity(self, other_embedding):
#         """Computes the cosine similarity between this object and another embedding."""
#         if not self.embedding or not other_embedding:
#             return 0.0
        
#         dot_product = np.dot(self.embedding, other_embedding)
#         norm_a = np.linalg.norm(self.embedding)
#         norm_b = np.linalg.norm(other_embedding)
#         return dot_product / (norm_a * norm_b + 1e-10)  # Avoid division by zero


# class VectorStore:
#     def __init__(self, ):
#         self.documents = []

#     async def similarity_search(self, query_text, llm, top_k=5):
#         """Finds the top-k most similar stored documents to the query."""
#         query_embedding_text = await llm.generate(f"Generate an embedding vector for: {query_text}")
#         query_embedding = np.array([float(x) for x in query_embedding_text.split()])

#         # Compute similarities
#         similarities = [(doc, doc.cosine_similarity(query_embedding)) for doc in self.documents]
#         similarities.sort(key=lambda x: x[1], reverse=True)  # Sort by highest similarity
        
#         return [doc for doc, score in similarities[:top_k]]

#     def add_entry(self, text, llm, relevance=1.0, datatype="text", timestamp=None, source="unknown"):
#         """Adds a new document to the store after computing its embedding."""
#         data_object = DataObject(text, relevance, datatype, timestamp, source)
#         data_object.compute_embedding(llm)
#         self.documents.append(data_object)




# Recursive Retrieval Module
class RecursiveRetrievalModule:
    def __init__(self, vector_store, llm):
        self.vector_store = vector_store
        self.llm = llm

    async def iterative_retrieve(self, initial_query: str, max_steps: int = 3) -> List[Dict]:
        context = ""
        query = initial_query
        retrieved_documents = []

        for _ in range(max_steps):
            docs = await self.vector_store.similarity_search(query, top_k=3)
            retrieved_documents.extend(docs)

            # Generate sub-questions (mocked)
            sub_questions = await self.llm.generate("Generate sub-questions for: " + query)
            if not sub_questions:
                break

            query = " ".join(sub_questions)

        return retrieved_documents

# Recursive Reasoning Module
class RecursiveReasoningModule:
    async def process_documents(self, retrieved_docs: List[Dict], initial_query: str) -> Dict:
        insights = await LLM().generate("Synthesize insights from the provided data, find potential factual invalidity and explain in depth why this query might be fa: " + str(retrieved_docs))
        return {"insights": insights}

# Recursive Generation Module
class RecursiveGenerationModule:
    async def generate_final_answer(self, reasoning_output: Dict, initial_query: str) -> str:
        prompt = f""" Evaluate the reliability of the user-provided data based on the following insights: {reasoning_output['insights']}. Provide a concise and informative assessment, including a percentage of certainty (0-100%) regarding the validity of the data. Be clear and direct in your response. {reasoning_output['insights']} for query: {initial_query}"""
        return await LLM().generate(prompt)

# Test Function
async def run_recursive_pipeline(initial_query):
    vector_store = VectorStore(initial_query)
    llm = LLM()

    retrieval_module = RecursiveRetrievalModule(vector_store, llm)
    reasoning_module = RecursiveReasoningModule()
    generation_module = RecursiveGenerationModule()
    
    print("\n[STEP 1] Retrieving Documents...")
    retrieved_docs = await retrieval_module.iterative_retrieve(initial_query)
    print("Retrieved Docs:", retrieved_docs)

    print("\n[STEP 2] Processing Documents...")
    reasoning_output = await reasoning_module.process_documents(retrieved_docs, initial_query)
    print("Reasoning Output:", reasoning_output)

    print("\n[STEP 3] Generating Final Answer...")
    final_answer = await generation_module.generate_final_answer(reasoning_output, initial_query)
    print("Final Answer:", final_answer)









if __name__ == "__main__":
    client = anthropicClientSetup()

    # File you're cursing parsing, can be local path or web
    # filePath = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
    # filePath = "media/wasted.jpeg"
    filePath = "media/test1.png"
    # filePath = "https://www.facebook.com/TheProjectTV/posts/rapper-50-cent-has-posted-a-photoshopped-album-cover-replacing-his-head-with-don/1045944933561837/"
    # filePath = "media/test.pdf"

    fileType, fileData = loadFile(filePath)
    # print(f"Filetype: {fileType}")
    # print(f"fileData: {fileData}")

    if fileType.split("/")[0] == "image":
        message = imageToText(fileType, fileData)
    else:
        message = "Donald Trump is the new president of Ukraine!!"
    # tokens = (width px * height px)/750



    misinformationCategories = getMisinformationCategories()
    # Run the test
    asyncio.run(run_recursive_pipeline(message))
    # print(moderate_message(message, misinformationCategories)) 












































# allowed_user_comments = [
#     'This movie was great, I really enjoyed it. The main actor really killed it!',
#     'I hate Mondays.',
#     'It is a great time to invest in gold!'
# ]

# disallowed_user_comments = [
#     'Delete this post now or you better hide. I am coming after you and your family.',
#     'Stay away from the 5G cellphones!! They are using 5G to control you.',
#     'Congratulations! You have won a $1,000 gift card. Click here to claim your prize!'
# ]

# Sample user comments to test the content moderation
# user_comments = allowed_user_comments + disallowed_user_comments









# # Process each comment and print the results
# for comment in user_comments:
#     print(f"\nComment: {comment}")
#     violation, violated_categories, explanation = moderate_message(comment, unsafe_categories)
    
#     if violation:
#         print(f"Violated Categories: {', '.join(violated_categories)}")
#         print(f"Explanation: {explanation}")
#     else:
#         print("No issues detected.")






# import os
# import mimetypes

# class Parse:
#     def __init__(self, file):
#         pass    



# class File:
#     def __init__(self, fileType) -> None:
#         self.file = file
#         self.fileType = self.loadFile(file)