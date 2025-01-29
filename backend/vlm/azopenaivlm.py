import os  
import base64
from dotenv import load_dotenv
from openai import AzureOpenAI  

load_dotenv()

endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME") 
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")  

# Initialize Azure OpenAI Service client with key-based authentication    
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-05-01-preview",
)
    
    
IMAGE_PATH = "Pamelas_Diner_Test.png"
encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

#Prepare the chat prompt 
chat_prompt = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": "You are an AI assistant that helps people find information."
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "\n"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            },
            {
                "type": "text",
                "text": "Describe what is in the attached image"
            }
        ]
    }
    # },    
#     {
#         "role": "assistant",
#         "content": [
#             {
#                 "type": "text",
#                 "text": "The image shows the interior of a casual dining restaurant. The restaurant has a lively and eclectic decor, with walls covered in various colorful artworks, posters, and decorations. There are several groups of people seated at tables, enjoying their meals. The tables are rectangular, and most have items like condiments and menus on them. The ceiling has recessed lighting, and there are also some hanging red pendant lights providing additional illumination. The floor has a pattern of multicolored tiles. Overall, the atmosphere appears to be friendly and relaxed."
#             }
#         ]
#     }
] 
    
# Include speech result if speech is enabled  
messages = chat_prompt  
    
# Generate the completion  
completion = client.chat.completions.create(  
    model=deployment,
    messages=messages,
    max_tokens=800,  
    temperature=0.7,  
    top_p=0.95,  
    frequency_penalty=0,  
    presence_penalty=0,
    stop=None,  
    stream=False
)

print(completion.to_json())  






    
