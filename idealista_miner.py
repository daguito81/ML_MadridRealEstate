# Based on the code by "Ivan" from StackOverflow
# Modified from https://stackoverflow.com/questions/40023931/how-to-get-real-estate-data-with-idealista-api
# Modifications were mostly bug fixes and updating the code to work with current packages

#Import Libraries
import pandas as pd     #For data manipulation
import json             #To manipulate the json file (response)
import urllib           #To parse the keys
import requests as rq   #To connect to the API
import base64           #To encode the keys for the OAuth
import time             #To slow the loop to meet Idealista's requirements
import os               #To interact with the files in the OS

df_tot = pd.DataFrame() #Initializing Empty DataFrame to hold the data
limit = 90              #Number of requests to go through (Idealista has a 100 / month limit)

country = 'es' #values: es, it, pt  We choose 'es' for Spain
locale = 'es' #values: es, it, pt, en, ca  We choose es again for Spain
language = 'es' # We choose es for spanish
max_items = '50' #Idealista Max items is 50 (Item's per Request)
operation = 'rent' #We care about homes that are being rented
property_type = 'homes' # We care about homes and not commercial places
order = 'priceDown' #Just for sorting purposes
center = '40.416655,-3.704162' #Close to the center of Madrid
distance = '15000' #15km from the center seems to cover everything we're interested in
sort = 'desc' #For sorting purposes
bankOffer = 'false' #So we don't get offerings from bank-owned properties


def get_oauth_token(): #This function creates the Auth Token we need to make the API requests
    url = "https://api.idealista.com/oauth/token"                          
    apikey= urllib.parse.quote_plus('APIKey') 
    secret= urllib.parse.quote_plus('APISecret')
    auth = base64.b64encode(str.encode(apikey + ':' + secret))
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' ,'Authorization' : 'Basic ' + auth.decode()}
    params = urllib.parse.urlencode({'grant_type':'client_credentials'})
    content = rq.post(url,headers = headers, params=params)
    bearer_token = json.loads(content.text)['access_token']
    return bearer_token

def search_api(token, url):  #This function creates the API requests and returns the response as a json
    headers = {'Content-Type': 'Content-Type: multipart/form-data;', 'Authorization' : 'Bearer ' + token}
    content = rq.post(url, headers = headers)
    result = json.loads(content.text)
    return result




for i in range(1,limit): #This loops activates both functions for the ammount of requests we specify
    url = ('https://api.idealista.com/3.5/'+country+'/search?operation='+operation+#"&locale="+locale+
           '&maxItems='+max_items+
           '&order='+order+
           '&center='+center+
           '&distance='+distance+
           '&propertyType='+property_type+
           '&sort='+sort+ 
           '&numPage=%s'+
           '&language='+language) %(i)
    token = get_oauth_token()                       #This gets the authorization token
    a = search_api(token, url)                      #This does the API request with our parameters
    df = pd.DataFrame.from_dict(a['elementList'])   #This converts the json response into a dict and then creates a dataframe from it
    df_tot = pd.concat([df_tot,df])                 #This concatenates the total data dataframe with this request's dataframe
    
    if not os.path.isfile('idealista_data_temp.csv'):                               #If the file doesnt exists, it creates it
        df.to_csv('idealista_data_temp.csv', header='column_names', index=False)
    else: # else it exists so append without writing the header
        df.to_csv('idealista_data_temp.csv', mode='a', header=False, index=False)   #If the file exists, it appends the new data to it
    print("Request # ", i, "saved on temp")                                         #This is to work as a backup in case a request goes wrong
    time.sleep(1) #Timer to loop once every second (Idealista Limit)

df_tot = df_tot.reset_index()                           #Resets the index so it's a single one 
df_tot.to_csv("idealista_data_final.csv", sep = ',')    #Creates a final csv file, the lenght should be exactly the same as the temp csv

