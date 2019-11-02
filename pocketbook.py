import json
import requests

api_base_url = "https://getpocket.com/v3/get"
api_auth_url = "https://getpocket.com/v3/oauth/request"
api_authorize_url = "https://getpocket.com/v3/oauth/authorize"
api_get_url = "https://getpocket.com/v3/get"


api_headers = {'Content-Type': 'application/json', 'X-Accept': 'application/json'}

def get_request_token():
    response = requests.post(url = api_auth_url, headers=api_headers, json={"consumer_key": pocket_conf['api_consumer_key'], "redirect_uri": "https://www.google.com"})
    pocket_conf['request_token'] = json.loads(response.content.decode('utf-8'))['code']
    do_save_config()

def do_auth_redirect():
    #When the user taps a "Login" or "connect with Pocket" button in your application, you should present some UI to indicate that your application is preparing to login and make a request to obtain a request token from Pocket.
    print ("go to: https://getpocket.com/auth/authorize?request_token="+pocket_conf['request_token'] + "&redirect_uri=")
    input("press enter once authorised")

def do_convert_auth_token():
    response = requests.post(url = api_authorize_url, headers=api_headers, json={"consumer_key": pocket_conf['api_consumer_key'],"code": pocket_conf['request_token']})
    #should be a 200 OK

    data = json.loads(response.content.decode('utf-8'))
    pocket_conf['username'] = data['username']
    pocket_conf['access_token'] = data['access_token']
    do_save_config()

def do_get_articles():
    count = 3
    sort = "newest"
    detailtype = "complete"
    response = requests.post(url = api_get_url, headers=api_headers, json={"consumer_key": pocket_conf['api_consumer_key'],"access_token": pocket_conf['access_token'], "count": count, "sort": sort, "detailtype": detailtype})
    #should be a 200 OK
   
    data = json.loads(response.content.decode('utf-8'))
    print(data)

def do_load_config():
    with open('config.json') as config_file:
        data = json.load(config_file)
    return data
    
def do_save_config():
    with open('config.json', 'w') as outfile:
        json.dump(pocket_conf, outfile)


pocket_conf = do_load_config()
if not 'access_token' in pocket_conf:
    account_info = get_request_token()
    do_auth_redirect()
    do_convert_auth_token()
do_get_articles()
#test line
