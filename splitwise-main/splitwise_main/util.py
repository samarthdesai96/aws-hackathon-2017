import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from splitwise_main.expense_manager import SplitwiseOAuthManager


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

'''
def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message,
	    "responseCard": {
      	        "version": 1,
                "contentType": "application/vnd.amazonaws.card.generic",
                "genericAttachments": [
                {
                    "title":"Splitwise OAuth initiation",
                    "subTitle":"Use below url to initiate Splitwise authorization",
                    "imageUrl": "https://s3.amazonaws.com/lex-box/ice-tea.jpeg",
                    "attachmentLinkUrl": "https://s3.amazonaws.com/lex-box/ice-tea.html",
                    "buttons":[ 
                    {
                       "text":"click on this url ",
                       "value":"intent_name"
                    }
                    ] 
                 } 
               ] 
            }
      }
    }
    
'''

def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }

def initiate_oauth(userId):
    sauth = SplitwiseOAuthManager(userId)
    auth_url = sauth.request_authorized_url()
    oauth_msg = {'contentType': 'PlainText',
                 'content': "I can't access your splitwise account yet. \r "
                            "Please authorize me using this url {}\r\r\r "
                            "Have you finished login? ".format(auth_url)}
    return oauth_msg

def get_token_from_db(userId):
    logger.info('Getting token from db for user %s' %userId)
    sauth = SplitwiseOAuthManager(userId)
    return sauth.get_access_token()

def login_attempts(intent, first=True):
    if first:
	intent['sessionAttributes']['login_attempts'] = 1
	return 1
    else:
        attmp = intent['sessionAttributes']['login_attempts'] 
    	attmp = int(attmp) + 1
        intent['sessionAttributes']['login_attempts'] = attmp
	return attmp

def is_logged_in(userid, intent):
    # here goto dynamodb to see if token is present
    token = None
    attemtps = 0 
    if intent['sessionAttributes']:
        logger.info("session attrs are not empty")
        token = intent['sessionAttributes'].get('access_token', None)
        if not token:
            token = get_token_from_db(userid)
            intent['sessionAttributes']['access_token'] = str(token) if token else None
	attempts = login_attempts(intent, first=False)
    else:
        logger.info("session attrs are empty")
        token = get_token_from_db(userid)
        token = str(token) if token else None
        intent['sessionAttributes'] = { 'access_token' : token }
	attempts = login_attempts(intent, first=True)
    return token, attempts

'''
def prompt_for_login(intent):
    if not is_logged_in(intent['userId'], intent):
	
        logger.info('Token is not present. Now asking for login confirmation with %s' % intent)
        return confirm_intent(intent['sessionAttributes'],
                              intent['currentIntent']['name'],
                              get_slots(intent),
                              initiate_oauth(intent['userId']))
    return None
'''

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

