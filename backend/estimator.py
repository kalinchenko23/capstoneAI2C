def cost_time_predict(places:int):
    results={
    "basic_time":"couple of seconds",
    "basic_cost":round(0.04*places,2),
    "reviews_time":round(2*places/60,2),
    "reviews_cost":round(0.2*places,2),
    "photos_time":round(34*places/60,2),
    "photos_cost":round(0.4*places,2),
    "time_everything":round(44*places/60,2),
    "cost_everything":round(0.52*places,2)
    }
    return results
