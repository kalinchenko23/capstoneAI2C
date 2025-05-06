import os
import aiohttp
import asyncio
import json
import requests
import openai
from fastapi import HTTPException

#Defining config information
VLM_ENDPOINT = "https://noland-capstone-ai.openai.azure.com/"
VLM_DEPLOYMENT = "gpt-4"
API_VERSION = "2024-05-01-preview"
MAX_CONCURRENT_REQUESTS = 25  
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


def get_safe_prompt(keywords,vlm_key):

    HEADERS = {
        "Content-Type": "application/json",
        "api-key": vlm_key,
        "User-Agent": "Image-Analysis-Tool/1.0"
    }
    """Synchronously generate a safe user prompt based on keywords using ChatGPT."""
    
    if not keywords.strip():  # Check for empty or whitespace-only string
        return "Describe the objects and setting in the image in a neutral manner."
        
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that reformulates user-provided keywords into safe and neutral image analysis prompts."},
            {"role": "user", "content": f"Given the following information: {keywords}, create a professional and neutral prompt that can be used to describe an image focusing on these elements. Do not include any potentially sensitive content."}
        ],
        "model": VLM_DEPLOYMENT,
        "max_tokens": 100,
        "temperature": 0.3
    }
    
    response = requests.post(
        f"{VLM_ENDPOINT}/openai/deployments/{VLM_DEPLOYMENT}/chat/completions?api-version={API_VERSION}",
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "No response content")
    elif response.status_code == 401:
        raise Exception(response.text)
    else:
        return "Describe the objects and setting in the image in a neutral manner."


async def analyze_image(encoded_image, safe_prompt, vlm_key, retry_count=0, max_retries=8):
    """Analyze a binary image using Azure OpenAI GPT-4 Vision."""
    
    HEADERS = {
        "Content-Type": "application/json",
        "api-key": vlm_key,
        "User-Agent": "Image-Analysis-Tool/1.0"
    }
    async with aiohttp.ClientSession() as session:
        payload = {
            "messages": [
                {"role": "system", "content": "You are an AI vision model that analyzes images and provides factual descriptions of primary objects, settings, and scenes in four sentences or less, without speculation or interpretation."},
                {"role": "user", "content": [
                    {"type": "text", "text": safe_prompt},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{encoded_image}"}
                ]}
            ],
            "model": VLM_DEPLOYMENT,
            "max_tokens": 150,
            "temperature": 0.3
        }
    
        async with session.post(
            f"{VLM_ENDPOINT}/openai/deployments/{VLM_DEPLOYMENT}/chat/completions?api-version={API_VERSION}",
            headers=HEADERS,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            if response.status == 200:
                data = await response.json()
                result = data.get("choices", [{}])[0].get("message", {}).get("content", "No response content")
                return result

            if response.status == 429:  # Rate limit error
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    await asyncio.sleep(wait_time)
                    return await analyze_image(encoded_image, session, safe_prompt, retry_count + 1, max_retries)
                else:
                    return "Rate limit exceeded after multiple retries"

            elif response.status == 400:
                response_text = await response.text()
                if "jailbreak" in response_text.lower() or "content filter" in response_text.lower():
                    return "Content blocked due to moderation policy"
            
            elif response.status == 401:
                raise HTTPException(status_code=401,detail="Your VLM key or endpoint is incorrect")

async def generate_summary(image_descriptions: list, vlm_key: str):
    """Generate a summary paragraph based on all image descriptions.

    Args:
        image_descriptions (list): _description_
        vlm_key (str): _description_

    Returns:
        _type_: _description_
    """  
    HEADERS = {
        "Content-Type": "application/json",
        "api-key": vlm_key,
        "User-Agent": "Image-Analysis-Tool/1.0"
    }

    if not image_descriptions:
        return "No images were analyzed."
    
    descriptions=[description["vlm_insight"] for description in image_descriptions]
    # Create a prompt to summarize the descriptions
    all_descriptions = "\n\n".join(descriptions) 
    num_descriptions = len(descriptions)
    
    summary_prompt = f"""Based on the following {num_descriptions} image descriptions, 
    create a concise one-paragraph summary that captures the key themes, 
    settings, and objects that appear across multiple images:

    {all_descriptions}
    
    Summarize these descriptions in one coherent paragraph:"""
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that creates concise, informative summaries."},
            {"role": "user", "content": summary_prompt}
        ],
        "model": VLM_DEPLOYMENT,
        "max_tokens": 250,
        "temperature": 0.3
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{VLM_ENDPOINT}/openai/deployments/{VLM_DEPLOYMENT}/chat/completions?api-version={API_VERSION}",
            headers=HEADERS,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "Failed to generate summary.")
            else:
                return f"{response.status} something went wrong"


