import os
import aiohttp
import asyncio
import json
import requests

# Load the JSON secrets config
with open("secrets.json") as config_file:
    config = json.load(config_file)

AZURE_OPENAI_API_KEY_VLM = config["AZURE_OPENAI_API_KEY_VLM"]
AZURE_OPENAI_ENDPOINT = config["AZURE_OPENAI_ENDPOINT"]
DEPLOYMENT_NAME = config["DEPLOYMENT_NAME"]
API_VERSION = config["API_VERSION"]


HEADERS = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_API_KEY_VLM,
    "User-Agent": "Image-Analysis-Tool/1.0"
}



MAX_CONCURRENT_REQUESTS = 25  
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


def get_safe_prompt(keywords):
    """Synchronously generate a safe user prompt based on keywords using ChatGPT."""
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that reformulates user-provided keywords into safe and neutral image analysis prompts."},
            {"role": "user", "content": f"Given the following keywords: {', '.join(keywords)}, create a professional and neutral prompt that can be used to describe an image focusing on these elements. Do not include any potentially sensitive content."}
        ],
        "model": DEPLOYMENT_NAME,
        "max_tokens": 100,
        "temperature": 0.3
    }
    try:
        response = requests.post(
            f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}",
            headers=HEADERS,
            json=payload,
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "No response content")
        else:
            return "Describe the objects and setting in the image in a neutral manner."
    except Exception as e:
        return "Describe the objects and setting in the image in a neutral manner."


async def analyze_image(encoded_image, session, safe_prompt, retry_count=0, max_retries=8):
    """Analyze a binary image using Azure OpenAI GPT-4 Vision."""
    async with semaphore:
        try:
            payload = {
                "messages": [
                    {"role": "system", "content": "You are an AI vision model that analyzes images and provides factual descriptions of primary objects, settings, and scenes in four sentences or less, without speculation or interpretation."},
                    {"role": "user", "content": [
                        {"type": "text", "text": safe_prompt},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{encoded_image}"}
                    ]}
                ],
                "model": DEPLOYMENT_NAME,
                "max_tokens": 150,
                "temperature": 0.3
            }

            async with session.post(
                f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}",
                headers=HEADERS,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:

                if response.status == 200:
                    data = await response.json()
                    result = data.get("choices", [{}])[0].get("message", {}).get("content", "No response content")
                    return result

                elif response.status == 429:  # Rate limit error
                
                    if retry_count < max_retries:
                        wait_time = 2 ** retry_count
                        await asyncio.sleep(wait_time)
                        return await analyze_binary_image(encoded_image, session, safe_prompt, retry_count + 1, max_retries)
                    else:
                        return "Rate limit exceeded after multiple retries"
                
                elif response.status >= 500:  # Server errors
                    
                    if retry_count < max_retries:
                        wait_time = 1 * (retry_count + 1)  # Linear backoff for server errors
                        await asyncio.sleep(wait_time)
                        return await analyze_binary_image(encoded_image, session, safe_prompt, retry_count + 1, max_retries)
                    else:
                        return "Server error after multiple retries"

                elif response.status == 400:
                    response_text = await response.text()
                    if "jailbreak" in response_text.lower() or "content filter" in response_text.lower():
                        return "Content blocked due to moderation policy"

                return f"Error {response.status}: {await response.text()}"

        except Exception as e:
            if retry_count < max_retries:
                wait_time = 2 * (retry_count + 1)
                await asyncio.sleep(wait_time)
                return await analyze_image(encoded_image, session, safe_prompt, retry_count + 1, max_retries)
            return f"Exception occurred: {str(e)}"



async def analyze_images_api(encoded_image,safe_prompt):
    """API entry point to analyze binary images from Google Maps."""
    
    #Processing binary images
    async with aiohttp.ClientSession() as session:
        result=await analyze_image(encoded_image, session, safe_prompt)
        return result

