import boto3

# When the API receives a request, you should
# 1. extract the text message from the API request: msg_from_user = event['messages'][0]
# 2. send it to your Lex chatbot: response
# 3. wait for the response: msg_from_lex
# 4. send back the response from Lex as the API response.
# Define the client to interact with Lex
client = boto3.client('lexv2-runtime')


def lambda_handler(event, context):
    msg_from_user = event['messages'][0]['unstructured']['text']

    # change this to the message that user submits on 
    # your website using the 'event' variable
    # msg_from_user = "Hello"

    print(f"Message from frontend: {msg_from_user}")

    # Initiate conversation with Lex
    response = client.recognize_text(
        botId='XAGJV8QOYI',  # MODIFY HERE
        botAliasId='3OHFW6MB5N',  # MODIFY HERE
        localeId='en_US',
        sessionId='testuser',
        text=msg_from_user)

    msg_from_lex = response.get('messages', [])
    if msg_from_lex:
        print(f"Message from Chatbot: {msg_from_lex[0]['content']}")
        print(response)

        # modify resp to send back the next question Lex would ask from the user
        # format resp in a way that is understood by the frontend
        # HINT: refer to function insertMessage() in chat.js that you uploaded
        # to the S3 bucket
        resp = {
            'statusCode': 200,
            'messages': [{
                'type': 'unstructured',
                'unstructured': {
                    'text': msg_from_lex[0]['content']
                }
            }]
        }

        return resp
