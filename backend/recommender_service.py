import pandas as pd
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time

def rank_live_results_granularly(api_data, user_prompt, api_key, top_n=3):
    
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
        print("API data is empty. Cannot perform ranking.")
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
        print("No text snippets found in the API data to embed.")
        return False
    
    print(f"Generating embeddings for the prompt and {len(all_snippets)} text snippets...")
    texts_to_embed = [user_prompt] + all_snippets

    try:
        response = client.embeddings.create(input=texts_to_embed, model="text-embedding-3-small")
        all_embeddings = [item.embedding for item in response.data]
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return pd.DataFrame()

    prompt_embedding = np.array(all_embeddings[0])
    snippet_embeddings = np.array(all_embeddings[1:])
    
    # Calculate similarity for every snippet
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

    
    # --- Step 5: Rank locations based on their best match score ---
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
    top_locations = final_df.sort_values(by='similarity_score', ascending=False).head(top_n)
    
    end_time = time.time()
    print(f"Granular ranking completed in {end_time - start_time:.2f} seconds.")
    print(top_locations[['name', 'influential_snippet', 'similarity_score']])
    return list(top_locations.index)




# --- 3. EXAMPLE USAGE ---
# Simulate an API call with detailed data
# live_api_data = [
#   {
#     "name": {
#       "original_name": "Rock 'n' Joe Coffee (Penn Ave)",
#       "translated_name": "Rock 'n' Joe Coffee (Penn Ave)"
#     },
#     "type": "coffee_shop",
#     "website": "http://www.rocknjoe.com/",
#     "google_maps_url": "https://maps.google.com/?cid=7026232693633619918&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQABgEIAA",
#     "phone_number": "(412) 281-7111",
#     "address": "524 Penn Ave, Pittsburgh, PA 15222, USA",
#     "latitude": 40.442327,
#     "longitude": -80.00286799999999,
#     "reviews_summary": "This coffee shop offers both indoor and outdoor seating, with a cozy upstairs area perfect for relaxing or catching up with friends. Customers praise the delicious coffee, especially the lattes, which have even won awards for their quality and flavor. The staff is consistently described as friendly and accommodating, providing quick service and a welcoming atmosphere. Additionally, the shop offers a variety of food options, including vegetarian choices and tasty sandwiches, making it a favorite spot in downtown.",
#     "reviews": [
#       {
#         "author_name": {
#           "original_name": "Zen",
#           "translated_name": "Zen"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sCi9DQUlRQUNvZENodHljRjlvT2xCb2RVaE9hV1p5VmtocVFtRndTMkl4ZFZNNVdtYxAB!2m1!1s0x8834f1567976d459:0x61823168854497ce",
#         "text": "So cute!! Indoor and outdoor seating available.\nCoffee was delicious!",
#         "original_text": "So cute!! Indoor and outdoor seating available.\nCoffee was delicious!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/116752467943723065716/reviews",
#         "publish_date": "a week ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Suman Hazra",
#           "translated_name": "Summan Hazra"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VJQ0FnSURqcXRUZGZnEAE!2m1!1s0x8834f1567976d459:0x61823168854497ce",
#         "text": "Its bang in the middle of downtown near the cultural district surrounded by imposing skyscrapers. The coffee is good and my request to sweeten mine with honey was very graciously accepted. They seem to have lots of variety but i went for a generic iced latte. There is seating on the second floor which is accessible by a staircase and also couple of tables outside as well which is nice on a sunny day. The only reason i am not giving it a perfect score is because no details stood out for me. It’s a generic good coffee shop!",
#         "original_text": "Its bang in the middle of downtown near the cultural district surrounded by imposing skyscrapers. The coffee is good and my request to sweeten mine with honey was very graciously accepted. They seem to have lots of variety but i went for a generic iced latte. There is seating on the second floor which is accessible by a staircase and also couple of tables outside as well which is nice on a sunny day. The only reason i am not giving it a perfect score is because no details stood out for me. It’s a generic good coffee shop!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/104162699927935071901/reviews",
#         "publish_date": "a year ago",
#         "rating": 4
#       },
#       {
#         "author_name": {
#           "original_name": "Chase E",
#           "translated_name": "Chase E"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VJQ0FnSURCOGZfNE9BEAE!2m1!1s0x8834f1567976d459:0x61823168854497ce",
#         "text": "This is pretty easily the best place to get coffee in downtown. The caramel latte I had was amazing and the indoor has lots of seating and a very cool vibe. Staff were also EXTREMELY friendly! I will be back! Don't waste your time at any other coffee shop in the area. This is the one to go to.",
#         "original_text": "This is pretty easily the best place to get coffee in downtown. The caramel latte I had was amazing and the indoor has lots of seating and a very cool vibe. Staff were also EXTREMELY friendly! I will be back! Don't waste your time at any other coffee shop in the area. This is the one to go to.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/104798501964289468910/reviews",
#         "publish_date": "2 years ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Sara",
#           "translated_name": "Sara"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VJQ0FnSUNwMDktYUhREAE!2m1!1s0x8834f1567976d459:0x61823168854497ce",
#         "text": "I went inside of this coffee shop for the first time this morning, and what I really loved about this place was that it had plenty of vegetarian options, the staff was very nice and friendly, and I got served really quickly, and the upstairs portion is the perfect place to catch up with a few friends, and to charge your phone.\n\nI will definitely be back again!",
#         "original_text": "I went inside of this coffee shop for the first time this morning, and what I really loved about this place was that it had plenty of vegetarian options, the staff was very nice and friendly, and I got served really quickly, and the upstairs portion is the perfect place to catch up with a few friends, and to charge your phone.\n\nI will definitely be back again!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/101919633657349849840/reviews",
#         "publish_date": "a year ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Sara M",
#           "translated_name": "Sara M"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VJQ0FnSUR6N2NEVkNBEAE!2m1!1s0x8834f1567976d459:0x61823168854497ce",
#         "text": "Best coffee downtown! Their lattes are so good! They’ve won some awards for them for best in Pittsburgh, too. The brand of syrups they use is a good quality, I think. The flavors are always really prominent. Photo is old, but relevant, sometimes they do latte art, it depends on who is working. They have good food, too. I like their ham & swiss baguette sandwich. Their pastries are also delicious. The upstairs is really nice to sit and relax in. Overall, as I said, it’s my favorite coffee downtown. I really hope they never close!",
#         "original_text": "Best coffee downtown! Their lattes are so good! They’ve won some awards for them for best in Pittsburgh, too. The brand of syrups they use is a good quality, I think. The flavors are always really prominent. Photo is old, but relevant, sometimes they do latte art, it depends on who is working. They have good food, too. I like their ham & swiss baguette sandwich. Their pastries are also delicious. The upstairs is really nice to sit and relax in. Overall, as I said, it’s my favorite coffee downtown. I really hope they never close!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/117359054414317512591/reviews",
#         "publish_date": "a year ago",
#         "rating": 5
#       }
#     ],
#     "rating": "average: 4.8 out of 5 reviews",
#     "reviews_span": "latest date: 2025-07-02, most recent date: 2023-01-22, date difference: 892 days",
#     "url_to_all_photos": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDB8f_4RA!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce",
#     "photos": [
#       {
#         "vlm_insight": "The image shows a seating area inside a building with large windows overlooking the main street, providing good natural visibility of the outside. There are no visible security cameras mounted on the ceiling, walls, or near the windows in this area, which suggests a lack of electronic surveillance coverage. The windows themselves offer clear sightlines to the street, which can aid in passive monitoring by occupants. Overall, the security measures appear to rely primarily on window visibility rather than camera surveillance.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDB8f_4RA!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       },
#       {
#         "vlm_insight": "The image shows two cups of frothy beverages on a wooden table inside a café or restaurant. There are no visible security cameras or windows overlooking a main street in this image. The setting appears to be indoors with a focus on the drinks and table, so no assessment of visibility or security measures related to street surveillance can be made from this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDVu_jfZg!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       },
#       {
#         "vlm_insight": "In the image, there is one visible security camera mounted on the left side of the building facade, positioned above the outdoor seating area. The camera is angled downward, likely covering the entrance and the immediate sidewalk area in front of the establishment. The large windows above and beside the entrance provide good visibility of the main street and outdoor seating area, allowing for natural surveillance from inside. Overall, the combination of the camera placement and window coverage offers a reasonable level of visibility and security for monitoring the street and entrance.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDrtr-i3gE!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       },
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on the exterior of the building or around the entrance of \"Rock n Joe.\" The windows above and around the entrance provide clear visibility of the main street, allowing for natural surveillance from inside the building. The large glass windows on the ground floor also offer good visibility of the outdoor seating area and the street. Overall, while window placement supports visibility, the absence of visible security cameras suggests limited electronic surveillance coverage.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIABIhDqZ5JtGjZ_mLi_ko_UZe1K!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       },
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on the building or street-facing areas that would provide surveillance coverage of the main street or sidewalk. The windows along the building's facade overlook the sidewalk and street, offering potential natural visibility for occupants inside to observe street activity. However, the windows appear to be standard glass without any visible security features such as bars or reinforced glass. Overall, the security measures in terms of camera placement and window oversight appear minimal or absent based on this view.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIABIhANUrz9WHmTFsWf7k6bT_k_!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       },
#       {
#         "vlm_insight": "The image shows the interior of a coffee shop with a focus on the counter area. There are no visible security cameras mounted inside or outside the shop that overlook the main street. The windows or openings facing the street are not visible in this image, so their presence and coverage cannot be assessed. Overall, based on this image alone, there is insufficient evidence of security cameras or window coverage for street visibility and security assessment.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDBl4zNlgE!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       },
#       {
#         "vlm_insight": "The image shows an indoor setting with a wooden table, iced coffee, and a pastry. In the background, there are large windows overlooking a street, providing natural visibility to the outside area. No security cameras are visible in the image, so it is unclear if there is any camera coverage of the main street from this vantage point. The windows do offer some level of passive surveillance, allowing occupants to see outside, but the overall security measures cannot be fully assessed based on this image alone.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDB8f_4JA!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a coffee cup on a metal mesh table with a person holding a yellow phone in the background. There are no visible security cameras or windows overlooking a main street in this image. The setting appears to be an outdoor or semi-outdoor cafe area, but no elements related to security measures or street visibility can be assessed from this photo.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDRkt6YAg!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a table with a coffee cup, a small plush dragon, and a candle. The background includes metal railings and windows, but there are no visible security cameras in this view. The windows appear to overlook an outdoor area, possibly a street, but the angle and coverage of visibility from these windows cannot be fully assessed from this image alone. Overall, there is insufficient information in this image to evaluate security camera placement or comprehensive window coverage for street visibility.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICvnc_eOw!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       },
#       {
#         "vlm_insight": "The image shows an indoor seating area with wooden tables and chairs, but there are no visible security cameras in the frame. Additionally, there are no windows overlooking the main street visible in this image. The doors present do not have windows or glass panels that would provide visibility to the outside. Therefore, based on this image alone, it is not possible to assess the placement or coverage of security cameras or windows for street visibility and security measures.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDUksGZcg!2e10!4m2!3m1!1s0x8834f1567976d459:0x61823168854497ce"
#       }
#     ],
#     "prompt_used": "\"Analyze the placement and coverage of security cameras and windows overlooking the main street to assess visibility and security measures.\"",
#     "photos_summary": "Across the images, the predominant setting is café or coffee shop interiors and adjacent outdoor seating areas featuring wooden tables, beverages, and occasional decorative items like pastries or plush toys. Large windows overlooking main streets or sidewalks are common, providing natural visibility and passive surveillance opportunities for occupants, though their coverage and security features vary. Notably, visible electronic security measures are minimal; only one image shows a security camera mounted outside above an entrance, while most others reveal no cameras either inside or outside the establishments. Overall, the security approach relies largely on window placement for street visibility rather than extensive use of surveillance cameras.",
#     "street_view": {
#       "vlm_insight": "In the image, there are no visible security cameras mounted on the building facade or near the entrance that directly overlook the main street. The windows on the upper floors provide potential natural surveillance of the street below, offering some visibility for occupants to monitor street activity. The ground floor windows are large and transparent, allowing clear views into and out of the building, which can contribute to passive security through natural observation. Overall, the security measures rely more on window visibility rather than active camera surveillance in this view.",
#       "url": "URL contains api key, can't be exposed"
#     },
#     "working_hours": [
#       "Monday: 7:00 AM – 6:00 PM",
#       "Tuesday: 7:00 AM – 6:00 PM",
#       "Wednesday: 7:00 AM – 6:00 PM",
#       "Thursday: 7:00 AM – 6:00 PM",
#       "Friday: 7:00 AM – 6:00 PM",
#       "Saturday: 8:00 AM – 4:00 PM",
#       "Sunday: 8:00 AM – 4:00 PM"
#     ]
#   },
#   {
#     "name": {
#       "original_name": "La Gourmandine Downtown",
#       "translated_name": "La Gourmandine Downtown"
#     },
#     "type": "bakery",
#     "website": "https://lagourmandinebakery.com/",
#     "google_maps_url": "https://maps.google.com/?cid=15748680301051047918&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQABgEIAA",
#     "phone_number": "(412) 456-2727",
#     "address": "308 Forbes Ave, Pittsburgh, PA 15222, USA",
#     "latitude": 40.4398492,
#     "longitude": -80.0004969,
#     "reviews_summary": "The reviews highlight a charming spot known for its delicious pastries, including a super flaky chocolate croissant, a cheesecake-like cherry dessert, and an authentic almond croissant with a unique texture. Customers appreciated the friendly and knowledgeable staff who provided helpful recommendations and quick, attentive service. Despite a small indoor space, the venue offers additional outdoor seating and a great atmosphere enhanced by a well-curated playlist. Many reviewers expressed a strong desire to return and try more items, praising the quality and value of the food and drinks.",
#     "reviews": [
#       {
#         "author_name": {
#           "original_name": "Celeste Rains-Turk",
#           "translated_name": "Celeste Rains-Turk"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VNaTd0YkxhdF9LSGxBRRAB!2m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee",
#         "text": "What a cool spot! My family loved the pastries we tried from the super flakey chocolate croissant to the amazing texture of the guarmandise and the cheesecake like texture of the cherry dessert my husband got. Plus the man working at the front was so so kind answering our questions about what each item was since they are sophisticated in their names and even gave us recommendations on other spots to check out around town. I want to go back and try their drinks and other goodies.",
#         "original_text": "What a cool spot! My family loved the pastries we tried from the super flakey chocolate croissant to the amazing texture of the guarmandise and the cheesecake like texture of the cherry dessert my husband got. Plus the man working at the front was so so kind answering our questions about what each item was since they are sophisticated in their names and even gave us recommendations on other spots to check out around town. I want to go back and try their drinks and other goodies.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/117190625433930120462/reviews",
#         "publish_date": "a month ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "matcha milk",
#           "translated_name": "matcha milk"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sCi9DQUlRQUNvZENodHljRjlvT21jeUxTMUtkQzFrZFRSWmNTMXRhamQxV1ZObE9WRRAB!2m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee",
#         "text": "Everything looked incredibly good. There was a line when we arrive (Saturday morning 10am) but it moved very quickly. The playlist was the vibes, the service was quick and great. Would love to come back again! It looks small when you walk in but there’s additional seating outside as well.",
#         "original_text": "Everything looked incredibly good. There was a line when we arrive (Saturday morning 10am) but it moved very quickly. The playlist was the vibes, the service was quick and great. Would love to come back again! It looks small when you walk in but there’s additional seating outside as well.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/104359678161845124156/reviews",
#         "publish_date": "a week ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Erica “CA Rizz”",
#           "translated_name": "Erica \"Ca Rizz\""
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VJQ0FnTUNJZ0lHbk13EAE!2m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee",
#         "text": "This is a very interesting Google Contribution.  I always say I like to express these in love and light.\n\nThe only way I got to eat here was by a generous gift from a woman on the PRT Bus 🚍 a few days ago.  She was very kind and I explained to her if I ever see her again and I have the opportunity I will repay her for the $10 gift card ✅.\n\nThe amazing thing is at La Gourmandine, I was able to get a very nice meal and leave a tip for under $10 👀\n\nI will attach photos ASAP ✅🙂\nEDIT: Pics attached March 29th ~ TY",
#         "original_text": "This is a very interesting Google Contribution.  I always say I like to express these in love and light.\n\nThe only way I got to eat here was by a generous gift from a woman on the PRT Bus 🚍 a few days ago.  She was very kind and I explained to her if I ever see her again and I have the opportunity I will repay her for the $10 gift card ✅.\n\nThe amazing thing is at La Gourmandine, I was able to get a very nice meal and leave a tip for under $10 👀\n\nI will attach photos ASAP ✅🙂\nEDIT: Pics attached March 29th ~ TY",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/115679851728590636246/reviews",
#         "publish_date": "3 months ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Cameron",
#           "translated_name": "Cameron"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnTUR3bElqT3R3RRAB!2m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee",
#         "text": "What a lovely experience! Came here right as they opened and had an excellent cappuccino with a great, authentic almond croissant! Texture is kinda like a smashed down croissant but truly different and great flavor, definitely a must-try!",
#         "original_text": "What a lovely experience! Came here right as they opened and had an excellent cappuccino with a great, authentic almond croissant! Texture is kinda like a smashed down croissant but truly different and great flavor, definitely a must-try!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/111604464848598730836/reviews",
#         "publish_date": "3 months ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Paige W",
#           "translated_name": "Paige W"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnTUNneHVuNm1nRRAB!2m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee",
#         "text": "Stopped in on a Sunday morning and snagged the last mozzarella pie! The food and pastry were exquisite and just what we needed after a night out. My latte was also delicious. Definitely recommend coming here.",
#         "original_text": "Stopped in on a Sunday morning and snagged the last mozzarella pie! The food and pastry were exquisite and just what we needed after a night out. My latte was also delicious. Definitely recommend coming here.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/102728475830522547308/reviews",
#         "publish_date": "4 months ago",
#         "rating": 5
#       }
#     ],
#     "rating": "average: 5.0 out of 5 reviews",
#     "reviews_span": "latest date: 2025-07-06, most recent date: 2025-02-16, date difference: 140 days",
#     "url_to_all_photos": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipO7MJEuSUaG-TuNTQ809Zfn0hFTzAHykRUVoWN9!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee",
#     "photos": [
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on the building facade or around the outdoor seating area overlooking the main street. The large windows of the establishment provide clear visibility of the street and sidewalk, which can help with natural surveillance by staff or patrons inside. The windows are positioned at eye level and are sizable, allowing for good coverage of the street area. However, the absence of visible security cameras suggests that electronic surveillance may be limited or not prominently installed in this area.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipO7MJEuSUaG-TuNTQ809Zfn0hFTzAHykRUVoWN9!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       },
#       {
#         "vlm_insight": "The image shows the interior of a bakery with no visible security cameras mounted on the ceiling or walls within the frame. There are no windows overlooking the main street visible in this image, as the view is focused on the display cases and interior shelving. The lighting fixtures and decor do not include any obvious security monitoring devices. Therefore, based on this image alone, there is no evidence of security cameras or windows providing visibility to the main street for security purposes.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIABIhCKmNUqmvS9jbiZ9p2JZKyl!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       },
#       {
#         "vlm_insight": "The image shows a close-up view of croissants displayed inside a bakery or café, with no visible security cameras or windows overlooking a main street. The focus is on the baked goods and interior decor, including a sign that says \"Eat.\" There is no information available in this image to analyze the placement or coverage of security cameras or windows for visibility and security measures.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipMRightpHdBkQ72NLIDlQ1jfY6pAqDf-HtekvES!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of pastries on a countertop and does not include any visible security cameras, windows, or a main street. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows overlooking the main street based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIABIhAkbIj9B1hebDAidrWMdnEJ!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of baked goods with price tags, but it does not provide any view of security cameras or windows overlooking a main street. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipMcy2DWEV6PjMc9xPxv5zMpVwLu-WQ3SNgJJPUk!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of pastries displayed in a bakery case and does not include any visible security cameras, windows, or a main street. Therefore, I cannot analyze the placement or coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIABIhB2pSTo140RavdkuzHmoRDJ!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       },
#       {
#         "vlm_insight": "The image shows the front entrance of La Gourmandine Bakery with large glass windows and doors that provide clear visibility of the interior from the main street. There are no visible security cameras mounted on or near the entrance or the windows overlooking the street. The windows on the upper floor also overlook the main street, potentially offering natural surveillance from inside the building. Overall, the visibility is good due to the glass frontage and upper windows, but there is a lack of visible electronic security measures such as cameras.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgID_8_fx3gE!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a hand holding a pink macaron filled with cream and raspberries. There are no visible security cameras or windows overlooking a street in this image. The background includes a computer screen and some office items, but no relevant security features or street views are present. Therefore, an analysis of security camera placement and window coverage cannot be made based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIABIhAuwBu2rtMybyuIcnsVULiB!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       },
#       {
#         "vlm_insight": "The image shows the interior of a cafe or similar establishment with exposed brick walls and a line of people waiting. There are no visible security cameras mounted on the walls or ceiling inside the space. The windows visible in the image are limited to a small glass door at the back, which does not provide a direct view of the main street. Overall, there appears to be minimal to no visible security camera coverage or windows overlooking the main street for enhanced visibility or security measures.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDnyO-pCA!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a pastry on a plate with a piece of parchment paper underneath, placed on a wooden surface. There are no visible security cameras, windows, or a main street in the image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICRiY_3uAE!2e10!4m2!3m1!1s0x8834f156d7bc000f:0xda8e8d4b3156efee"
#       }
#     ],
#     "prompt_used": "\"Analyze the placement and coverage of security cameras and windows overlooking the main street to assess visibility and security measures.\"",
#     "photos_summary": "The images collectively depict bakery and café settings featuring prominently displayed baked goods such as croissants, pastries, and macarons, often shown in close-up views emphasizing interior decor and food presentation. Several images highlight large glass windows and doors, particularly at the front entrances, providing clear visibility between the interior and the main street, which supports natural surveillance from inside the establishments. However, across all images, there is a consistent absence of visible security cameras or electronic surveillance devices both inside and outside the venues. The interiors commonly include exposed brick walls, display cases, and seating or waiting areas, but lack windows overlooking the main street except for the prominent glass frontages. Overall, the key themes center on bakery and café environments with strong natural visibility through large windows but minimal to no visible electronic security measures.",
#     "street_view": {
#       "vlm_insight": "In the image, there are no visible security cameras mounted on the buildings facing the main street, which suggests limited direct surveillance coverage from this vantage point. The windows on the buildings are large and numerous, especially on the second floors, providing good natural visibility for occupants to observe street activity. The ground-floor windows are also sizable, allowing clear views into and out of the businesses, enhancing passive surveillance. Overall, while window placement supports visibility, the absence of visible security cameras indicates a potential gap in active security monitoring along this section of the street.",
#       "url": "URL contains api key, can't be exposed"
#     },
#     "working_hours": [
#       "Monday: 8:00 AM – 5:00 PM",
#       "Tuesday: 8:00 AM – 5:00 PM",
#       "Wednesday: 8:00 AM – 5:00 PM",
#       "Thursday: 8:00 AM – 5:00 PM",
#       "Friday: 8:00 AM – 5:00 PM",
#       "Saturday: 8:30 AM – 2:30 PM",
#       "Sunday: 8:30 AM – 2:30 PM"
#     ]
#   },
#   {
#     "name": {
#       "original_name": "The Yard",
#       "translated_name": "The Yard"
#     },
#     "type": "bar",
#     "website": "http://www.theyardpgh.com/",
#     "google_maps_url": "https://maps.google.com/?cid=12129389360568354285&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQABgEIAA",
#     "phone_number": "(412) 291-8182",
#     "address": "100 Fifth Ave, Pittsburgh, PA 15222, USA",
#     "latitude": 40.4412646,
#     "longitude": -80.0027879,
#     "reviews_summary": "The Yard in Market Square offers a delightful dining experience with creative and flavorful dishes, such as the standout fried green tomato grilled cheese and a variety of delicious appetizers like soft pretzels with beer cheese and fried pierogis. The staff, including servers like Dani, Eli, and Nikki, receive high praise for their attentive, friendly, and accommodating service, with Nikki even providing a memorable birthday song. Customers appreciate the warm and inviting atmosphere, a wide selection of beers on tap, and the restaurant's commitment to excellent customer care, as demonstrated when a manager personally addressed and corrected an order mistake. Overall, The Yard is highly recommended for its tasty food, exceptional hospitality, and enjoyable ambiance, making it a favorite spot for both locals and visitors.",
#     "reviews": [
#       {
#         "author_name": {
#           "original_name": "Maryann Savage",
#           "translated_name": "Maryann Savage"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VJQ0FnSUNQa3BxMEZnEAE!2m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed",
#         "text": "Had a delicious meal and enjoyable time at The Yard in Market Square! The grilled cheese sandwiches and the unique combinations of ingredients were outstanding!!! I had the fried green tomato grilled cheese that was so flavorful and yummy! I am a huge lover of appetizers so for me, the soft pretzels with beer cheese and fried pierogis were off the charts! Our server, Dani, was wonderful! We enjoyed her company and attention as much as the food! Looking forward to being repeat customers!",
#         "original_text": "Had a delicious meal and enjoyable time at The Yard in Market Square! The grilled cheese sandwiches and the unique combinations of ingredients were outstanding!!! I had the fried green tomato grilled cheese that was so flavorful and yummy! I am a huge lover of appetizers so for me, the soft pretzels with beer cheese and fried pierogis were off the charts! Our server, Dani, was wonderful! We enjoyed her company and attention as much as the food! Looking forward to being repeat customers!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/102936787194249088884/reviews",
#         "publish_date": "7 months ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Lindsay Aiello",
#           "translated_name": "Lindsay Aiello"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnSUNYdmJmSm9nRRAB!2m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed",
#         "text": "Our server was so sweet! She was very helpful in pricing tips on the menu and extremely accommodating.\nThe food was very good - I don't do bread but I did have the Always Sunny Philly without it and it was spectacular!\nThere is a very wide selection of beer on tap!",
#         "original_text": "Our server was so sweet! She was very helpful in pricing tips on the menu and extremely accommodating.\nThe food was very good - I don't do bread but I did have the Always Sunny Philly without it and it was spectacular!\nThere is a very wide selection of beer on tap!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/100182600110326106763/reviews",
#         "publish_date": "8 months ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Emmalee and Theodore Delanoche",
#           "translated_name": "Emmalee and Theodore Delanoche"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VLUDFzdG5ZbC1XN0tBEAE!2m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed",
#         "text": "⭐⭐⭐⭐⭐\n\nIf you're looking for a brunch spot that truly understands the meaning of hospitality, look no further than The Yard! My experience here was nothing short of delightful, even when faced with a small hiccup in our order.\n\nFrom the moment we walked in, the atmosphere was warm and inviting, with a cozy yet vibrant vibe that just screams \"weekend brunch.\" The menu is a treasure trove of creative dishes, and everything we ordered was bursting with flavor and beautifully presented.\n\nNow, let’s talk about the service. When one of our orders came out with bacon—despite requesting it without—what could have been a frustrating moment turned into a shining example of how exceptional customer care can elevate a dining experience. The manager personally approached our table, genuinely apologizing for the oversight. Their accountability and willingness to make things right was truly refreshing. It’s rare to see such commitment to customer satisfaction in the restaurant industry!\n\nNot only did they ensure the mistake was corrected, but they also went above and beyond to make our meal enjoyable. We were treated like valued guests, and it's that kind of attention to detail that sets The Yard apart from other brunch spots.\n\nOverall, The Yard is a must-visit for anyone looking to enjoy a fantastic brunch with delicious food and outstanding service. Whether you're a local or just passing through, this gem will leave you with a smile on your face and a desire to return. Thank you, The Yard, for turning a simple brunch into an extraordinary experience!",
#         "original_text": "⭐⭐⭐⭐⭐\n\nIf you're looking for a brunch spot that truly understands the meaning of hospitality, look no further than The Yard! My experience here was nothing short of delightful, even when faced with a small hiccup in our order.\n\nFrom the moment we walked in, the atmosphere was warm and inviting, with a cozy yet vibrant vibe that just screams \"weekend brunch.\" The menu is a treasure trove of creative dishes, and everything we ordered was bursting with flavor and beautifully presented.\n\nNow, let’s talk about the service. When one of our orders came out with bacon—despite requesting it without—what could have been a frustrating moment turned into a shining example of how exceptional customer care can elevate a dining experience. The manager personally approached our table, genuinely apologizing for the oversight. Their accountability and willingness to make things right was truly refreshing. It’s rare to see such commitment to customer satisfaction in the restaurant industry!\n\nNot only did they ensure the mistake was corrected, but they also went above and beyond to make our meal enjoyable. We were treated like valued guests, and it's that kind of attention to detail that sets The Yard apart from other brunch spots.\n\nOverall, The Yard is a must-visit for anyone looking to enjoy a fantastic brunch with delicious food and outstanding service. Whether you're a local or just passing through, this gem will leave you with a smile on your face and a desire to return. Thank you, The Yard, for turning a simple brunch into an extraordinary experience!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/110193393003664680237/reviews",
#         "publish_date": "a month ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Rob Kurzdorfer",
#           "translated_name": "Rob Kurzdorfer"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VJQ0FnSUM3MS1tVmVBEAE!2m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed",
#         "text": "The beer is Volcano Sauce from Aslin Beer company. It is a fantastic sour ale.\n\nI was visiting from Buffalo, NY and needed a place with a kids menu for my kids.\n\nWe ordered the pub pretzels with beer cheese/mustard as an appetizer and they came out appropriately before the entrees.\n\nKids tenders were good, but seasoned waffle fries (they were delicious) are not something kids will usually eat.\n\nI ordered the Smash Club burger. It wasn’t the color of burger I was expecting (I might get the Yard Burger next time), but it tasted delicious.\n\nThe staff makes this location and we had a great experience",
#         "original_text": "The beer is Volcano Sauce from Aslin Beer company. It is a fantastic sour ale.\n\nI was visiting from Buffalo, NY and needed a place with a kids menu for my kids.\n\nWe ordered the pub pretzels with beer cheese/mustard as an appetizer and they came out appropriately before the entrees.\n\nKids tenders were good, but seasoned waffle fries (they were delicious) are not something kids will usually eat.\n\nI ordered the Smash Club burger. It wasn’t the color of burger I was expecting (I might get the Yard Burger next time), but it tasted delicious.\n\nThe staff makes this location and we had a great experience",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/108576379896053826227/reviews",
#         "publish_date": "9 months ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Katie Fitzgerald",
#           "translated_name": "Katie Fitzgerald"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VJQ0FnTUNZdnBmTVlBEAE!2m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed",
#         "text": "Eli and Nikki were awesome!! Eli was a great waiter , we had so much fun with him and Nikki sang an awesome birthday song to our friend for her 50th. Definitely will be back!!!",
#         "original_text": "Eli and Nikki were awesome!! Eli was a great waiter , we had so much fun with him and Nikki sang an awesome birthday song to our friend for her 50th. Definitely will be back!!!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/112657711221775390607/reviews",
#         "publish_date": "2 months ago",
#         "rating": 5
#       }
#     ],
#     "rating": "average: 5.0 out of 5 reviews",
#     "reviews_span": "latest date: 2025-06-08, most recent date: 2024-10-08, date difference: 243 days",
#     "url_to_all_photos": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgID91NOV_wE!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed",
#     "photos": [
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on the buildings or street fixtures overlooking the main street. The windows on the building labeled \"The Yard\" appear to be limited in number and size, with some windows higher up on the adjacent building, which may provide some natural surveillance but not extensive coverage of the street level. The street view is partially obstructed by a white van, which could limit visibility from certain angles. Overall, the security measures in terms of camera placement and window coverage for street surveillance appear minimal or not clearly evident in this scene.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgID91NOV_wE!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       },
#       {
#         "vlm_insight": "The image provided is a close-up of a dish of macaroni and cheese with bits of bacon and sprinkled herbs. There are no visible security cameras, windows, or any elements related to visibility or security measures overlooking a main street in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows based on this photo.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipMlAqiQ98iAvJkdZrtr1-Fmaiz-8UCiIlNOwmau!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a meal on a table, featuring a grilled cheese sandwich, waffle fries, curly fries, and a dipping sauce. There are no visible security cameras or windows overlooking a street in this image. The setting appears to be indoors at a restaurant or bar, with no clear view of any exterior security measures. Therefore, it is not possible to analyze the placement or coverage of security cameras or windows from this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgMCg1pig3QE!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a food dish on a wooden table, with no visible security cameras or windows. There are no elements in the image that provide information about visibility or security measures related to a main street. The focus is entirely on the food and drink, so no assessment of security camera placement or window coverage can be made from this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICnvpWWlQE!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a sandwich and chips on a table inside a restaurant. There are no visible security cameras or windows overlooking a main street in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this photo.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipP9LjlBfn4SXoeHSX0fQl6LqLOaC_qI5MOAvEHJ!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a table with food and drinks inside a restaurant, but it does not provide a view of the main street, windows, or any security cameras. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows overlooking the main street based on this image. Additional images showing the exterior or window views would be needed for such an assessment.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDHwenH9gE!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a meal consisting of a burger and waffle fries on a tray, with drinks and other dining items in the background. There are no visible security cameras or windows overlooking a main street in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this photo.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICPkpq0jgE!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       },
#       {
#         "vlm_insight": "The image shows a bar or restaurant interior with multiple windows overlooking the main street, providing natural visibility from inside to outside. However, there are no visible security cameras mounted on the walls or ceiling inside the establishment that would cover the main street or interior. The windows are large and clear, allowing good visibility of the street area, but the absence of visible cameras suggests limited electronic surveillance coverage. Overall, security measures rely primarily on natural visibility through windows rather than active camera monitoring.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICPkpq0Dg!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of food baskets on a table inside a restaurant, with no visible security cameras or windows overlooking a main street. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDx9fr7Vw!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       },
#       {
#         "vlm_insight": "The image shows a dessert on a plate and does not contain any visible security cameras, windows, or a main street. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipNDgT1S2f0jqQbVKGaJpcCz5y96bklfiJgFHkTu!2e10!4m2!3m1!1s0x8834f1569cad7b5d:0xa8543f5bf31445ed"
#       }
#     ],
#     "prompt_used": "\"Analyze the placement and coverage of security cameras and windows overlooking the main street to assess visibility and security measures.\"",
#     "photos_summary": "The images predominantly depict close-up views of various food dishes and restaurant interiors, featuring items such as sandwiches, fries, macaroni and cheese, burgers, and desserts, with settings mainly indoors at dining tables or bars. Only two images provide exterior or window views: one shows a main street scene with minimal window coverage and no visible security cameras, and another reveals a restaurant interior with large windows offering natural visibility to the street but lacking any visible electronic surveillance. Overall, the key themes center on casual dining environments with limited or no evident security camera presence, relying primarily on natural window visibility rather than active monitoring for street-level surveillance.",
#     "street_view": {
#       "vlm_insight": "The image shows the interior of a building, likely a restaurant or bar, with wooden paneling and a counter area. There are no visible security cameras mounted on the walls or ceiling in the immediate area shown. Additionally, there are no windows visible in this image that overlook a main street or provide external visibility. Therefore, based on this image alone, there is limited information to assess the placement and coverage of security cameras or windows for street visibility and security measures.",
#       "url": "URL contains api key, can't be exposed"
#     },
#     "working_hours": [
#       "Monday: 11:00 AM – 10:00 PM",
#       "Tuesday: 11:00 AM – 10:00 PM",
#       "Wednesday: 11:00 AM – 10:00 PM",
#       "Thursday: 11:00 AM – 10:00 PM",
#       "Friday: 11:00 AM – 12:00 AM",
#       "Saturday: 10:00 AM – 12:00 AM",
#       "Sunday: 10:00 AM – 10:00 PM"
#     ]
#   },
#   {
#     "name": {
#       "original_name": "Cafe Milano",
#       "translated_name": "Cafe Milano"
#     },
#     "type": "pizza_restaurant",
#     "website": "http://pizzamilano.net/",
#     "google_maps_url": "https://maps.google.com/?cid=17276075191803242580&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQABgEIAA",
#     "phone_number": "(412) 281-3131",
#     "address": "134 6th St, Pittsburgh, PA 15222, USA",
#     "latitude": 40.4431334,
#     "longitude": -80.0025034,
#     "reviews_summary": "Cafe Milano offers a good variety of pizzas, with their specialty pizzas like chicken and spinach standing out as the best options, while their traditional pizzas are decent but less impressive. Customers appreciate the fresh and flavorful toppings, prompt delivery service, and the ease of online ordering, making it a convenient choice for both dine-in and delivery. The wings, especially the Buffalo wings, receive high praise for their unique, well-balanced sauce and exceptional flavor, making them a must-try item. However, not all experiences are positive, as one reviewer found the place unclean and the pizza greasy with an unpleasant aftertaste, which they would not recommend.",
#     "reviews": [
#       {
#         "author_name": {
#           "original_name": "Dennis Govachini",
#           "translated_name": "Dennis Govachini"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sCi9DQUlRQUNvZENodHljRjlvT2xKbFZrTTVTMFpJVjNvNE4yaFNka0kyUjJoR2VtYxAB!2m1!1s0x8834f15672513693:0xefc0f2dab85ee854",
#         "text": "Cafe Milano has good variety in types of pizza and food. Their strength is good specialty pizzas like chicken and spinach ...but I am biased .Their salads are good and fresh and delivery is an option and prompt. They have traditional pizza also ..it's Fine but not as good as their specialty items.",
#         "original_text": "Cafe Milano has good variety in types of pizza and food. Their strength is good specialty pizzas like chicken and spinach ...but I am biased .Their salads are good and fresh and delivery is an option and prompt. They have traditional pizza also ..it's Fine but not as good as their specialty items.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/111445939446877631365/reviews",
#         "publish_date": "2 weeks ago",
#         "rating": 4
#       },
#       {
#         "author_name": {
#           "original_name": "Josh Bartolovich",
#           "translated_name": "Josh Bartolovich"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnSUN6cllMRG9RRRAB!2m1!1s0x8834f15672513693:0xefc0f2dab85ee854",
#         "text": "Our pizzas came out hot and fresh. Service here was great also. We had a medium pepperoni pizza with extra cheese, and they loaded it up. We also got a small pizza with black olives and mushrooms, which tasted very fresh and not canned. We will be back here again to try out more food. Pizza is a solid 8/10",
#         "original_text": "Our pizzas came out hot and fresh. Service here was great also. We had a medium pepperoni pizza with extra cheese, and they loaded it up. We also got a small pizza with black olives and mushrooms, which tasted very fresh and not canned. We will be back here again to try out more food. Pizza is a solid 8/10",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/113123251425427291396/reviews",
#         "publish_date": "a year ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Mark D",
#           "translated_name": "Mark D"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VMbUsxNjdKa2NYRGl3RRAB!2m1!1s0x8834f15672513693:0xefc0f2dab85ee854",
#         "text": "The place is a filthy dump. Ordered a slice of pepperoni. It was a grease bomb. Bad aftertaste too... I would not recommend it.",
#         "original_text": "The place is a filthy dump. Ordered a slice of pepperoni. It was a grease bomb. Bad aftertaste too... I would not recommend it.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/102650184565507330653/reviews",
#         "publish_date": "a month ago",
#         "rating": 1
#       },
#       {
#         "author_name": {
#           "original_name": "Roxanne",
#           "translated_name": "Roxanne"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnSURIdWFDQ2xBRRAB!2m1!1s0x8834f15672513693:0xefc0f2dab85ee854",
#         "text": "I visit Pittsburgh often for concerts or work. I have ordered delivery from here about 3 times. Pizza was phenomenal. The salads have been delicious, fresh, and large portions for what you pay. Great value. Easy ordering online and getting delivered to hotel. I would absolutely recommend the food here!",
#         "original_text": "I visit Pittsburgh often for concerts or work. I have ordered delivery from here about 3 times. Pizza was phenomenal. The salads have been delicious, fresh, and large portions for what you pay. Great value. Easy ordering online and getting delivered to hotel. I would absolutely recommend the food here!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/101463978080992568305/reviews",
#         "publish_date": "9 months ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Alonzo D. Craig",
#           "translated_name": "Alonzo D. Craig"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnTURvMnFYbHd3RRAB!2m1!1s0x8834f15672513693:0xefc0f2dab85ee854",
#         "text": "The hands down best place for pizza and wings downtown. Crust to topping, each part of the pizza stood on its own but also excellently blended with the other parts in a blessed union of flavor and texture. And the wings are a monument to culinary genius. The sauce for the Buffalo wings, in my opinion, is unmatched. The aroma turns heads as soon as I open the box. It is tangy, yet buttery, yet savory, yet expertly hot. I will try everything on the menu. I suggest you do the same.",
#         "original_text": "The hands down best place for pizza and wings downtown. Crust to topping, each part of the pizza stood on its own but also excellently blended with the other parts in a blessed union of flavor and texture. And the wings are a monument to culinary genius. The sauce for the Buffalo wings, in my opinion, is unmatched. The aroma turns heads as soon as I open the box. It is tangy, yet buttery, yet savory, yet expertly hot. I will try everything on the menu. I suggest you do the same.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/116795284390668686752/reviews",
#         "publish_date": "2 months ago",
#         "rating": 5
#       }
#     ],
#     "rating": "average: 4.0 out of 5 reviews",
#     "reviews_span": "latest date: 2025-06-27, most recent date: 2024-06-04, date difference: 388 days",
#     "url_to_all_photos": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDforLwrwE!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854",
#     "photos": [
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on the exterior of the buildings facing the main street, which may limit direct surveillance coverage from this vantage point. The large windows of Cafe Milano provide clear visibility into the interior from the street, allowing for natural observation by patrons and staff, which can act as a passive security measure. The adjacent building also has windows overlooking the street, but these are smaller and less prominent. Overall, the security relies more on natural visibility through windows rather than on active camera surveillance in this area.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDforLwrwE!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       },
#       {
#         "vlm_insight": "The image shows two pieces of stuffed bread or calzones on a wooden surface. There are no visible security cameras or windows overlooking a main street in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipNqisRBnFtfik9inGo2CZvdhup-faLd-sHX_0_0!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       },
#       {
#         "vlm_insight": "The image shows close-up slices of pepperoni and cheese pizza on a paper plate. There are no visible security cameras or windows overlooking a main street in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows based on this photo. Please provide an image showing the exterior or interior of a building for such an assessment.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICzndbqbw!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       },
#       {
#         "vlm_insight": "The image shows the interior of a restaurant with no visible windows overlooking a main street, limiting natural visibility to the outside. There are no security cameras visible inside the dining area or near the entrance that can be seen from this angle. The layout focuses on seating and the kitchen area, with no apparent security measures such as cameras or window surveillance evident in the image. Overall, the current setup does not provide clear visibility or security coverage of the main street outside.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDforLwDw!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a food item, specifically a gyro or wrap with grilled meat, onions, and vegetables, accompanied by two dipping sauces. There are no visible security cameras, windows, or street views in the image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows overlooking the main street based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipNlvid3CsR1qqPrSdXWZYF_VdLCBtBm2tsEPrab!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       },
#       {
#         "vlm_insight": "The image shows a pizza in an open cardboard box on a table. There are no visible security cameras, windows, or street views in the image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows overlooking the main street based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDenoWQXQ!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a pizza on a metal tray placed on a wooden table. There are no visible security cameras, windows, or any street views in this image. Therefore, it is not possible to analyze the placement or coverage of security cameras or windows overlooking the main street based on this photo.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIC19M3BwwE!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a bowl of soup on a plate with some vegetables and a sign in the background. There are no visible security cameras or windows overlooking a main street in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipMqvwPuqUmXxFFxx6qS2lxG7AFotc8rGfusRi0b!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       },
#       {
#         "vlm_insight": "The image shows a plate of creamy pasta with shrimp and a piece of garlic bread on a wooden table inside a restaurant. There are no visible windows or security cameras in the image, and the setting appears to be indoors. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows overlooking the main street based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICr9s6bPg!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of food, specifically fried items sprinkled with grated cheese, placed on aluminum foil. There are no visible security cameras, windows, or a main street in the image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICh3J28hwE!2e10!4m2!3m1!1s0x8834f15672513693:0xefc0f2dab85ee854"
#       }
#     ],
#     "prompt_used": "\"Analyze the placement and coverage of security cameras and windows overlooking the main street to assess visibility and security measures.\"",
#     "photos_summary": "The images predominantly depict various food items—including pizza, calzones, gyros, pasta, soup, and fried dishes—often presented on wooden tables or plates within indoor restaurant settings. Only one image shows an exterior urban scene featuring buildings with large windows overlooking a main street, notably at Cafe Milano, where natural visibility through windows serves as a passive security measure in the absence of visible security cameras. Across the remaining images, there are no visible security cameras, windows facing streets, or overt security features, with most focusing solely on close-up views of food indoors without external views or surveillance elements.",
#     "street_view": {
#       "vlm_insight": "The image shows the interior of a restaurant or cafe with seating areas and large windows facing the main street. There are no visible security cameras mounted on the walls or ceiling within this view. The windows provide natural light and clear visibility to the outside, which could allow staff to observe the main street. However, based on this image alone, there is no direct evidence of active security camera coverage overlooking the main street.",
#       "url": "URL contains api key, can't be exposed"
#     },
#     "working_hours": [
#       "Monday: 10:00 AM – 1:00 AM",
#       "Tuesday: 10:00 AM – 1:00 AM",
#       "Wednesday: 10:00 AM – 1:00 AM",
#       "Thursday: 10:00 AM – 1:00 AM",
#       "Friday: 10:00 AM – 2:00 AM",
#       "Saturday: 10:00 AM – 2:00 AM",
#       "Sunday: 10:00 AM – 1:00 AM"
#     ]
#   },
#   {
#     "name": {
#       "original_name": "The Coffee Village",
#       "translated_name": "The Coffee Village"
#     },
#     "type": "coffee_shop",
#     "website": "https://coffeevillages.com/",
#     "google_maps_url": "https://maps.google.com/?cid=3239265752839321811&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQABgEIAA",
#     "phone_number": "(412) 586-5750",
#     "address": "801 Liberty Ave, Pittsburgh, PA 15222, USA",
#     "latitude": 40.442858799999996,
#     "longitude": -79.9989232,
#     "reviews_summary": "The reviews for this coffee spot are mixed, with some customers praising the friendly staff and pleasant atmosphere, while others experienced disappointing service. Several reviewers enjoyed the food and drinks, highlighting the delicious cinnamon rolls, delightful vanilla chai latte, and good house blend coffee. However, a few customers were let down by the quality of the espresso and caramel syrup, as well as encountering rude and unkind staff members. Despite these issues, the café is appreciated for its convenient early weekend hours and availability of seating for those looking to work.",
#     "reviews": [
#       {
#         "author_name": {
#           "original_name": "Simi Odette",
#           "translated_name": "Like"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sCi9DQUlRQUNvZENodHljRjlvT25WQlZ6SkNWRlZrU0ZVNVFqUlJVV2x3Y2pOb2FHYxAB!2m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3",
#         "text": "The lady working at the register was nice and friendly explaining the latte sizes and espresso shots. Unfortunately, the drink itself was a letdown. I didn’t see a fresh espresso shot pulled, and it tasted like it had been sitting out, maybe from their previous orders, weak and not very fresh. The caramel syrup also tasted low quality. Probably won’t be coming back.",
#         "original_text": "The lady working at the register was nice and friendly explaining the latte sizes and espresso shots. Unfortunately, the drink itself was a letdown. I didn’t see a fresh espresso shot pulled, and it tasted like it had been sitting out, maybe from their previous orders, weak and not very fresh. The caramel syrup also tasted low quality. Probably won’t be coming back.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/102766337298061451165/reviews",
#         "publish_date": "2 weeks ago",
#         "rating": 2
#       },
#       {
#         "author_name": {
#           "original_name": "Jackie Robert",
#           "translated_name": "Jackie Robert"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sCi9DQUlRQUNvZENodHljRjlvT205NVZYQktMWFIyTkVWNVVHTXhRbTVJVUVvMVJIYxAB!2m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3",
#         "text": "Eating here was a lovely experience, wonderfully climate controlled, breakfast items were beyond my expectations and the vanilla chai latte I ordered was delightful. This is my go-to spot in Pittsburgh. I highly recommend it. 💜",
#         "original_text": "Eating here was a lovely experience, wonderfully climate controlled, breakfast items were beyond my expectations and the vanilla chai latte I ordered was delightful. This is my go-to spot in Pittsburgh. I highly recommend it. 💜",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/113938063459252424644/reviews",
#         "publish_date": "a week ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Wyatt Edmundson",
#           "translated_name": "Wyatt Edmundson"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sCi9DQUlRQUNvZENodHljRjlvT2pOcGJIWkllV1prZFVkak5rRnZZVmRHU0haZlNrRRAB!2m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3",
#         "text": "We came here after getting exceptionally terrible service somewhere else down the street. Much kinder atmosphere and we were served very quickly. The cinnamon rolls are delectable.",
#         "original_text": "We came here after getting exceptionally terrible service somewhere else down the street. Much kinder atmosphere and we were served very quickly. The cinnamon rolls are delectable.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/115954808033221137264/reviews",
#         "publish_date": "a week ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Alivia Gaydos",
#           "translated_name": "Relieves gaydos"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnSUMzdXF1NDJnRRAB!2m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3",
#         "text": "I want to say that I don’t typically leave reviews ever. I came here with my sisters yesterday after Pittsburgh’s 10k race. This place happened to be on the way to were we were headed and wanted to grab a quick drink and warm up. There was one middle aged man working who was nothing but rude and unkind. I initially assumed that maybe he was having a rough day but by the end of my short visit it was clear that he was just a very miserable guy. My sister ordered a latte and we sat down for literally 2 minutes before she went up to ask for a bathroom key in which he responded that you have to buy something. We told him that we literally just bought a drink (as if he couldn’t remember us from a minute ago) and he continued to bend over the counter and ask as where it was at to which we said it was on the table where we were sitting at. He then proceeded to throw the bathroom key on the counter and we left. If you’ve seen the movie Anyone but You this was that but worse.",
#         "original_text": "I want to say that I don’t typically leave reviews ever. I came here with my sisters yesterday after Pittsburgh’s 10k race. This place happened to be on the way to were we were headed and wanted to grab a quick drink and warm up. There was one middle aged man working who was nothing but rude and unkind. I initially assumed that maybe he was having a rough day but by the end of my short visit it was clear that he was just a very miserable guy. My sister ordered a latte and we sat down for literally 2 minutes before she went up to ask for a bathroom key in which he responded that you have to buy something. We told him that we literally just bought a drink (as if he couldn’t remember us from a minute ago) and he continued to bend over the counter and ask as where it was at to which we said it was on the table where we were sitting at. He then proceeded to throw the bathroom key on the counter and we left. If you’ve seen the movie Anyone but You this was that but worse.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/108555826184762139827/reviews",
#         "publish_date": "8 months ago",
#         "rating": 1
#       },
#       {
#         "author_name": {
#           "original_name": "Paul K",
#           "translated_name": "Paul K."
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnSUM3bExxWDlnRRAB!2m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3",
#         "text": "Solid spot to grab coffee, the house blend was very good.  Never too busy to find a table to sit and work.  Appreciated that they opened early on the weekends.",
#         "original_text": "Solid spot to grab coffee, the house blend was very good.  Never too busy to find a table to sit and work.  Appreciated that they opened early on the weekends.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/114511188461162963688/reviews",
#         "publish_date": "11 months ago",
#         "rating": 5
#       }
#     ],
#     "rating": "average: 3.6 out of 5 reviews",
#     "reviews_span": "latest date: 2025-07-05, most recent date: 2024-08-12, date difference: 327 days",
#     "url_to_all_photos": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICb_8eYIQ!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3",
#     "photos": [
#       {
#         "vlm_insight": "The image shows the exterior of The Coffee Village with large windows facing the main street, providing good visibility into the café from the outside. There are no visible security cameras mounted on the building's exterior near the entrance or windows. The windows offer natural surveillance potential, but the absence of visible cameras may indicate limited electronic security coverage for the street-facing area. Overall, the security measures rely primarily on visibility through windows rather than camera surveillance.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICb_8eYIQ!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       },
#       {
#         "vlm_insight": "The image shows the interior of a cafe or bakery counter with baked goods displayed, but it does not provide a view of any security cameras or windows overlooking a main street. There are no visible security cameras mounted on the walls or ceiling in this image. Additionally, there are no windows shown that would provide visibility to an outside street. Therefore, an assessment of visibility and security measures related to cameras and windows cannot be made based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgID4qdTdBw!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       },
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on or around the storefront of \"Crazy Mocha\" that directly overlook the main street. The large windows provide clear visibility into the interior of the coffee shop, which could allow employees or patrons to observe street activity. However, the absence of visible cameras suggests limited electronic surveillance coverage of the main street area from this vantage point. The windows do contribute to natural visibility but do not replace the security benefits of strategically placed cameras.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICcyJrAbw!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       },
#       {
#         "vlm_insight": "In the image, there is one visible security camera mounted on the ceiling near the entrance door, positioned to cover the main entrance and the interior area close to the door. The large windows on either side of the entrance provide clear visibility of the main street from inside the establishment, allowing patrons and staff to observe street activity. The camera placement focuses on monitoring the entrance rather than the street outside, relying on the windows for external visibility. Overall, the combination of the camera and large windows offers good coverage of the entrance and street view, enhancing security and situational awareness.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICG_cfFAQ!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       },
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on the walls or ceiling inside the coffee shop that overlook the main street or the interior area near the counter. The windows visible are located behind the counter area, but they do not appear to directly face the main street; they seem to look outside but the exact street view is not clear. The interior lighting and layout focus on customer service and product display rather than visible security measures. Overall, there is limited visible coverage from security cameras or windows specifically positioned for monitoring the main street or the shop's entrance area.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICcpLz2vgE!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       },
#       {
#         "vlm_insight": "The image shows an indoor setting with a table, chairs, and a coffee cup, but there are no visible security cameras or windows overlooking a main street. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this image. Additional images or information showing the exterior or surveillance setup would be needed for such an assessment.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIC3uqu4-gE!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       },
#       {
#         "vlm_insight": "The image shows the interior of a café or similar establishment, focusing on a table with a coffee cup. There are no visible security cameras in the frame, and no windows overlooking a main street can be seen. The walls feature colorful artwork, but no security or surveillance equipment is apparent. Therefore, based on this image alone, it is not possible to assess the visibility or security measures related to cameras or windows overlooking the main street.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgID-9OuKuAE!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       },
#       {
#         "vlm_insight": "In the image, there are no visible security cameras installed inside the café or near the windows overlooking the main street. The large front windows provide clear visibility of the street from inside, allowing natural surveillance by patrons and staff. However, the absence of visible cameras suggests limited electronic security coverage for monitoring the exterior or interior areas. Overall, security relies primarily on natural visibility through the windows rather than on camera surveillance.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICrvpmmxAE!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       },
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on the buildings overlooking the narrow street. The windows on both sides of the alley are present but appear to be limited in number and mostly high up, which may reduce direct visibility of street-level activity. The alley is relatively enclosed by tall buildings, which could create blind spots and limit natural surveillance. Overall, the current placement of windows and absence of visible security cameras suggest limited active security coverage and visibility on this street.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICHhpHxFw!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       },
#       {
#         "vlm_insight": "The image shows a wall covered with various posters and flyers under a bright wall-mounted light fixture. There are no visible security cameras in the image. Additionally, there are no windows overlooking a main street or any outdoor area; the setting appears to be an indoor space. Therefore, visibility and security measures related to cameras or windows cannot be assessed from this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICG_cfFQQ!2e10!4m2!3m1!1s0x8834f157ead15ad7:0x2cf42f0a331378d3"
#       }
#     ],
#     "prompt_used": "\"Analyze the placement and coverage of security cameras and windows overlooking the main street to assess visibility and security measures.\"",
#     "photos_summary": "The images collectively depict café and street settings characterized by large windows that provide natural visibility into interiors and onto adjacent streets, facilitating informal surveillance by patrons and staff. However, across multiple scenes—including storefronts like The Coffee Village and Crazy Mocha, interior café counters, and narrow alleyways—there is a notable absence or minimal presence of visible security cameras, with only one image showing a ceiling-mounted camera focused on an entrance area. Indoor spaces often emphasize customer service and ambiance, featuring tables, coffee cups, and artwork, but lack evident electronic surveillance or windows overlooking main streets. Enclosed alleys with high, sparse windows further limit natural street-level visibility, suggesting overall reliance on passive observation through windows rather than active camera-based security measures.",
#     "street_view": {
#       "vlm_insight": "The image shows a brick building with a large window facing a narrow street or alley. There are no visible security cameras mounted on the exterior wall or near the window to monitor the main street. The window provides some visibility of the interior but does not appear to offer a broad view of the street outside. Overall, security camera coverage and visibility from windows overlooking the main street seem limited in this area.",
#       "url": "URL contains api key, can't be exposed"
#     },
#     "working_hours": [
#       "Monday: 6:00 AM – 5:00 PM",
#       "Tuesday: 6:00 AM – 5:00 PM",
#       "Wednesday: 6:00 AM – 5:00 PM",
#       "Thursday: 6:00 AM – 5:00 PM",
#       "Friday: 6:00 AM – 5:00 PM",
#       "Saturday: 8:00 AM – 4:00 PM",
#       "Sunday: 8:00 AM – 4:00 PM"
#     ]
#   },
#   {
#     "name": {
#       "original_name": "Bae Bae's Cafe",
#       "translated_name": "Bae Bae's Cafe"
#     },
#     "type": "cafe",
#     "website": "https://www.toasttab.com/baebaescafe/v3",
#     "google_maps_url": "https://maps.google.com/?cid=10853534986816994947&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQABgEIAA",
#     "phone_number": "(412) 258-6322",
#     "address": "945 Liberty Ave, Pittsburgh, PA 15222, USA",
#     "latitude": 40.443601199999996,
#     "longitude": -79.9965213,
#     "reviews_summary": "The cafe offers a charming and elegant atmosphere with friendly and efficient service, including occasional complimentary treats like scones and muffins, which enhances the overall experience. Many customers praise the delicious food and coffee, as well as the appealing decor and lively music, making it a desirable spot to visit regularly if nearby. However, some have had less positive experiences, citing issues such as drinks not matching their orders, poor drink presentation, and staff seeming unsure or nervous, which detracted from their visit. Additionally, ordering can be challenging due to the requirement to use a QR code and occasional online ordering difficulties, though those who manage to order generally find the food excellent.",
#     "reviews": [
#       {
#         "author_name": {
#           "original_name": "hallow",
#           "translated_name": "hallow"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnTUR3NTdtZmt3RRAB!2m1!1s0x8834f109a0d0b203:0x969f8090e6803e83",
#         "text": "Such a cute spot with an elegant atmosphere! The barista was incredibly kind and fast, and even gave us a free scone on the house! Food and coffee was delicious, I'd definitely be a regular here if i lived close.",
#         "original_text": "Such a cute spot with an elegant atmosphere! The barista was incredibly kind and fast, and even gave us a free scone on the house! Food and coffee was delicious, I'd definitely be a regular here if i lived close.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/104086579432021334727/reviews",
#         "publish_date": "3 months ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Pranita Chakkingal",
#           "translated_name": "Pranita chakkingal"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnTURnc3ZfYTBBRRAB!2m1!1s0x8834f109a0d0b203:0x969f8090e6803e83",
#         "text": "I got the Passionfruit Pea Flower Coconut\nTropical Fruit, Perfect cooler(Caffeine Free) with the lychee boba. I thought it was too sweet and had a slightly weird after taste but the flavor was overall good. They gave us free strawberry muffins, though.",
#         "original_text": "I got the Passionfruit Pea Flower Coconut\nTropical Fruit, Perfect cooler(Caffeine Free) with the lychee boba. I thought it was too sweet and had a slightly weird after taste but the flavor was overall good. They gave us free strawberry muffins, though.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/107093241639003061267/reviews",
#         "publish_date": "4 months ago",
#         "rating": 3
#       },
#       {
#         "author_name": {
#           "original_name": "adrianna juliette",
#           "translated_name": "adrianna juliette"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnSURibUlYSGx3RRAB!2m1!1s0x8834f109a0d0b203:0x969f8090e6803e83",
#         "text": "Waking up in downtown Pittsburgh, I felt hungry, thirsty, but excited to take on the day! Making Bae Bae’s Cafe my first stop was an excellent choice! The music was great, eye-catching decor, and our food and drinks were so so soooo yummy. For sure would come here again if I lived in the area! Check em out man!",
#         "original_text": "Waking up in downtown Pittsburgh, I felt hungry, thirsty, but excited to take on the day! Making Bae Bae’s Cafe my first stop was an excellent choice! The music was great, eye-catching decor, and our food and drinks were so so soooo yummy. For sure would come here again if I lived in the area! Check em out man!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/106992775380273755737/reviews",
#         "publish_date": "11 months ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "N N",
#           "translated_name": "N N"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VNSDZ6WnJsOVBqV3F3RRAB!2m1!1s0x8834f109a0d0b203:0x969f8090e6803e83",
#         "text": "Sketchy neighborhood, but I liked the cute interior if the place. However the beverage I ordered did not taste like anything I ordered and to be honest it was not good. Also the lady seemed to have a hard time pitting a lid on and gave it to me with what seemed like a  somewhat dented lid. What made me more anxious was her nervous look on her face as she gave it to me. Please do not make drinks if you don’t know how to make them and certainly do not give a “to go drink” if you cant find a descent lid. Will not be returning here.",
#         "original_text": "Sketchy neighborhood, but I liked the cute interior if the place. However the beverage I ordered did not taste like anything I ordered and to be honest it was not good. Also the lady seemed to have a hard time pitting a lid on and gave it to me with what seemed like a  somewhat dented lid. What made me more anxious was her nervous look on her face as she gave it to me. Please do not make drinks if you don’t know how to make them and certainly do not give a “to go drink” if you cant find a descent lid. Will not be returning here.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/104723466149760412805/reviews",
#         "publish_date": "a month ago",
#         "rating": 1
#       },
#       {
#         "author_name": {
#           "original_name": "Cherie Peters",
#           "translated_name": "Cherie Peters"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnTURRbjhybTBnRRAB!2m1!1s0x8834f109a0d0b203:0x969f8090e6803e83",
#         "text": "Tried ordering from this place twice, in person and online. When I went in person she told me I had to order with the QR code and she couldn't tell me how long it would take to get my order. I didn't have time to wait around so I had to leave. Today I tried ordering on-line and the order wouldn't go through. I really want to try their food. It looks really good. It is just really frustrating trying to order anything if you are on a schedule.\n\nUpdate: I finally was able to order some food from here. The food was excellent.",
#         "original_text": "Tried ordering from this place twice, in person and online. When I went in person she told me I had to order with the QR code and she couldn't tell me how long it would take to get my order. I didn't have time to wait around so I had to leave. Today I tried ordering on-line and the order wouldn't go through. I really want to try their food. It looks really good. It is just really frustrating trying to order anything if you are on a schedule.\n\nUpdate: I finally was able to order some food from here. The food was excellent.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/104962182885021889015/reviews",
#         "publish_date": "4 months ago",
#         "rating": 5
#       }
#     ],
#     "rating": "average: 3.8 out of 5 reviews",
#     "reviews_span": "latest date: 2025-05-28, most recent date: 2024-08-01, date difference: 300 days",
#     "url_to_all_photos": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICu5pbM4wE!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83",
#     "photos": [
#       {
#         "vlm_insight": "The image shows a seating area inside a room with a large window overlooking the main street, providing good natural visibility of the outside. There are no visible security cameras inside the room or mounted near the window that would cover the main street area. The window itself allows for direct visual monitoring of the street but lacks any electronic surveillance equipment. Overall, security measures in terms of camera coverage appear to be absent or minimal based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICu5pbM4wE!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a bubble tea drink on a wooden table indoors. There are no visible security cameras or windows overlooking a main street in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this photo. Additional images or context would be needed for such an assessment.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgMDgsv_acA!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       },
#       {
#         "vlm_insight": "The image shows an interior ceiling decorated with colorful hanging lanterns and umbrellas, with no visible security cameras. The walls have bookshelves and decorative items, but there are no windows overlooking a main street in this view. Therefore, no assessment of visibility or security measures related to cameras or windows can be made based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgMDw57mfMw!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       },
#       {
#         "vlm_insight": "The image shows an indoor retail setting with shelves and decorative items on a green wall, but there are no visible security cameras or windows overlooking a main street. The absence of these elements means there is no direct indication of visibility or security measures related to monitoring the street. The focus appears to be on product display and interior decor rather than external surveillance. Therefore, no assessment of security camera placement or window coverage for street visibility can be made from this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICLg8yAJA!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       },
#       {
#         "vlm_insight": "The image does not show any security cameras or windows overlooking a main street. It depicts an indoor setting with a hand holding a bubble tea drink in front of a green wall decorated with flowers and the letters \"BAE.\" There are shelves with products in the background, but no visible security or street-facing features. Therefore, no assessment of visibility or security measures related to cameras or windows can be made from this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEO7QubeL7fak5gE!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a sandwich and does not include any visible security cameras, windows, or street views. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows overlooking the main street based on this image. If you provide an image showing the exterior of a building or street view, I can assist with that analysis.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICrqIf5IQ!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       },
#       {
#         "vlm_insight": "The image shows the interior of a room with hanging lanterns and a hanging chair, but there are no visible security cameras in the frame. Additionally, there are no windows clearly overlooking a main street visible in this image. The focus is more on the interior decor rather than on security features or external visibility. Therefore, it is not possible to assess visibility or security measures related to cameras or windows from this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICe2p3jzAE!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       },
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on the buildings or street poles overlooking the main street. The windows on the buildings facing the street are numerous and provide good natural visibility of the street below, especially from the upper floors. The street is well-lit with traffic lights and signage, but there is no evident electronic surveillance coverage. Overall, visibility is primarily through natural observation from windows rather than through installed security cameras.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgIDpmOSLBw!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       },
#       {
#         "vlm_insight": "In the image, there are no visible security cameras mounted on the building or nearby structures that directly overlook the main street. The windows on the building are large and provide clear visibility of the street area, which could allow occupants to monitor street activity. However, the presence of decorative sculptures near the windows might partially obstruct some sightlines. Overall, the security measures appear limited to natural surveillance through windows, with no evident electronic surveillance devices in place.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICun4D5Lw!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       },
#       {
#         "vlm_insight": "The image shows an indoor setting with decorative elements such as a golden gorilla statue, hanging lanterns, and a mirror reflecting part of the room. There are no visible security cameras in the image. The windows visible in the reflection do not appear to overlook a main street, and their coverage or visibility for security purposes cannot be assessed from this image. Overall, there is no clear indication of security measures related to cameras or window placement for street surveillance.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgICexLnGIg!2e10!4m2!3m1!1s0x8834f109a0d0b203:0x969f8090e6803e83"
#       }
#     ],
#     "prompt_used": "\"Analyze the placement and coverage of security cameras and windows overlooking the main street to assess visibility and security measures.\"",
#     "photos_summary": "The images collectively depict various indoor settings characterized by decorative elements such as hanging lanterns, umbrellas, shelves with products, and unique items like a golden gorilla statue and a hanging chair, alongside close-ups of food and drinks like bubble tea and sandwiches. Several images feature windows that provide natural visibility of main street areas, often from upper floors, enabling passive surveillance through direct observation; however, no electronic security cameras or surveillance devices are visible either inside the rooms or mounted externally on buildings or street poles. The overall theme emphasizes interior decor and natural street visibility without evident reliance on electronic security measures, highlighting a security approach based primarily on unobstructed window views rather than camera coverage.",
#     "street_view": {
#       "vlm_insight": "In the image, there is one visible security camera mounted on the brick wall to the right of the entrance, positioned above eye level. This camera is likely aimed to cover the main entrance area and part of the sidewalk in front of the building, providing a view of people entering and exiting. The large windows above and beside the entrance offer good visibility for occupants inside to observe the street and sidewalk, enhancing natural surveillance. Overall, the combination of the camera placement and window coverage contributes to a reasonable level of visibility and security for the main street area.",
#       "url": "URL contains api key, can't be exposed"
#     },
#     "working_hours": [
#       "Monday: Closed",
#       "Tuesday: Closed",
#       "Wednesday: 10:00 AM – 4:00 PM",
#       "Thursday: 10:00 AM – 4:00 PM",
#       "Friday: 10:00 AM – 4:00 PM",
#       "Saturday: 10:00 AM – 4:00 PM",
#       "Sunday: 10:00 AM – 4:00 PM"
#     ]
#   },
#   {
#     "name": {
#       "original_name": "De Fer Coffee & Tea",
#       "translated_name": "By Fer Coffee & Tea"
#     },
#     "type": "cafe",
#     "website": "https://www.defer.coffee/",
#     "google_maps_url": "https://maps.google.com/?cid=7146824084755113796&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQABgEIAA",
#     "phone_number": "Phone number is not provided",
#     "address": "725 Penn Ave, Pittsburgh, PA 15222, USA",
#     "latitude": 40.443534,
#     "longitude": -79.999763,
#     "reviews_summary": "The coffee shop offers good quality coffee, though some customers found the sizes to be on the smaller side. The breakfast sandwiches, including vegetarian and bacon options, are highly praised for their taste and value, with excellent coffee and friendly staff enhancing the experience. While the coffee is consistently well-liked, one visitor noted a less-than-ideal customer service moment when staff informed them about closing and unavailable food in a somewhat inconsiderate manner. Overall, the shop is appreciated for its great coffee, tasty food options like the Chicken Pesto Wrap and Ham and Cheddar Hand Pie, and a welcoming atmosphere, making it a popular spot for both quick grabs and enjoyable visits.",
#     "reviews": [
#       {
#         "author_name": {
#           "original_name": "Zen",
#           "translated_name": "Zen"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sCi9DQUlRQUNvZENodHljRjlvT21WV1FXOUxUbXd5TUZGV2QxWnBNVmsyUzFOUE5GRRAB!2m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744",
#         "text": "We were so excited to finally try this place! It was good coffee but sizes were quite small. May come back to give the food a shot🤷🏻‍♀️",
#         "original_text": "We were so excited to finally try this place! It was good coffee but sizes were quite small. May come back to give the food a shot🤷🏻‍♀️",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/116752467943723065716/reviews",
#         "publish_date": "3 weeks ago",
#         "rating": 4
#       },
#       {
#         "author_name": {
#           "original_name": "Steve W",
#           "translated_name": "Steve W"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sCi9DQUlRQUNvZENodHljRjlvT2tSVlJWSTVRMk42Tm5WME5TMUlNRWhXVDFscWNFRRAB!2m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744",
#         "text": "The breakfast sandwich is something special. Whether you choose the vegetarian option or the bacon version it is well worth the price. The coffee is excellent and the staff is very friendly.\n\nWe were in Pittsburgh for two days and went there twice. Each time was great!",
#         "original_text": "The breakfast sandwich is something special. Whether you choose the vegetarian option or the bacon version it is well worth the price. The coffee is excellent and the staff is very friendly.\n\nWe were in Pittsburgh for two days and went there twice. Each time was great!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/114772964713332871063/reviews",
#         "publish_date": "2 weeks ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "Bridget Lynch",
#           "translated_name": "Bridget Lynch"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sCi9DQUlRQUNvZENodHljRjlvT2poTWMzaEtNMEUzUkhsVFVUWmtiSEJRTmxKYVowRRAB!2m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744",
#         "text": "We walked from Market Square area to the closest De Fer location.\nThe iced latte was great.\nThe greeting to let us know they were closing and there wasn’t food available because they turned the press off was inconsiderate. We weren’t even there for food. Not to mention that 4 others came in after us and that wasn’t said to them. We were there 30 minutes before they closed. Customer service should always be your top priority.\nThe cafe is small at the location we visited; we were in Pittsburgh for a wedding so we weren’t familiar with this area.\nAlthough our greeting was inappropriate, the coffee was great and I would recommend it.",
#         "original_text": "We walked from Market Square area to the closest De Fer location.\nThe iced latte was great.\nThe greeting to let us know they were closing and there wasn’t food available because they turned the press off was inconsiderate. We weren’t even there for food. Not to mention that 4 others came in after us and that wasn’t said to them. We were there 30 minutes before they closed. Customer service should always be your top priority.\nThe cafe is small at the location we visited; we were in Pittsburgh for a wedding so we weren’t familiar with this area.\nAlthough our greeting was inappropriate, the coffee was great and I would recommend it.",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/115774120871026748256/reviews",
#         "publish_date": "a week ago",
#         "rating": 4
#       },
#       {
#         "author_name": {
#           "original_name": "Michael Stevens",
#           "translated_name": "Michael Stevens"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChdDSUhNMG9nS0VJQ0FnTUR3OFpMZnBRRRAB!2m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744",
#         "text": "WOW! What a great shop, such an improvement from the outfit that was in the space previously.\n\nStaff is absolutely top notch, coffee is delicious and the food is awesome - very impressed by the balance of great quality served quickly.\n\nHighly recommend the Chicken Pesto Wrap and the Ham and Cheddar Hand Pie that forced me to write this review.\n\nHands down the best coffee shop downtown - you can just tell the staff and ownership are top notch!",
#         "original_text": "WOW! What a great shop, such an improvement from the outfit that was in the space previously.\n\nStaff is absolutely top notch, coffee is delicious and the food is awesome - very impressed by the balance of great quality served quickly.\n\nHighly recommend the Chicken Pesto Wrap and the Ham and Cheddar Hand Pie that forced me to write this review.\n\nHands down the best coffee shop downtown - you can just tell the staff and ownership are top notch!",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/109641860586849721305/reviews",
#         "publish_date": "3 months ago",
#         "rating": 5
#       },
#       {
#         "author_name": {
#           "original_name": "John Fesler",
#           "translated_name": "John Fesler"
#         },
#         "review_url": "https://www.google.com/maps/reviews/data=!4m6!14m5!1m4!2m3!1sChZDSUhNMG9nS0VJQ0FnTUR3MmVtMmNREAE!2m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744",
#         "text": "Nice little coffee tea shop great as a grab and go limited seating. Definitely good coffee and busy",
#         "original_text": "Nice little coffee tea shop great as a grab and go limited seating. Definitely good coffee and busy",
#         "original_language": "en",
#         "author_url": "https://www.google.com/maps/contrib/113511359315253918407/reviews",
#         "publish_date": "3 months ago",
#         "rating": 4
#       }
#     ],
#     "rating": "average: 4.4 out of 5 reviews",
#     "reviews_span": "latest date: 2025-07-03, most recent date: 2025-03-26, date difference: 99 days",
#     "url_to_all_photos": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipMeLjAeZl2iWMJFWilcRwGHItLBd-7oPSHpdUcK!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744",
#     "photos": [
#       {
#         "vlm_insight": "The image shows the interior of a café or tea shop, focusing on the counter area. There are no visible security cameras mounted on the walls or ceiling in the frame. Additionally, there are no windows overlooking the main street visible in this image, so visibility and security measures related to street monitoring cannot be assessed from this perspective. The focus is primarily on the service area and decorative elements.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipMeLjAeZl2iWMJFWilcRwGHItLBd-7oPSHpdUcK!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a table with various coffee drinks and a glass of iced beverage, but it does not provide any view or information about security cameras, windows, or a main street. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows overlooking the main street based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipNqgZrEQbEbIUikA9VzWocPlHzeysUKIpciVxIg!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of an espresso machine with coffee being brewed into a small measuring cup. There are no visible security cameras or windows overlooking a main street in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipNu98zcJwrDeOtbEM1XkLLWdI1NOJoHzJIy4X2m!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       },
#       {
#         "vlm_insight": "The image shows a close-up of a plastic cup filled with a red beverage and ice, placed on a blue and white checkered cloth. There are no visible security cameras or windows overlooking a main street in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipPx06QWifZFaDRA0o3cB-drX_3yfC4g2wUdwLHf!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       },
#       {
#         "vlm_insight": "The building has large windows on the ground floor facing the main street, providing good visibility into and out of the coffee shop, which enhances natural surveillance. There is one visible security camera mounted on the left side of the building near the corner, positioned to monitor the sidewalk and street area directly in front of the entrance. The camera placement appears strategic for covering the immediate vicinity of the entrance but may have limited coverage of the broader street or adjacent areas. Overall, the combination of large windows and at least one security camera contributes to decent visibility and security measures for this corner location.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIABIhC3scrZ5xOd2rNBmLnKy2yR!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       },
#       {
#         "vlm_insight": "The image shows the interior of a retail store with shelves displaying various products, but there are no visible security cameras or windows overlooking a main street in the frame. The walls and shelving units are fully stocked, and the store appears well-organized, but no security measures such as cameras or external windows can be assessed from this angle. To evaluate visibility and security coverage, an image showing the exterior or entrance area with cameras or windows would be needed.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgMDw2em2SQ!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       },
#       {
#         "vlm_insight": "The image shows a coffee cup on a marble table with a window in the background overlooking a street. There are no visible security cameras mounted on or near the window frame or street-facing area. The window provides clear visibility of the street outside, but no specific security measures such as cameras or alarms are evident in this view. Overall, the image does not provide enough information to assess the placement or coverage of security cameras for security purposes.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEMrR3-Dp1qeo4QE!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       },
#       {
#         "vlm_insight": "The image shows a festive cup of whipped cream-topped hot chocolate with holiday sprinkles, a candy cane, and sugar cubes on a blue surface. There are no visible security cameras, windows, or street views in this image. Therefore, it is not possible to analyze the placement and coverage of security cameras or windows overlooking a main street based on this photo.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipPnvEkT-R1qXyr65E_CEuj0vd_ynUTRNjusksba!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       },
#       {
#         "vlm_insight": "The image shows an indoor setting with a wall, a piece of artwork, a hanging light, and some items on a shelf, but there are no visible security cameras or windows overlooking a street. Therefore, it is not possible to assess the placement or coverage of security cameras or windows for visibility and security measures based on this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipOjCIUlDDEI9YquCaczLIViEpFqrbsHq7mZX7I2!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       },
#       {
#         "vlm_insight": "The image does not show any security cameras, windows, or a main street. It depicts a close-up of a drink with ice cubes on a blue surface, surrounded by dried citrus slices, sugar cubes, a cup with star-shaped cookies, and a bottle of milk. Therefore, no analysis of security camera placement or window coverage can be made from this image.",
#         "url": "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sAF1QipOUgih_E38UtWWDU8wVGuHaXwF8C2fXgfLDYaav!2e10!4m2!3m1!1s0x8834f1bd41fe2bdf:0x632e9ea3bc08e744"
#       }
#     ],
#     "prompt_used": "\"Analyze the placement and coverage of security cameras and windows overlooking the main street to assess visibility and security measures.\"",
#     "photos_summary": "The images collectively depict various interior scenes of cafés and retail spaces, focusing on beverage presentations such as coffee drinks, iced beverages, and festive hot chocolate, often set against decorative or cozy backgrounds like marble tables, checkered cloths, or shelves with products and artwork. While most interiors lack visible security cameras or windows overlooking a main street, one building exterior features large street-facing windows and a strategically placed security camera monitoring the entrance and sidewalk, enhancing natural surveillance. Overall, the key themes emphasize café ambiance and drink aesthetics, with limited but notable attention to exterior visibility and security measures at one corner location.",
#     "street_view": {
#       "vlm_insight": "The image shows a section of a building facade with two windows overlooking the street. There are no visible security cameras mounted on or near the windows or the wall. The windows provide some natural visibility to the street, but the coverage is limited to the immediate area directly in front of the building. Overall, security measures in terms of camera surveillance appear to be lacking in this view.",
#       "url": "URL contains api key, can't be exposed"
#     },
#     "working_hours": [
#       "Monday: 7:00 AM – 4:00 PM",
#       "Tuesday: 7:00 AM – 4:00 PM",
#       "Wednesday: 7:00 AM – 4:00 PM",
#       "Thursday: 7:00 AM – 4:00 PM",
#       "Friday: 7:00 AM – 4:00 PM",
#       "Saturday: 8:00 AM – 4:00 PM",
#       "Sunday: 8:00 AM – 4:00 PM"
#     ]
#   }
# ]


# # Example 2: A query about a specific offering
# user_prompt_2 = "big windows, no security cameras"
# ranked_results_2 = rank_live_results_granularly(live_api_data, user_prompt_2)
# print(ranked_results_2)
