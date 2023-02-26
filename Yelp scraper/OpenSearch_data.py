import csv
import json
import os

with open('yelp_data.csv', newline='') as f:
    reader = csv.reader(f)
    restaurants = list(reader)

    # covert to json
    for restaurant in restaurants:
        with open("./yelp_data.txt", "a", encoding='utf-8') as f:
            json.dump(json.loads('{"index": {"_index": "restaurants", "_id": "' + str(restaurant[0]) + '"}}'), f,
                      ensure_ascii=False)
            f.write("\n")
            json.dump(json.loads('{"cuisine": "' + str(restaurant[2]) + '"}'), f,
                      ensure_ascii=False)
            f.write("\n")

os.rename("./yelp_data.txt", "./yelp_data.json")







