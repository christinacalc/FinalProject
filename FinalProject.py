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
import datetime,time 
import calendar


def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

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

def GetDOW(datelist):
    weekdays= {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    DOW= []
    for each in datelist:
        (year, month, day)= int(each[0]), int(each[1]), int(each[2])
        x= calendar.weekday(year, month, day)
        if x in weekdays.keys():
            DOW.append(weekdays[x])
    return DOW

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

googleDates= []
for each in googledata:
    date= each["createdTime"]
    newdate= date.split("T")
    newerdate= newdate[0].split("-")
    googleDates.append(newerdate)

conn= sqlite3.connect("FinalProject.sqlite") #establishing DB connection
cur= conn.cursor() #opening cursor 


cur.execute('DROP TABLE IF EXISTS Google')
cur.execute('CREATE TABLE Google (file_name TEXT, file_id TEXT, date_created TIMESTAMP, weekday TEXT)') #creating users table with 3 columns 

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
        print(type(response_text))
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


access_token = "EAAXPPlAm9IYBAFcmHjaR1vRv6qhBTOA9lvUjwOUGMbMkcONQfCLiM3Upp19h1MZBzO2Wptoa9pBfbqcd43sbZCZAhtEJxlAQzbqgZAgRwgQNT3U9x73tinMNwxRRYETMW96YHWPnUjglvOvlPxkoWFnVzJZBiPwBQusf1Rw4vZBgZDZD"

url_params= {}
baseurl= "https://graph.facebook.com/v2.7/me/feed"
url_params["limit"]= 100
url_params["access_token"]= access_token

f= CacheFacebook(baseurl, url_params)
fb= json.loads(f)
fbdata= fb["data"]

FBDates= []
zipdatafb= []
for each in fbdata:
    date= each["created_time"]
    zipdatafb.append(date)
    newdate= date.split("T")
    newerdate= newdate[0].split("-")
    FBDates.append(newerdate)

FBDOW = GetDOW(FBDates)

cur.execute('DROP TABLE IF EXISTS Facebook')
cur.execute('CREATE TABLE Facebook (story TEXT, id TEXT, date_created TIMESTAMP)') #creating users table with 3 columns 

for item in fbdata:
    if "story" in item.keys():
        x = item["story"]
    else:
        x= "null"
    fbtup= x, item['id'], item['created_time'], 
    cur.execute('INSERT INTO Facebook (story, id, date_created) VALUES (?,?,?)', fbtup)

cur.execute('DROP TABLE IF EXISTS Facebook_Dates')
cur.execute('CREATE TABLE Facebook_Dates (numerical_date TEXT, week_day TEXT)')


fbdowtup= zip(zipdatafb, FBDOW)

for each in fbdowtup:
    print(each)
    cur.execute('INSERT INTO Facebook_Dates (numerical_date, week_day) VALUES (?,?)', each)
    

conn.commit() #commit changes to the DB
#- - - - - - - - - - - - - - - - - - - - - -  -END FACEBOOK DATA START ORGANIZING BY TIME- - - - - - - - - - - - - - - - - - - - - - - - - 




cur.close() #always close the cursor when you're finished using it!

