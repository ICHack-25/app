import anthropic
import os
from dotenv import load_dotenv
import json
from typing import List, Dict
import asyncio
import requests
import mimetypes
import base64
import httpx

load_dotenv()
BASE_URL = "http://127.0.0.1:5000" 
API_KEY = "testkey123"

# Use a session to keep headers consistent
session = requests.Session()
session.headers.update({
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
})

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

    def add_entry(self, data, datatype, embeddings, source, time_published):
        """Adds a new document to the store."""
        new_entry = DataObject(data, datatype, embeddings, source, time_published)
        # print(new_entry.to_dict())
        response = session.post(f"{BASE_URL}/rag-add", json=new_entry.to_dict())  # Fixed URL
        # print(response)

    def clear_all(self):
        """Clears all stored documents."""
        response = session.delete(f"{BASE_URL}/rag-knowledge-bases", json={})  # Use DELETE method
        print(response)

    def get_all(self):
        """Returns all stored documents as dictionaries."""
        print("Fetching all the relevant data..\n")
        # print("\n9) GET /rag-knowledge-bases")
        response = session.get(f"{BASE_URL}/rag-knowledge-bases")
        # print("Status:", response.status_code)
        try:
            print("Response:", response)
            print("================================")
            print(response.json())
            print("================================")
            return [i for i in response.json()]
            # return response.json().data
        except:
            print("Non-JSON response:", response[data])
            print(response)

    def addImage(self, data, datatype, embeddings=[0.1,0.2], source="unknown", time_published="unknown"):
        self.add_entry(imageToText(datatype, data), embeddings, datatype, source, time_published)

    def addText(self, data, datatype="text/plain", embeddings=[0.1,0.2], source="unknown", time_published="unknown"):
        self.add_entry(data, datatype, embeddings, source, time_published)

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


################ retrieve filetype from a file ####################
def getFileType(path):
    """returns the file's MIME type, e.g. image/jpeg"""
    return mimetypes.guess_type(path)[0]


################ take a file, return filetype + encoded data ####################
def loadLocalFile(path):
    """Load a file from the given filepath and return its type and 64-bit encoded content."""
    path = nameToPath(path)
    if not os.path.exists(path): raise FileNotFoundError(f"The file {path} does not exist.")
    with open(path, "rb") as f: 
        fileData = f.read()
    return getFileType(path), base64.standard_b64encode(fileData).decode("utf-8")



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


def allConnectedReasoning():
    stored_data = db.get_all()
    if stored_data != [] and stored_data is not None:
        query = "<DataSeparator>".join([item.data for item in db.get_all()])
    else:
        query = ""
    return query


###################### Recursive Retrieval Module ######################
class RecursiveRetrievalModule:
    def __init__(self, llm):
        self.llm = LLM(system="you are very good at asking potential validity and skeptical questions.")

    async def iterative_retrieve(self: str) -> List[Dict]:  #max_steps
        queries = db.get_all() # str[]
        if queries != []:
            for ind in range(len(queries)):
                query = queries[ind]
                # docs = await self.db.similarity_search(query, top_k=100) # same as retr

                # Generate sub-questions (mocked)
                sub_questions = await self.llm.generate(f"Generate sub-questions for: {query}. Strictly write in line \n newline etc.")
                if not sub_questions:
                    break
                
                
                # query = " ".join(sub_questions)
                for line in sub_questions.splitlines():
                    db.addText(line)



###################### Recursive Reasoning Module ######################
class GenerateInsights:
    async def process_documents(self) -> Dict:
        retrieved_docs = allConnectedReasoning()
        llm = LLM(system="You are an advanced reasoning engine that critically analyses retrieved documents. Identify key insights, detect factual inconsistencies, and explain any discrepancies in depth. Ensure logical coherence in your findings.")

        insights = await llm.generate(
            f"Synthesize insights from the provided data, identify any factual inconsistencies, and explain in detail why this query might be flawed: {retrieved_docs}"
        )
        return {"insights": insights}


###################### Recursive Generation Module ######################
class RecursiveGenerationModule:
    async def generate_final_answer(self, overall_insights, initial_query: str) -> str:
        reasoning_output = allConnectedReasoning()
        llm = LLM(system="You are a precise evaluator of information validity. Assess insights critically, determine the reliability of provided data, and quantify certainty in a structured manner.")
        prompt = f"""Evaluate the reliability of the user-provided data based on the following insights: {overall_insights['insights']}. 
        - Identify whether the insights suggest factual accuracy or inconsistency.  
        - Provide a clear, structured assessment.  
        - Assign a certainty percentage (0-100%) based on the reasoning.  
        
        Final evaluation for query '{initial_query}':"""
        return await llm.generate(prompt)



###################### Final Report Generation Pipeline ######################
async def run_recursive_pipeline(initial_query):
    """Main Pipeline"""
    # stored_data = db.get_all()
    # if stored_data != [] and stored_data is not None:
    #     query = "<DataSeparator>".join([item.data for item in db.get_all()])
    # else:
    #     query = ""
    # print(query)
    # initial_query
    
    llm = LLM("analyse this request thoroughly")

    retrieval_module = RecursiveRetrievalModule(llm)
    generate_insights = GenerateInsights()
    generation_module = RecursiveGenerationModule()
    
    print("\n[STEP 1] Retrieving Documents...")
    retrieved_docs = await retrieval_module.iterative_retrieve()
    print("Retrieved Docs:", retrieved_docs)

    print("\n[STEP 2] Processing Documents...")
    insights = await generate_insights.process_documents()
    print("Reasoning Output:", insights)

    print("\n[STEP 3] Generating Final Answer...")
    final_answer = await generation_module.generate_final_answer(insights, initial_query)
    print("Final Answer:", final_answer)








def send_prompt(query, links, files):
    client = anthropicClientSetup()
    db = DBStore()

    query = query
    links = links
    files = files

    # query = "Donald Trump is the new president of Ukraine!! Moon is fake."
    # links = ["https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg", "https://www.facebook.com/TheProjectTV/posts/rapper-50-cent-has-posted-a-photoshopped-album-cover-replacing-his-head-with-don/1045944933561837/"]
    # files = ["parsing/media/wasted.jpeg", "parsing/media/test1.png", "parsing/media/test.pdf"]


    # def add_entry(self, data, datatype, embeddings, source, time_published):
    
    # # add the query
    # db.add_entry(data=query, datatype="text/plain", source="a", time_published="hello") # HACK technically /plain is not a valid MIME type, but text is
    # print(db.get_all())
    
    # db.clear_all() # clear previous knowledge, remove if you're adding new prompt whatever
    for line in query.splitlines():
        db.addText(line)
    for file in files[:1]:
        dtype, data = loadLocalFile(nameToPath(file))
        if dtype.split("/")[0] == "image":
            db.addImage(data, dtype)
            
            
    initial_query = allConnectedReasoning()
    # db.get_all()
    # print([i.data for i in db.get_all()])
    # db.clear_all()
    # message = query

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
    asyncio.run(run_recursive_pipeline(initial_query))
    
    return allConnectedReasoning()
    # print("========================================\n")
    # print(allConnectedReasoning())
    
    # Run the test
    # print(moderate_message(message, misinformationCategories)) 








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
# # response = session.post(f"{BASE_URL}/rag-add", json=rag_data)
# # print("Add Response:", response.json())

# # # Send a POST request to /rag-get
# # response = requests.post(f"{BASE_URL}/rag-get", json={})  # No payload needed
# # print("Get Response:", response.json())

# # # Send a POST request to /rag-clear
# # response = requests.post(f"{BASE_URL}/rag-clear", json={})  # No payload needed
# # print("Clear Response:", response.json())











