from openai import AsyncOpenAI, RateLimitError, AuthenticationError
from httpx import HTTPStatusError
import asyncio

VLM_MODEL = "gpt-4.1-mini-2025-04-14"
MAX_CONCURRENT_REQUESTS = 25


async def get_safe_prompt(keywords: str, vlm_key: str) -> str:
    """Generate a safe user prompt based on keywords using OpenAI."""

    if not keywords.strip():
        return "Describe the objects and setting in the image in a neutral manner."

    client = AsyncOpenAI(api_key=vlm_key)

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that reformulates user-provided keywords into safe and neutral image analysis prompts."
            )
        },
        {
            "role": "user",
            "content": (
                f"Given the following information: {keywords}, create a professional and neutral prompt that can be used "
                "to describe an image focusing on these elements. Do not include any potentially sensitive content."
            )
        }
    ]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=100,
            temperature=0.3
        )
        # Safe access
        return response.choices[0].message.content if response.choices else "No response content"

    except HTTPStatusError as e:
        if e.response.status_code == 401:
            raise Exception(e.response.text)
        else:
            print(f"[VLM] HTTP error while generating safe prompt: {e.response.status_code}")
            return "Describe the objects and setting in the image in a neutral manner."

    except Exception as e:
        print(f"[VLM] General error generating safe prompt: {e}")
        return "Describe the objects and setting in the image in a neutral manner."


async def analyze_image(encoded_image: str, safe_prompt: str, vlm_key: str, retry_count=0, max_retries=8) -> str:
    """Analyze an image using GPT-4o Vision capabilities via OpenAI with smart error handling and retries."""

    client = AsyncOpenAI(api_key=vlm_key)

    content = [
        {"type": "text", "text": safe_prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
    ]

    try:
        response = await client.chat.completions.create(
            model=VLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI vision model that analyzes images and provides factual "
                        "descriptions of primary objects, settings, and scenes in four sentences or less, "
                        "without speculation or interpretation."
                    )
                },
                {"role": "user", "content": content}
            ],
            max_tokens=150,
            temperature=0.3
        )

        return response.choices[0].message.content if response.choices else "No response content"

    except RateLimitError as e:
        # Handle 429 Rate Limit
        if retry_count < max_retries:
            wait_time = 2 ** retry_count
            print(f"[VLM] Rate limit error. Retrying after {wait_time} seconds... (Retry {retry_count + 1}/{max_retries})")
            await asyncio.sleep(wait_time)
            return await analyze_image(encoded_image, safe_prompt, vlm_key, retry_count + 1, max_retries)
        else:
            return "Rate limit exceeded after multiple retries."

    except AuthenticationError as e:
        # Handle 401 Unauthorized
        print("[VLM] Authentication error: Invalid VLM API key.")
        raise Exception("Authentication failed: check your API key.")

    except HTTPStatusError as e:
        if e.response.status_code == 400:
            # Handle potential moderation errors or bad request
            response_text = e.response.text.lower()
            if "jailbreak" in response_text or "content filter" in response_text:
                return "Content blocked due to moderation policy"
            else:
                return "Bad request error when analyzing image."
        else:
            print(f"[VLM] HTTP error: {e.response.status_code}")
            return "An HTTP error occurred while analyzing the image."

    except Exception as e:
        # General catch-all
        if retry_count < max_retries:
            wait_time = 2 ** retry_count
            print(f"[VLM] General error '{str(e)}'. Retrying after {wait_time} seconds... (Retry {retry_count + 1}/{max_retries})")
            await asyncio.sleep(wait_time)
            return await analyze_image(encoded_image, safe_prompt, vlm_key, retry_count + 1, max_retries)
        else:
            return f"[VLM] Failed after multiple retries: {str(e)}"

async def generate_summary(image_descriptions: list, vlm_key: str) -> str:
    """Generate a summary paragraph based on all image descriptions, with smart error handling."""
    
    client = AsyncOpenAI(api_key=vlm_key)

    if not image_descriptions:
        return "No images were analyzed."

    descriptions = [description["vlm_insight"] for description in image_descriptions]
    all_descriptions = "\n\n".join(descriptions)
    num_descriptions = len(descriptions)

    summary_prompt = f"""Based on the following {num_descriptions} image descriptions, 
create a concise one-paragraph summary that captures the key themes, 
settings, and objects that appear across multiple images:

{all_descriptions}

Summarize these descriptions in one coherent paragraph:"""

    try:
        response = await client.chat.completions.create(
            model=VLM_MODEL,
            messages=[
                {"role": "system", "content": "You are an AI assistant that creates concise, informative summaries."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=250,
            temperature=0.3
        )

        return response.choices[0].message.content if response.choices else "Failed to generate summary."

    except RateLimitError as e:
        print("[VLM] Rate limit error while generating summary.")
        return "Rate limit error: please try again later."

    except AuthenticationError as e:
        print("[VLM] Authentication error while generating summary.")
        raise Exception("Authentication failed: check your API key.")

    except HTTPStatusError as e:
        if e.response.status_code == 400:
            return "Bad request error while generating summary."
        elif e.response.status_code == 401:
            raise Exception("Authentication failed: invalid VLM key.")
        else:
            print(f"[VLM] HTTP error: {e.response.status_code}")
            return f"HTTP error {e.response.status_code} while generating summary."

    except Exception as e:
        print(f"[VLM] General error generating summary: {str(e)}")
        return f"[VLM] Failed to generate summary: {str(e)}"
   
    
   