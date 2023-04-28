# Dining Concierge Assistant

S3 frontend URL:
----
https://s3.amazonaws.com/cs6998chatbot.com/chat.html

Directory:
----
- README.pdf
- Frontend
- Lambda Functions
  - LF0.py
  - LF1.py
  - LF2.py
- YAML
  - AI Customer Service API-test-stage-swagger.yaml
- Yelp scraper
  - get_yelp_data.py: functions as the Yelp scraper, generates yelp_data.csv file
  - DynamoDBLF.py: sends data in yelp_data.csv to DynamoDB
  - OpenSearch_data.py: converts data in yelp_data.csv to match the format for ElasticSearch, generates yelp_data.json file
  - step2_upload.txt: upload yelp_data.json to ElasticSearch
  - yelp_data.csv
  - yelp_data.json
 
Architecture：
----
<img width="602" alt="Screenshot 2023-02-07 at 3 21 54 PM" src="https://user-images.githubusercontent.com/123121874/235216310-6d4c32ef-568d-4123-afc7-7b100007b23c.png">
