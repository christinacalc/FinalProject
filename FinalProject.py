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
import plotly
import plotly.plotly as py
import plotly.graph_objs as go


plotly.tools.set_credentials_file(username='christinacalc', api_key="A5fuT8ipXqStpZArcT97")

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = "https://www.googleapis.com/auth/drive.metadata.readonly"
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Final Project'


googlecache_file = "googlecache.json" #google cache file

try:
    cache_file = open(googlecache_file,'r') #google cache pattern
    cache_contents = cache_file.read() 
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

def GetDOW(datelist): #function that takes a list of strings (dates) as input
    weekdays= {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"} #number corresponds to output from weekday method
    DOW= [] #created a list of days of the week for each of the
    for each in datelist: #iterating through the datelist
        (year, month, day)= int(each[0]), int(each[1]), int(each[2]) #creating tuple that will be used in the weekday method
        x= calendar.weekday(year, month, day) #using calendar module with weekdays function to generate a number pertaining to 
        if x in weekdays.keys(): #if the output from the weekday method in the dictionary
            DOW.append(weekdays[x]) #append the dict value to a list of Days of the Week
    return DOW #returns list of days of the week for datelist

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
    credentials = get_credentials() #also obtained from quickstart.py from https://developers.google.com/gmail/api/quickstart/python
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http, cache_discovery = True, cache = None) 

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
        x= main() #calling function that calls google client api
        with open(googlecache_file, 'w') as cache_file:
            json.dump(x, cache_file)
        print("Fetching. . . \n")
        return x


googledata = get_google_data() #assigning output of google API call to variable, which will be a list of dictionaries of the data of each google drive file

googleDates= [] #formats date to look more readable
zipdatagoogle= [] #obtains raw date as it is in the dict 
for each in googledata:
    date= each["createdTime"]
    zipdatagoogle.append(date)
    newdate= date.split("T")
    newerdate= newdate[0].split("-")
    googleDates.append(newerdate)

GOOGLEDOW= GetDOW(googleDates) #calling DOW function to get Days of the week for googledata, will return a list

conn= sqlite3.connect("FinalProject.sqlite") #establishing DB connection
cur= conn.cursor() #opening cursor 


cur.execute('DROP TABLE IF EXISTS Google') 
cur.execute('CREATE TABLE Google (file_name TEXT, file_id TEXT, date_created TIMESTAMP)') #creating users table with 3 columns 

for item in googledata:
    googletup= item["name"], item['id'], item['createdTime']
    cur.execute('INSERT INTO Google (file_name, file_id, date_created) VALUES (?,?,?)', googletup) #inserts name, id, and time created of each item

cur.execute('DROP TABLE IF EXISTS Google_Dates') 
cur.execute('CREATE TABLE Google_Dates (numerical_date TEXT, week_day TEXT)') #matches google numerical date with the weekday of that date

googledowtup= zip(zipdatagoogle, GOOGLEDOW) #creates a tuple containing the numerical date with its corresponding day of the week
for each in googledowtup:
    print(each)
    cur.execute('INSERT INTO Google_Dates (numerical_date, week_day) VALUES (?, ?)', each)


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

def CacheFacebook(baseurl, url_params): #facebook cache pattern
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
        response = requests.get(full_url) #using requests.get to get facebook graphAPI data
        #store the response

        FBCACHE_DICTION[full_url] = response.text #putting response in dictionary with key full_url
        response_text = response.text #assiging same data to return later
        fbcache_file = open(facebookcache_file, 'w') #writing the cachefile 
        fbcache_file.write(json.dumps(FBCACHE_DICTION)) 
        fbcache_file.close() #close file
    return response_text

def canonical_order(d):
    alphabetized_keys = sorted(d.keys()) #cleans up parameter dictionary by sorting the keys alphabetically
    res = [] 
    for k in alphabetized_keys:
        res.append((k, d[k]))
    return res #returns alphabetized list of key, value tuples

def requestURL(baseurl, params = {}): #the function that gets the URL ready to be requested
    req = requests.Request(method = 'GET', url = baseurl, params = canonical_order(params))
    prepped = req.prepare() 
    return prepped.url #url in correct format for requests.get function


access_token = "EAAXPPlAm9IYBAFcmHjaR1vRv6qhBTOA9lvUjwOUGMbMkcONQfCLiM3Upp19h1MZBzO2Wptoa9pBfbqcd43sbZCZAhtEJxlAQzbqgZAgRwgQNT3U9x73tinMNwxRRYETMW96YHWPnUjglvOvlPxkoWFnVzJZBiPwBQusf1Rw4vZBgZDZD"

url_params= {}
baseurl= "https://graph.facebook.com/v2.7/me/feed" #obtaining posts from my timeline
url_params["limit"]= 100 #100 posts exactly
url_params["access_token"]= access_token

f= CacheFacebook(baseurl, url_params) #calling cache function
fb= json.loads(f) #turning response object into a string
fbdata= fb["data"] #getting to the data 

FBDates= [] #formats date to look more readable
zipdatafb= [] #obtains raw date as it is in the dict
for each in fbdata: #accessing each dict to obtain post info
    date= each["created_time"] #accessing value of "created_time" key
    zipdatafb.append(date) #append raw date to list to use later
    newdate= date.split("T") 
    newerdate= newdate[0].split("-")
    FBDates.append(newerdate) #cleaned date up to look more readable and be used in the GETDOW function

FBDOW = GetDOW(FBDates) #calling DOW function to get Days of the week for fbdata, will return a list of days of week pertaining to numerical dates

cur.execute('DROP TABLE IF EXISTS Facebook')
cur.execute('CREATE TABLE Facebook (story TEXT, id TEXT, date_created TIMESTAMP)') #creating users table with 3 columns 

for item in fbdata:
    if "story" in item.keys(): #some of the data has "story" key, which is if the post is titled
        x = item["story"]
    else: #if the post is not titled, return null
        x= "null"
    fbtup= x, item['id'], item['created_time'], #collect all of this data into a tuple
    cur.execute('INSERT INTO Facebook (story, id, date_created) VALUES (?,?,?)', fbtup) #insert each tuple into the DB to its corresponding column

cur.execute('DROP TABLE IF EXISTS Facebook_Dates')
cur.execute('CREATE TABLE Facebook_Dates (numerical_date TEXT, week_day TEXT)') 


fbdowtup= zip(zipdatafb, FBDOW) #creates a zip object which is a list of tuples

for each in fbdowtup:
    print(each)
    cur.execute('INSERT INTO Facebook_Dates (numerical_date, week_day) VALUES (?,?)', each)
    

conn.commit() #commit changes to the DB
#- - - - - - - - - - - - - - - - - - - PLOTLY- - -  -- - - - - - - - - - - - - - - - - - - - - - - - - 

myfbdict= {"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0} #initialized DOW count dictionary


cur.execute('SELECT * FROM Facebook_Dates') # selecting all the rows from table Facebook_Dates, which contains date of post and day of week 
fbdowlist= cur.fetchall() #creates a list of these selected item

for each in fbdowlist: #item will be a tuple
    if each[1] == "Monday": #counter pattern for each DOW
        myfbdict["Monday"]+=1
    if each[1] == "Tuesday":
        myfbdict["Tuesday"]+=1
    if each[1] == "Wednesday":
        myfbdict["Wednesday"]+=1
    if each[1] == "Thursday":
        myfbdict["Thursday"]+=1
    if each[1] == "Friday":
        myfbdict["Friday"]+=1
    if each[1] == "Saturday":
        myfbdict["Saturday"]+=1
    if each[1] == "Sunday":
        myfbdict["Sunday"]+=1

mygoogledict= {"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0}

cur.execute('SELECT * FROM Google_Dates') # selecting all the rows from table Google_Dates, which contains date of post along with day of week
googledowlist= cur.fetchall() #creates a list of the items 

for each in googledowlist:
    if each[1] == "Monday": #counter pattern for each DOW
        mygoogledict["Monday"]+=1
    if each[1] == "Tuesday":
        mygoogledict["Tuesday"]+=1
    if each[1] == "Wednesday":
        mygoogledict["Wednesday"]+=1
    if each[1] == "Thursday":
        mygoogledict["Thursday"]+=1
    if each[1] == "Friday":
        mygoogledict["Friday"]+=1
    if each[1] == "Saturday":
        mygoogledict["Saturday"]+=1
    if each[1] == "Sunday":
        mygoogledict["Sunday"]+=1


fbkeys= list(myfbdict.keys()) #converting dict_keys object to a list for all four of these 
fbvalues= list(myfbdict.values())
googlekeys= list(mygoogledict.keys())
googlevalues= list(mygoogledict.values())


trace1 = go.Bar( #code pattern obtained from https://plot.ly/python/bar-charts/ 
    x=fbkeys, #x-axis will be day of the week
    y=fbvalues, #y-axis will be number of how frequently there was a post on that day
    name='Facebook use'
)
trace2 = go.Bar(
    x=googlekeys, #same as above
    y=googlevalues,
    name='Google Drive use'
)

data = [trace1, trace2]
layout = go.Layout(
    barmode='group'
)

fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='grouped-bar') #will open a URL to my graph!


cur.close() #always close the cursor when you're finished using it!

