import boto3
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection

REGION = 'us-east-1'
HOST = 'search-restaurants-4ktblvmo6acuagteij2h6ks26u.us-east-1.es.amazonaws.com'
INDEX = 'restaurants'


def query(term):
    q = {'size': 3, 'query': {'multi_match': {'query': term}}}

    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)

    res = client.search(index=INDEX, body=q)

    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_id'])

    return results


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)


def lookup_data(key, db=None, table='yelp-restaurants'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.get_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        print(response['Item'])
        return response['Item']


def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    ses = boto3.client('ses')

    queues = sqs.list_queues(QueueNamePrefix='collectedInfo')
    request_queue_url = queues['QueueUrls'][0]

    # pulls a message from the sqs queue
    response = sqs.receive_message(
        QueueUrl=request_queue_url,
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=10,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=30,
        WaitTimeSeconds=0
    )

    if 'Messages' in response:
        for message in response['Messages']:
            print(str(message['Body']).split('+'))
            location, cuisine, dinningDate, dinningTime, people, email = str(message['Body']).split('+')
            sqs.delete_message(QueueUrl=request_queue_url, ReceiptHandle=message['ReceiptHandle'])

            # get a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch
            results = query(cuisine)
            print(results)

            # send businessID to DynamoDB for more info
            recommendations = []
            for res in results:
                recommendation = lookup_data({'businessID': res})
                recommendations.append(recommendation)

            # send via email
            message = 'Hello! Here are my ' + cuisine + ' restaurant suggestions for ' + str(
                people) + ' for ' + dinningDate + ' at ' + dinningTime + '\n'
            i = 1
            for recommendation in recommendations:
                message += str(i) + '. ' + recommendation['name'] + ', located at ' + recommendation[
                    'address'] + '\n'
                i += 1

            try:
                response = ses.send_email(
                    Destination={
                        'ToAddresses': [
                            email,
                        ],
                    },
                    Message={
                        'Body': {
                            'Text': {
                                'Charset': "UTF-8",
                                'Data': message,
                            },
                        },
                        'Subject': {
                            'Charset': "UTF-8",
                            'Data': 'Dining Concierge Assistant: Restaurant Suggestions',
                        },
                    },
                    Source='kylieshen00@gmail.com'
                )
            except ClientError as e:
                print(e.response['Error']['Message'])
            else:
                print("Email sent."),
                print(response['MessageId'])

