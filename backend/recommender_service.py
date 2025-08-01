import pandas as pd
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from logging_service import logger
import time
 
def score_to_label(score):
    """
   Helper function that converts similarity score from float to a more meaningfull
   str value.
    
    Args:
        score (float): 
    Returns:
        pandas.DataFrame
    """
    if score < 0.5:
        return 'low'
    elif score < 0.75:
        return 'medium'
    else:
        return 'high'

def rank_live_results(api_data, user_prompt, api_key, top_n=3):  
    """
    Ranks live API data based on semantic similarity to a user prompt.
    
    Args:
        api_data (list): The list of dictionary objects from your API call.
        user_prompt (str): The user's search query.
        top_n (int): The number of top results to return.
    
    Returns:
        pandas.DataFrame: A DataFrame of the top_n ranked locations.
    """
    client = OpenAI(api_key=api_key)

    if not api_data:
        logger.debug("API data is empty. Cannot perform ranking.")
        return False
    
    start_time = time.time()

    # Extract all individual text snippets for embedding
    all_snippets = []

    # This list will track which location each snippet belongs to
    snippet_location_map = []

    for i, location in enumerate(api_data):
        # Add individual reviews
        if 'reviews' in location and location['reviews'] and type(location['reviews'])==dict:
            for review in location['reviews']:
                if review.get('text'):
                    all_snippets.append(review['text'])
                    snippet_location_map.append(i)
        
        # Add individual VLM insights from photos
        if 'photos' in location and location['photos']:
            for photo in location['photos']:
                if photo.get('vlm_insight'):
                    all_snippets.append(photo['vlm_insight'])
                    snippet_location_map.append(i)
     
    if not all_snippets:
        logger.debug("No text snippets found in the API data to embed.")
        return False
    
    logger.debug(f"Generating embeddings for the prompt and {len(all_snippets)} text snippets...")
    texts_to_embed = [user_prompt] + all_snippets

    try:
        response = client.embeddings.create(input=texts_to_embed, model="text-embedding-3-small")
        all_embeddings = [item.embedding for item in response.data]
    except Exception as e:
        logger.debug(f"Error calling OpenAI API: {e}")
        return pd.DataFrame()

    prompt_embedding = np.array(all_embeddings[0])
    snippet_embeddings = np.array(all_embeddings[1:])
    
    # Calculate similarity for every snippet using cosine_similarity
    similarities = [cosine_similarity([prompt_embedding], [emb])[0][0] for emb in snippet_embeddings]

    # Find the best match for each location
    # Create a DataFrame to easily group results by location
    results_df = pd.DataFrame({
        'location_index': snippet_location_map,
        'influential_snippet': all_snippets,
        'similarity_score': similarities
    })
    
    # Group by the original location index and find the maximum similarity score
    # This is the "Best Match" strategy
    best_match_indices = results_df.groupby('location_index')['similarity_score'].idxmax()
    best_matches_df = results_df.loc[best_match_indices]

    
    # Rank locations based on their best match score
    # Convert the original API data to a DataFrame to merge results
    locations_df = pd.DataFrame(api_data)
    
    # Add the max similarity score to each location
    final_df = locations_df.merge(
            best_matches_df,
            left_index=True,
            right_on='location_index'
        )    
    
    # Set the DataFrame's index to be the original location index
    final_df = final_df.set_index('location_index')

    # Sort the locations by this new score
    sorted_locations = final_df.sort_values(by='similarity_score', ascending=False)
    if (sorted_locations["similarity_score"] >= 0.6).any():

        top_locations=sorted_locations[sorted_locations["similarity_score"] >= 0.6].copy()
    else:
        top_locations = sorted_locations.head(top_n).copy()

    top_locations.loc[:, 'similarity_label'] = top_locations['similarity_score'].apply(score_to_label)

    end_time = time.time()
    logger.debug(f"Granular ranking completed in {end_time - start_time:.2f} seconds.")
    logger.debug(top_locations[['name', 'influential_snippet', 'similarity_score']])

    return list(zip(top_locations.index, top_locations['similarity_label']))




