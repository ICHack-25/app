import anthropic
import os
import mimetypes
import base64
import httpx
from dotenv import load_dotenv
import json

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
    return message.content

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

def getMisinformationCategories():
    """List of categories considered unreliable for content moderation"""
    with open(nameToPath("misinformationCategories.txt")) as f:
        return [line.strip() for line in f.readlines()]

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
    print(moderate_message(message, misinformationCategories)) 





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