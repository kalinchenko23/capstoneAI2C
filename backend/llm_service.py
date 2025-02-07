import os
import json
from openai import AzureOpenAI

def get_review_summary(reviews): 
        
    try: 
        # Iterate over each place in the response
        
            
        reviews_list=[]    
        # Iterate over the reviews for each place
        for review in reviews:
            review_data = {
                "review_text": review.get("text", {}).get("text", "")
            }
            reviews_list.append(review_data)

        """Initialize the OpenAI client, provide system message, pass json reviews to OpenAI Model"""
        # Get configuration settings 
        
        azure_oai_endpoint = "..."
        azure_oai_key = "..."
        azure_oai_deployment = "..."
        
        # Initialize the Azure OpenAI client...
        client = AzureOpenAI(
                azure_endpoint = azure_oai_endpoint, 
                api_key=azure_oai_key,  
                api_version="2024-08-01-preview"
                )

        # Create a system message
        system_message = """You are a local travel advisor that summarizes customer reviews. 
        Summarize the review_text field in four sentences. The review should be in one paragraph not in bullet format.
        """
        messages_array = [{"role": "system", "content": system_message}]

        messages_array.append({"role": "user", "content": json.dumps(reviews_list, indent=2)})
        response = client.chat.completions.create(
            model=azure_oai_deployment,
            temperature=0.0,
            max_tokens=1200,
            messages=messages_array
        )
        generated_text = response.choices[0].message.content

        # Add generated text to message array
        messages_array.append({"role": "assistant", "content": generated_text})

    except Exception as ex:
        print(ex)

    return generated_text


