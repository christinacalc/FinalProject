from __future__ import print_function
import sqlite3
import httplib2
import os
import facebook
import requests
from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import json
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = "https://www.googleapis.com/auth/drive.metadata.readonly"
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Final Project'


googlecache_file = "googlecache.json"
# Put the rest of your caching setup here:
try:
    cache_file = open(googlecache_file,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

def get_credentials(): #the following code was modified from https://developers.google.com/gmail/api/quickstart/python
    home_dir = os.path.expanduser('~') #under 'quickstart.py'
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http, cache_discovery = True, cache = None) #confused whether or not this is caching here

    results = service.files().list(
        pageSize=100,fields="nextPageToken, files(id, name, createdTime)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
        return None
    else:
        # print('Files:')
        # for item in items:
        #     print('Name:{0}\n\nId:{1}\n\nDate created:{2}\n\n\n'.format(item['name'], item['id'], item['createdTime']))
        return items

def get_google_data():
    if len(CACHE_DICTION) == 100: #checking to see if the cache file is 100 documents exactly, if so, use cache, if not call API. 
        print("Using Google cache\n")
        return CACHE_DICTION
    else:
        x= main()
        with open(googlecache_file, 'w') as cache_file:
            json.dump(x, cache_file)
        print("Fetching. . . \n")
        return x


googledata = get_google_data()


conn= sqlite3.connect("FinalProject.sqlite") #establishing DB connection
cur= conn.cursor() #opening cursor 


cur.execute('DROP TABLE IF EXISTS Google')
cur.execute('CREATE TABLE Google (file_name TEXT, file_id TEXT, date_created TIMESTAMP)') #creating users table with 3 columns 

for item in googledata:
    googletup= item["name"], item['id'], item['createdTime']
    cur.execute('INSERT INTO Google (file_name, file_id, date_created) VALUES (?,?,?)', googletup)

conn.commit() #commit changes to the DB
#- - - - - - - - - - - - - - - - - END GOOGLE DATA/START FACEBOOK DATA- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

facebookcache_file = "fbcache.json"
# Put the rest of your caching setup here:
try:
    fbcache_file = open(facebookcache_file,'r')
    fbcache_contents = fbcache_file.read()
    fbcache_file.close()
    FBCACHE_DICTION = json.loads(fbcache_contents)
except:
    FBCACHE_DICTION = {}

def CacheFacebook(baseurl, url_params):
    BASE_URL = baseurl
    p_diction = url_params
    full_url = requestURL(BASE_URL, p_diction)

    if full_url in FBCACHE_DICTION:
        print('Using Facebook cache')
        # use stored response
        response_text = FBCACHE_DICTION[full_url]
    else:
        print('fetching')
        # do the work of calling the API
        response = requests.get(full_url)
        #store the response

        FBCACHE_DICTION[full_url] = response.text
        response_text = response.text

        fbcache_file = open(facebookcache_file, 'w')
        fbcache_file.write(json.dumps(FBCACHE_DICTION))
        fbcache_file.close()
    return response_text

def canonical_order(d):
    alphabetized_keys = sorted(d.keys())
    res = []
    for k in alphabetized_keys:
        res.append((k, d[k]))
    return res

def requestURL(baseurl, params = {}):
    req = requests.Request(method = 'GET', url = baseurl, params = canonical_order(params))
    prepped = req.prepare()
    return prepped.url


access_token = "EAAXPPlAm9IYBANklbFpUmALFW7S7oii4HhRSZBKmZBU8UyN88vmvdzW7nbl63bXjnwbV2ZA532FuIhvBZAJGdXhjjf9E2E7eCM7bd43fEFs3YNxoWqmECQ3LiJmB8uY0WDantWQTXBd46IvG88vrFYzZCfCZBvBDoXKNFZBTOd5RAZDZD"

# url_params= {}
# baseurl= "https://graph.facebook.com/v2.7/me?"
# #url_params["access_token"]= access_token
# url_params["fields"]= "id, name, posts.limit(100){story, created_time}"

graph = facebook.GraphAPI(access_token=access_token, version="2.7")


posts = graph.get_object(ids= 1273394489352675 , fields="feed")

for post in posts:
    print(post['created_time']) #THIS IS IN NO WAY FINISHED PLEASE COME BACK TO LATER!!!!!!!!!

#CacheFacebook(baseurl, url_params)









cur.close() #always close the cursor when you're finished using it!

