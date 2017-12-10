from pb_py import main as API
import os

# Pandora bots python SDK
# https://github.com/pandorabots/pb-python
# https://developer.pandorabots.com/docs#!/pandorabots_api_swagger_1_3
host = 'aiaas.pandorabots.com'
user_key = "be2e0c5765ab1c91b2b50be0bc694cda"
app_id = "1409616768402"
botname = "alice"
session_id = False

# get files of alice
def getFiles():
    print API.list_files(user_key, app_id, host, botname)

# upload AIML files etc to alice
def uploadFiles():
    path = "/home/tjalling/Downloads/robotlabnao"
    for f in os.listdir(path):
        filename = path + "/" + f
        result = API.upload_file(user_key, app_id, host, botname, filename)
        print result

def reset():
    API.debug_bot(user_key, app_id, host, botname, input_text, session_id, reset=True, recent=True)

# send an API call to pandora bots
def talk(input_text):
    global session_id

    # result = API.talk(user_key, app_id, host, botname, input_text, session_id, recent=True)
    result = API.debug_bot(user_key, app_id, host, botname, input_text, session_id, reset=False, trace=True, recent=True)
    print result['response']

    print result['trace']

    if not session_id:
        session_id = result['sessionid']

    return result['response']


uploadFiles()
getFiles()

# talk("Hello my name is Beata")
# Hello, my name is Alice. What is your name?
