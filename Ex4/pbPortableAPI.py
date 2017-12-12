# portable API for Pandora bots

import requests

host_base = "https://"


def talk(user_key, app_id, host, botname, input_text, session_id=False, recent=False, reset=False, trace=False, clientID=False):
    path = '/talk/' + app_id + '/' + botname
    url = host_base + host + path
    query = {"user_key": user_key,
             "input": input_text
             }
    if recent:
        query['recent'] = recent
    if session_id:
        query['sessionid'] = session_id
    if reset:
        query['reset'] = reset
    if trace:
        query['trace'] = trace
    if clientID:
        query['client_name'] = clientID
    response = requests.post(url, params=query)
    result = response.json()
    status = result['status']
    output = {}
    if status == 'ok':
        output["response"] =  result['responses'][0]
        if reset:
            output["output"] = 'Bot has been reset.'
        if trace:
            trace_text = result['trace']
            trace_string = 'Trace: '
            for elt in trace_text:
                if 'status' in elt.keys():
                    trace_string +='Level: ' + str(elt['level'])
                    trace_string += ' Sentence to process: ' + ' '.join(elt['input']) + ' '
                    trace_string += 'Matched pattern: ' + str(elt['matched'][0])
                    trace_string += ' from file: ' + elt['filename']
                    trace_string += ' template: ' + elt['template'] + '\n'
            output["trace"] = trace_string
        if 'sessionid'  in result:
            output["sessionid"] = result['sessionid']
    else:
        output["response"] = result['message']
    return output


def debug_bot(user_key, app_id, host, botname, input_text, session_id='', recent=False, reset=False, trace=False):
    response = talk(user_key, app_id, host, botname, input_text, session_id, recent, reset, trace)
    return response
