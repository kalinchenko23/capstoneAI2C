import json
from openai import OpenAI
from typing import List, Dict

LLM_DEPLOYMENT = "gpt-4.1-mini-2025-04-14"

def get_review_summary(client: OpenAI, reviews: List[Dict]) -> str:
    """
    Summarizes customer reviews using an OpenAI LLM.
    
    Args:
        llm_key (str): API key for OpenAI.
        reviews (List[Dict]): List of review dictionaries.

    Returns:
        str: A summary paragraph of all reviews.
    """
    if not reviews:
        return "No reviews available for summarization."

    review_texts = [{"review_text": r.get("text", {}).get("text", "")} for r in reviews if r.get("text")]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a local travel advisor that summarizes customer reviews. "
                "Summarize the 'review_text' fields in four sentences. "
                "The summary should be a single paragraph, not in bullet format."
            )
        },
        {
            "role": "user",
            "content": json.dumps(review_texts, indent=2)
        }
    ]

    try:
        response = client.chat.completions.create(
            model=LLM_DEPLOYMENT,
            temperature=0.0,
            max_tokens=400,
            messages=messages
        )
        return response.choices[0].message.content.strip() if response.choices else "No summary generated."
    
    except Exception as e:
        return f"Failed to generate review summary: {str(e)}"
