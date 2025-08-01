from openai import AsyncOpenAI, RateLimitError, AuthenticationError
from httpx import HTTPStatusError
from logging_service import logger
import asyncio
from typing import List, Dict

# Constants
VLM_MODEL = "gpt-4.1-mini-2025-04-14"
DEFAULT_PROMPT = "Describe the objects and setting in the image in a neutral manner."
MAX_CONCURRENT_REQUESTS = 25
MAX_RETRIES = 8


# --- Utility Functions ---
def exponential_backoff_delay(retry_count: int) -> int:
    return 2 ** retry_count


def handle_missing_keywords(keywords: str) -> str:
    return DEFAULT_PROMPT if not keywords.strip() else ""


def safe_get_content(response) -> str:
    return response.choices[0].message.content if response.choices else "No response content"


# --- Core Async Functions ---
async def get_safe_prompt(client: AsyncOpenAI, keywords: str) -> str:
    """Generate a safe, neutral image description prompt from user keywords."""
    if not keywords.strip():
        return DEFAULT_PROMPT

    messages = [
        {"role": "system", "content": "You are an AI assistant that reformulates user-provided keywords into safe and neutral prompt used by other LLMs for image analysis."},
        {"role": "user", "content": f"Given the following information: {keywords}, create a professional and neutral prompt for image analysis. Do not include any potentially sensitive content."}
    ]

    try:
        response = await client.chat.completions.create(
            model="gpt-4.1-mini-2025-04-14",
            messages=messages,
            max_tokens=100,
            temperature=0.3
        )
        return safe_get_content(response)

    except HTTPStatusError as e:
        if e.response.status_code == 401:
            raise Exception(e.response.text)
        logger.error(f"[VLM] HTTP error while generating safe prompt: {e.response.status_code}")
    except Exception as e:
        logger.error(f"[VLM] Error generating safe prompt: {e}")

    return DEFAULT_PROMPT


async def analyze_image(
    client: AsyncOpenAI,
    encoded_image: str,
    safe_prompt: str,
    retry_count: int = 0
) -> str:
    """Use OpenAI Vision to analyze an image and return a factual description."""

    messages = [
        {"role": "system", "content": "You are an AI vision model that analyzes images and provides factual descriptions of primary objects, settings, and scenes in four sentences or less, without speculation or interpretation."},
        {"role": "user", "content": [
            {"type": "text", "text": safe_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
        ]}
    ]

    try:
        response = await client.chat.completions.create(
            model=VLM_MODEL,
            messages=messages,
            max_tokens=150,
            temperature=0.3
        )
        return safe_get_content(response)

    except RateLimitError:
        if retry_count < MAX_RETRIES:
            wait_time = exponential_backoff_delay(retry_count)
            logger.error(f"[VLM] Rate limit. Retrying in {wait_time}s... (Attempt {retry_count+1}/{MAX_RETRIES})")
            await asyncio.sleep(wait_time)
            return await analyze_image(client, encoded_image, safe_prompt,retry_count + 1)
        logger.error("Rate limit exceeded after multiple retries.")
        return "Rate limit exceeded after multiple retries."

    except AuthenticationError:
        logger.error("[VLM] Invalid API key.")
        raise Exception("Authentication failed: check your API key.")

    except HTTPStatusError as e:
        if e.response.status_code == 400 and any(k in e.response.text.lower() for k in ("jailbreak", "content filter")):
            return "Content blocked due to moderation policy"
        logger.error(f"[VLM] HTTP error: {e.response.status_code}")
        return "HTTP error while analyzing image."

    except Exception as e:
        if retry_count < MAX_RETRIES:
            wait_time = exponential_backoff_delay(retry_count)
            logger.error(f"[VLM] Error '{e}'. Retrying in {wait_time}s... (Attempt {retry_count+1}/{MAX_RETRIES})")
            await asyncio.sleep(wait_time)
            return await analyze_image(client, encoded_image, safe_prompt, retry_count + 1)
        logger.error(f"Failed after retries: {e}")
        return f"Failed after retries: {e}"


async def generate_summary(client: AsyncOpenAI, image_descriptions: List[Dict[str, str]]) -> str:
    """Create a concise summary paragraph from multiple image descriptions."""
    if not image_descriptions:
        logger.debug("No images were analyzed.")
        return "No images were analyzed."

    descriptions = [desc["vlm_insight"] for desc in image_descriptions]
    combined_text = "\n\n".join(descriptions)
    count = len(descriptions)

    summary_prompt = (
        f"Based on the following {count} image descriptions, create a concise one-paragraph summary "
        f"that captures key themes, settings, and objects across the images:\n\n{combined_text}\n\n"
        "Summarize these descriptions in one coherent paragraph:"
    )

    messages = [
        {"role": "system", "content": "You are an AI assistant that creates concise, informative summaries."},
        {"role": "user", "content": summary_prompt}
    ]

    try:
        response = await client.chat.completions.create(
            model=VLM_MODEL,
            messages=messages,
            max_tokens=250,
            temperature=0.3
        )
        return safe_get_content(response)

    except RateLimitError:
        logger.error("[VLM] Rate limit while generating summary.")
        return "Rate limit error: try again later."

    except AuthenticationError:
        logger.error("[VLM] Authentication error during summary.")
        raise Exception("Authentication failed: check your API key.")

    except HTTPStatusError as e:
        if e.response.status_code in (400, 401):
            raise Exception("Authentication or bad request error during summary.")
        logger.error(f"[VLM] HTTP error: {e.response.status_code}")
        return f"HTTP error {e.response.status_code} during summary."

    except Exception as e:
        logger.error(f"[VLM] Summary generation error: {e}")
        return f"Summary generation failed: {e}"
