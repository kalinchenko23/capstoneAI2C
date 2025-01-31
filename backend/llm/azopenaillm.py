import os
from dotenv import load_dotenv
import json
from openai import AzureOpenAI

def main(): 
        
    try: 
        """Load Json from a seperate file"""
        json_file_path = os.path.join(os.path.dirname(__file__), "reviews.json")
        
        with open(json_file_path, "r", encoding="utf-8") as file:
            json_response = json.load(file)

        """Extracts reviews from Google Maps API response."""
        reviews_list = []

        # Iterate over each place in the response
        for place in json_response.get("places", []):
            place_name = place.get("displayName", {}).get("text", "Unknown Place")
            place_address = place.get("formattedAddress", {})
            
            # Iterate over the reviews for each place
            for review in place.get("reviews", []):
                review_data = {
                    "place_name": place_name,
                    "place_address": place_address,
                    # "author": review.get("authorAttribution", {}).get("displayName", "Unknown Author"),
                    "rating": review.get("rating", None),
                    "review_text": review.get("text", {}).get("text", ""),
                    "publish_time": review.get("publishTime", ""),
                    # "relative_time": review.get("relativePublishTimeDescription", ""),
                    # "review_link": review.get("googleMapsUri", "")
                }
                reviews_list.append(review_data)

        """Initialize the OpenAI client, provide system message, pass json reviews to OpenAI Model"""
        # Get configuration settings 
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        
        # Initialize the Azure OpenAI client...
        client = AzureOpenAI(
                azure_endpoint = azure_oai_endpoint, 
                api_key=azure_oai_key,  
                api_version="2024-08-01-preview"
                )

        # Create a system message
        system_message = """You are a local travel advisor that summarizes customer reviews. 
        The reviews will be provided in a python dictionary format and contains the follow keys: place_name, place_address, rating, review_text, and publish_time.
        If the dictionaries have the same value in the place_address field aggregate the dictionaries together.
        Summarize the review_text field in four sentences for each dictionary with the same place_address. The review should be in one paragraph not in bullet format.
        Create an average rating by taking the average of the rating field and total number of ratings.
        Create a date range by providing the earliest publish_time and the latest publish_time and provide the range as well as the number of months between the earliest and latest publish_time.
        The output should include the place_name, place_address, a summarization of the review_text, average rating compared to the number of total reviews, 
        and a date range from the earliest to latest publish_time of the reviews.
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

        # Print the response
        print("Response: " + generated_text + "\n")
            

    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()
