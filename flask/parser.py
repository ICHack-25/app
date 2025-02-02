import anthropic
import os
# import mimetypes
# import base64
# import httpx
from dotenv import load_dotenv
import json
from typing import List, Dict
import asyncio
import requests


load_dotenv()
BASE_URL = "http://127.0.0.1:5000"


################ SETUP Anthropic API ####################
def anthropicClientSetup():
    """Setup api reference to the Anthropic AI, return the client"""
    api_key=os.environ.get("ANTHROPIC_API_KEY")
    if api_key is None:
        raise Exception(f"Failed to load the Anthropic API from flask/parsing/.env file.")
    else:
        client = anthropic.Anthropic() # init the client NOTE need to load the .env file with api key
        return client

client = anthropicClientSetup()




################ Initialise system-prompt-specific Anthropic LLM ####################
class LLM:
    def __init__(self, system):
        self.client = anthropicClientSetup()
        self.system = system

    async def generate(self, prompt):
        """Use Anthropic to generate text based on a given prompt"""
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0,
            system=self.system,
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
    


################ MongoDB Connection Setup ####################
class DataObject: # object containing prompt data attributes
    def __init__(self, data, datatype, embeddings, source, time_published):
        self.data = data # str
        self.datatype = datatype # str
        self.embeddings = embeddings # float[]
        self.source = source # str
        self.time_published = time_published # str

    def to_dict(self):
        return {
            "data": self.data,
            "datatype": self.datatype,
            "embeddings": self.embeddings,
            "source": self.source,
            "time_published": self.time_published,
        }
    
class DBStore:
    def __init__(self):
        self.documents = []

    async def similarity_search(self, query_embedding, top_k=5):
        return []
        # return self.get_all()

    def add_entry(self, data, datatype, source, time_published):
        """Adds a new document to the store."""
        new_entry = DataObject(data, datatype, [0.1,0.2], source, time_published)
        print(new_entry.to_dict())
        response = requests.post(f"{BASE_URL}/rag-knowledge-bases", json=new_entry.to_dict())  # Fixed URL
        print(response)

    def clear_all(self):
        """Clears all stored documents."""
        response = requests.delete(f"{BASE_URL}/rag-knowledge-bases", json={})  # Use DELETE method
        print(response)

    def get_all(self):
        """Returns all stored documents as dictionaries."""
        response = requests.get(f"{BASE_URL}/rag-knowledge-bases", json={})  # Use GET method
        print(response)

    def addImage(self, data, datatype, source="unknown", time_published="unknown"):
        self.add_entry(self, imageToText(data), datatype, source, time_published)

    def addText(self, data, datatype="text/plain", source="unknown", time_published="unknown"):
        self.add_entry(self, data, datatype, source, time_published)

db = DBStore() # initialise database connection








################ Turn Image into Text desciption ####################
def imageToText(fileType, fileData):
    system = """
    Please provide a highly detailed and structured description of the given image. Break down the analysis into the following categories:
    1. **General Overview**: Describe the overall content of the image, including any people, objects, or scenes visible.
    2. **People (if applicable)**: If the image contains people, provide a detailed description of their appearance, clothing, posture, and any relevant context (e.g., location, event).
    3. **Objects and Items**: List and describe any notable objects or items in the image. Focus on key visual details such as shapes, colors, text (if any), and their placement within the image.
    4. **Text or Symbols**: If the image contains any text or symbols, transcribe it exactly, and describe their size, positioning, and relevance to the image’s context.
    5. **Background and Environment**: Describe the background, surroundings, and any environmental context that is visible (e.g., cityscape, nature, indoors).
    6. **Color and Lighting**: Provide a description of the color scheme, lighting, shadows, and overall tone of the image. Are there any visual cues that suggest manipulation (e.g., unnatural lighting or color)?
    7. **Potential Indicators of Misinformation**: Analyze the image for any signs of manipulation or inconsistency that might indicate misinformation. This could include:
        - Unnatural or poorly edited elements (e.g., visible artifacts, strange lighting or shadows).
        - Contextual clues that suggest the image might be misleading (e.g., inconsistencies in clothing or object placement).
        - Any aspects of the image that conflict with known facts (e.g., location mismatches, outdated events).
    8. **Contextual Relevance**: Based on the analysis, give an assessment of how reliable the image is in conveying factual information, highlighting anything that stands out as potentially misleading or fabricated.
    9. **Additional Observations**: Any further observations that might help identify the authenticity of the image, including any references to known events, locations, or personalities.
    """
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
                        "text": system
                    }
                ],
            }
        ],
    )
    return message.content[0].text


################ Convert Local file name into global path ####################
def nameToPath(fileName):
    """returns absolute path of files put into the /flask/parsing/media/ folder"""
    filepath = os.path.join(os.path.dirname(__file__), fileName) #  + "/media/"
    return filepath


################ Fetch misinformation categories ####################
def getMisinformationCategories():
    """List of categories considered unreliable for content moderation"""
    with open(nameToPath("misinformationCategories.txt")) as f:
        return [line.strip() for line in f.readlines()]
    

################ Identify Potential Validity Vulnerabilities ####################
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





###################### Recursive Retrieval Module ######################
class RecursiveRetrievalModule:
    def __init__(self, db, llm):
        self.db = db
        self.llm = llm

    async def iterative_retrieve(self, initial_query: str, max_steps: int = 3) -> List[Dict]:
        context = ""
        query = initial_query
        retrieved_documents = []

        for _ in range(max_steps):
            docs = await self.db.similarity_search(query, top_k=3)
            retrieved_documents.extend(docs)

            # Generate sub-questions (mocked)
            sub_questions = await self.llm.generate("Generate sub-questions for: " + query)
            if not sub_questions:
                break

            query = " ".join(sub_questions)

        return retrieved_documents



###################### Recursive Reasoning Module ######################
class RecursiveReasoningModule:
    async def process_documents(self, retrieved_docs: List[Dict], initial_query: str) -> Dict:
        llm = LLM(system="You are an advanced reasoning engine that critically analyses retrieved documents. Identify key insights, detect factual inconsistencies, and explain any discrepancies in depth. Ensure logical coherence in your findings.")

        insights = await llm.generate(
            f"Synthesize insights from the provided data, identify any factual inconsistencies, and explain in detail why this query might be flawed: {retrieved_docs}"
        )
        return {"insights": insights}


###################### Recursive Generation Module ######################
class RecursiveGenerationModule:
    async def generate_final_answer(self, reasoning_output: Dict, initial_query: str) -> str:
        llm = LLM(system="You are a precise evaluator of information validity. Assess insights critically, determine the reliability of provided data, and quantify certainty in a structured manner.")
        prompt = f"""Evaluate the reliability of the user-provided data based on the following insights: {reasoning_output['insights']}. 
        - Identify whether the insights suggest factual accuracy or inconsistency.  
        - Provide a clear, structured assessment.  
        - Assign a certainty percentage (0-100%) based on the reasoning.  
        
        Final evaluation for query '{initial_query}':"""
        return await llm.generate(prompt)



###################### Final Report Generation Pipeline ######################
async def run_recursive_pipeline(initial_query):
    """Main Pipeline"""
    # initial_query = "<DataSeparator>".join([item.data for item in db.get_all()])
    # initial_query
    
    llm = LLM("analyse this request thoroughly")

    retrieval_module = RecursiveRetrievalModule(db, llm)
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
    db = DBStore()

    query = "Donald Trump is the new president of Ukraine!!"
    links = ["https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg", "https://www.facebook.com/TheProjectTV/posts/rapper-50-cent-has-posted-a-photoshopped-album-cover-replacing-his-head-with-don/1045944933561837/"]
    files = ["media/wasted.jpeg", "media/test1.png", "media/test.pdf"]


    # def add_entry(self, data, datatype, embeddings, source, time_published):
    
    # add the query
    db.add_entry(data=query, datatype="text/plain", source="a", time_published="hello") # HACK technically /plain is not a valid MIME type, but text is
    print(db.get_all())
    
    message = query

    # filePath = 

    # fileType, fileData = loadFile(filePath)
    # # print(f"Filetype: {fileType}")
    # # print(f"fileData: {fileData}")

    # if fileType.split("/")[0] == "image":
    #     message = imageToText(fileType, fileData)
    # else:
    #     message = "Donald Trump is the new president of Ukraine!!"
    # # tokens = (width px * height px)/750


    misinformationCategories = getMisinformationCategories()
    asyncio.run(run_recursive_pipeline(message))
    
    # Run the test
    # print(moderate_message(message, misinformationCategories)) 










# def getFileType(path):
#     """returns the file's MIME type, e.g. image/jpeg"""
#     return mimetypes.guess_type(path)[0]

# def loadLocalFile(path):
#     """Load a file from the given filepath and return its type and 64-bit encoded content."""
#     path = nameToPath(path)
#     if not os.path.exists(path): raise FileNotFoundError(f"The file {path} does not exist.")
#     with open(path, "rb") as f: 
#         fileData = f.read()
#     return getFileType(path), base64.standard_b64encode(fileData).decode("utf-8")


# def nameToPath(fileName):
#     """returns absolute path of files put into the /flask/parsing/media/ folder"""
#     filepath = os.path.join(os.path.dirname(__file__), fileName) #  + "/media/"
#     return filepath


# print(imageToText(*loadLocalFile(nameToPath("parsing/media/wasted.jpeg"))))































# class DataObject:
#     def __init__(self, data, datatype, embeddings, source, time_published):
#         self.data = data # str
#         self.datatype = datatype # str
#         self.embeddings = embeddings # float[]
#         self.source = source # str
#         self.time_published = time_published # str

#     def to_dict(self):
#         return {
#             "data": self.data,
#             "datatype": self.datatype,
#             "embeddings": self.embeddings,
#             "source": self.source,
#             "time_published": self.time_published,
#         }




# # Send a POST request to /rag-add
# # response = requests.post(f"{BASE_URL}/rag-add", json=rag_data)
# # print("Add Response:", response.json())

# # # Send a POST request to /rag-get
# # response = requests.post(f"{BASE_URL}/rag-get", json={})  # No payload needed
# # print("Get Response:", response.json())

# # # Send a POST request to /rag-clear
# # response = requests.post(f"{BASE_URL}/rag-clear", json={})  # No payload needed
# # print("Clear Response:", response.json())











