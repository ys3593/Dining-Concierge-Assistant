# Assignment 1: Dining-Concierge-Assistant

Done by: Yaochen Shen

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


