import re
import datetime


import boto3
import dateutil.parser
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
available_locations = ['manhattan']
available_cuisine = ['french', 'chinese', 'japanese', 'italian', 'spanish', 'indian', 'mexican']


# --- Helpers that build all of the responses ---
def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']


def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None


def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']

    return {}


def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


# --- Helper Functions ---
def isvalid_email(s):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.match(pat,s):
        return True
    else:
        return False


def isvalid_int(num):
    try:
        int(num)
        return True
    except ValueError:
        return False


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        # if date.lower() == "today" or date.lower() == "tomorrow" or date.lower() == "the day after tomorrow":
        #     return True
        return False


def isvalid_time(time):
    try:
        dateutil.parser.parse(time).time()
        return True
    except ValueError:
        return False


def validate_slots(slots):
    # Validate location
    if not slots['dinningLocation']:
        return {
            'isValid': False,
            'invalidSlot': 'dinningLocation'
        }

    if slots['dinningLocation']['value']['originalValue'].lower() not in available_locations:
        return {
            'isValid': False,
            'invalidSlot': 'dinningLocation',
            'message': 'Sorry! Please enter Manhattan.'
        }

    # Validate cuisine
    if not slots['dinningCuisine']:
        return {
            'isValid': False,
            'invalidSlot': 'dinningCuisine'
        }

    if slots['dinningCuisine']['value']['originalValue'].lower() not in available_cuisine:
        return {
            'isValid': False,
            'invalidSlot': 'dinningCuisine',
            'message': 'Sorry! Please choose from French, Chinese, Japanese, Italian, Spanish, Indian or Mexican.'
        }

    # Validate date
    if not slots['dinningDate']:
        return {
            'isValid': False,
            'invalidSlot': 'dinningDate'
        }

    if not isvalid_date(slots['dinningDate']['value']['originalValue']):
        return {
            'isValid': False,
            'invalidSlot': 'dinningDate',
            'message': 'Sorry! Please re-enter the date.'
        }

    today = datetime.date.today()
    if slots['dinningDate']['value']['originalValue'].lower() != "today" and slots['dinningDate']['value']['originalValue'].lower() != "tomorrow" and slots['dinningDate']['value']['originalValue'].lower() != "the day after tomorrow":
        if dateutil.parser.parse(slots['dinningDate']['value']['originalValue']).date() < today:
            return {
                'isValid': False,
                'invalidSlot': 'dinningDate',
                'message': 'Sorry! Please re-enter the date. The date should be no earlier than today.'
            }

    # Validate time
    if not slots['dinningTime']:
        return {
            'isValid': False,
            'invalidSlot': 'dinningTime'
        }

    if not isvalid_date(slots['dinningTime']['value']['originalValue']):
        return {
            'isValid': False,
            'invalidSlot': 'dinningTime',
            'message': 'Sorry! Please re-enter the time.'
        }

    now = datetime.datetime.now().strftime("%H:%M")
    # if slots['dinningDate']['value']['originalValue'].lower() == "today" and dateutil.parser.parse(slots['dinningTime']['value']['originalValue']).time().strftime("%H:%M") < now:
    #     return {
    #         'isValid': False,
    #         'invalidSlot': 'dinningDate',
    #         'message': 'Sorry! Please re-enter the time. The time should be no earlier than now.'
    #     }

    # if slots['dinningDate']['value']['originalValue'].lower() != "today" and slots['dinningDate']['value']['originalValue'].lower() != "tomorrow" and slots['dinningDate']['value']['originalValue'].lower() != "the day after tomorrow":
    if dateutil.parser.parse(slots['dinningDate']['value']['originalValue']).date() == today and dateutil.parser.parse(slots['dinningTime']['value']['originalValue']).time().strftime("%H:%M") < now:
        return {
            'isValid': False,
            'invalidSlot': 'dinningDate',
            'message': 'Sorry! Please re-enter the time. The time should be no earlier than now.'
        }

    # Validate people
    if not slots['dinningPeople']:
        return {
            'isValid': False,
            'invalidSlot': 'dinningPeople'
        }

    if not isvalid_int(slots['dinningPeople']['value']['originalValue']):
        return {
            'isValid': False,
            'invalidSlot': 'dinningPeople',
            'message': 'Sorry! Please re-enter the number of people in your group.'
        }

    # Validate email
    if not slots['dinningEmail']:
        return {
            'isValid': False,
            'invalidSlot': 'dinningEmail'
        }

    if not isvalid_email(slots['dinningEmail']['value']['originalValue']):
        return {
            'isValid': False,
            'invalidSlot': 'dinningEmail',
            'message': 'Sorry! Please enter a valid email address.'
        }

    # Valid Order
    return {'isValid': True}


# --- Functions that control the bot's behavior ---
def suggest(intent_request):
    intent = intent_request['sessionState']['intent']['name']
    slots = get_slots(intent_request)

    # validate slots
    order_validation_result = validate_slots(slots)
    if intent_request['invocationSource'] == 'DialogCodeHook':
        if not order_validation_result['isValid']:
            if 'message' in order_validation_result:
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": order_validation_result['invalidSlot'],
                            "type": "ElicitSlot"
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": order_validation_result['message']
                        }
                    ]
                }
            else:
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "slotToElicit": order_validation_result['invalidSlot'],
                            "type": "ElicitSlot"
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots
                        }
                    }
                }
        else:
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Delegate"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots
                    }
                }
            }

    if intent_request['invocationSource'] == 'FulfillmentCodeHook':
        location = get_slot(intent_request, 'dinningLocation')
        cuisine = get_slot(intent_request, 'dinningCuisine')
        dinningDate = get_slot(intent_request, 'dinningDate')
        dinningTime = get_slot(intent_request, 'dinningTime')
        people = get_slot(intent_request, 'dinningPeople')
        email = get_slot(intent_request, 'dinningEmail')

        # push the information collected from the user to sqs
        text = location + "+" + cuisine + "+" + dinningDate + "+" + dinningTime + "+" + people + "+" + email
        sqs = boto3.client('sqs')
        sqs.send_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/472151504206/collectedInfo",
            MessageBody=text
        )

        response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    "name": intent,
                    "slots": slots,
                    "state": "Fulfilled"
                }

            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": "Your request has been received and you will be notified over email."
                }
            ]
        }

    return response


def greet(intent_request):
    session_attributes = get_session_attributes(intent_request)
    text = "Hello there! What can I help you with today?"
    message = {
        'contentType': 'PlainText',
        'content': text
    }
    fulfillment_state = "Fulfilled"
    return close(intent_request, session_attributes, fulfillment_state, message)


def thank(intent_request):
    session_attributes = get_session_attributes(intent_request)
    text = "No problem!"
    message = {
        'contentType': 'PlainText',
        'content': text
    }
    fulfillment_state = "Fulfilled"
    return close(intent_request, session_attributes, fulfillment_state, message)


# --- Intents ---
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    intent_name = intent_request['sessionState']['intent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return greet(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return suggest(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    return dispatch(event)
