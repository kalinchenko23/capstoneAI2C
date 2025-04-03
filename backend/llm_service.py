import os
import json
from openai import AzureOpenAI 

LLM_ENDPOINT = "https://noland-capstone-ai.openai.azure.com/"
LLM_DEPLOYMENT = "gpt-4o-mini"
API_VERSION = "2024-05-01-preview"

def get_review_summary(llm_key,reviews): 
    """Initialize the OpenAI client, provide system message, pass json reviews to OpenAI Model"""

    reviews_list=[]    
    # Iterate over the reviews for each place
    for review in reviews:
        review_data = {
            "review_text": review.get("text", {}).get("text", "")
        }
        reviews_list.append(review_data)
    
    # Initialize the Azure OpenAI client...
    client = AzureOpenAI(
            azure_endpoint = LLM_ENDPOINT, 
            api_key=llm_key,  
            api_version= API_VERSION
            )

    # Create a system message
    system_message = """You are a local travel advisor that summarizes customer reviews. 
    Summarize the review_text field in four sentences. The review should be in one paragraph not in bullet format.
    """
    messages_array = [{"role": "system", "content": system_message}]

    messages_array.append({"role": "user", "content": json.dumps(reviews_list, indent=2)})
    response = client.chat.completions.create(
        model=LLM_DEPLOYMENT,
        temperature=0.0,
        max_tokens=1200,
        messages=messages_array
    )

    generated_text = response.choices[0].message.content

    # Add generated text to message array
    messages_array.append({"role": "assistant", "content": generated_text})
    return generated_text




