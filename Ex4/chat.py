import pbPortableAPI as API

# Pandora bots python SDK
# https://github.com/pandorabots/pb-python
# https://developer.pandorabots.com/docs#!/pandorabots_api_swagger_1_3
host = 'aiaas.pandorabots.com'
user_key = "be2e0c5765ab1c91b2b50be0bc694cda"
app_id = "1409616768402"
botname = "alice"
session_id = False

# Send a test message to the Pandora chatbot to test the connection
def test():
    global session_id

    print "Testing chat connection"

    result = API.talk(user_key, app_id, host, botname, "test alice", session_id, recent=True)
    session_id = result['sessionid']

    print "Chat test response:" , result['response']


# send an API call to pandora bots
def talk(input_text):
    result = API.talk(user_key, app_id, host, botname, input_text, session_id, recent=True)
    print result['response']

    return result['response']

# return the trace of the response, for debugging
def trace(input_text):
    result = API.debug_bot(user_key, app_id, host, botname, input_text, session_id, reset=False, trace=True, recent=True)
    print result['trace']
    return result['trace']
