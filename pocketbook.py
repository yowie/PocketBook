import json
import requests
import yagmail
import ebooklib
from ebooklib import epub


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
    global pocket_conf
    global kindle_conf
    with open('config.json') as config_file:
        pocket_conf = json.load(config_file)
    
    with open('kindleconfig.json') as config_file:
        kindle_conf = json.load(config_file)

    
def do_save_config():
    with open('config.json', 'w') as outfile:
        json.dump(pocket_conf, outfile)


def do_create_epub():
    book = epub.EpubBook()

    # set metadata
    book.set_identifier('id123456')
    book.set_title('Sample book')
    book.set_language('en')

    book.add_author('Author Authorowski')
    book.add_author('Danko Bananko', file_as='Gospodin Danko Bananko', role='ill', uid='coauthor')

    # create chapter
    c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='hr')
    c1.content=u'<h1>Intro heading</h1><p>Zaba je skocila u baru.</p>'

    # add chapter
    book.add_item(c1)

    # define Table Of Contents
    book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
                (epub.Section('Simple book'),
                (c1, ))
                )

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

    # add CSS file
    book.add_item(nav_css)

    # basic spine
    book.spine = ['nav', c1]

    # write to the file
    epub.write_epub('test.epub', book, {})

def do_send_to_kindle():

yag = yagmail.SMTP('pocketbookindle@gmail.com')
contents = [
    "This is the body, and here is just text http://somedomain/image.png",
    "You can find an audio file attached.", 'test.epub'
]
yag.send(kindle_conf['email'], 'subject', contents)


do_load_config()
if not 'access_token' in pocket_conf:
    account_info = get_request_token()
    do_auth_redirect()
    do_convert_auth_token()
do_get_articles()
do_create_epub()
#do_send_to_kindle()
