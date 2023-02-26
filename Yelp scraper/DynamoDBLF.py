import boto3
from datetime import datetime
import csv


def lambda_handler(event, context):
    db = boto3.resource('dynamodb', region_name='us-east-1')
    table = db.Table("yelp-restaurants")

    with open('yelp_data.csv', newline='') as f:
        reader = csv.reader(f)
        restaurants = list(reader)

    for restaurant in restaurants:
        table.put_item(
            Item={
                'businessID': restaurant[0],
                'name': restaurant[1],
                'cuisine': restaurant[2],
                'address': restaurant[3],
                'coordinates': ((restaurant[4], restaurant[5])),
                'numberOfReviews': restaurant[7],
                'rating': str(restaurant[6]),
                'zipCode': restaurant[8],
                'insertedAtTimestamp': str(datetime.now())
            }
        )
