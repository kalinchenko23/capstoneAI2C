def cost_time_predict(places:int):
    """
    Predicts estimated time and cost based on the number of places.

    Calculates the estimated time (in seconds) and cost (in dollars)
    for performing operations related to a given number of places,
    breaking down the estimates by operation type (basic, reviews, photos)
    and providing a total."""

    results={
    "places": places,
    "basic_time":5,
    "basic_cost":0,
    "reviews_time":2*places,
    "reviews_cost":round(0.02*places,2),
    "photos_time": 34*places,
    "photos_cost":round(0.2*places,2),
    "time_everything":5+36*places,
    "cost_everything":round(0.22*places,2)
    }
    return results
