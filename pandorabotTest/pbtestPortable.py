import pbPortableAPI as API

# Pandora bots python SDK
# https://github.com/pandorabots/pb-python
# https://developer.pandorabots.com/docs#!/pandorabots_api_swagger_1_3
host = 'aiaas.pandorabots.com'
user_key = "be2e0c5765ab1c91b2b50be0bc694cda"
app_id = "1409616768402"
botname = "alice"
session_id = False


def testChat():
    global session_id

    print "testing chat connection"

    result = API.talk(user_key, app_id, host, botname, "test", session_id, recent=True)
    session_id = result['sessionid']

    print "Response:" , result['response']

# send an API call to pandora bots
def talk(input_text):
    result = API.talk(user_key, app_id, host, botname, input_text, session_id, recent=True)
    print result['response']

    # result = API.debug_bot(user_key, app_id, host, botname, input_text, session_id, reset=False, trace=True, recent=True)
    # print result['trace']

    return result['response']

testChat()

# Hello, my name is Alice. What is your name?
talk("Hello my name is Beata")
