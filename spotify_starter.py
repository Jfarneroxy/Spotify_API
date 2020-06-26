"""
This Program offers base code to build off of for Python projects based on the Spotify Web API.
The Spotify class contains necessary functions for user authentication through the APIs tokens
as well as a search function that can accept queries for songs, albums, and artists
"""

import base64
import requests
import datetime
from urllib.parse import urlencode



#The client id and client secret are unique to each Spotify user and must be changed for each application
client_id = 
client_secret = 


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    #generates base64 string for client credentials based on client id and client secret
    def get_client_credentials(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("Client ID or Client Secret is missing.")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()


    #inputs base64 string in to token to prepare the credentials for authorization
    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
         }

    #returns grant type as dictated by spotify API rules
    def get_token_data(self):
        return {
            'grant_type': 'client_credentials'
        }

    #steps to authenticate user in API accounting for token expiration
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range (200, 299):
            return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True


    #Combines all other authorization functions in order to generate usable token in API
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token


    #accepts generated access token and applies to header for queries
    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    #determines resource type of query returning album by default
    def get_resource(self, lookup_id, resource_type = 'albums', version = 'v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return{}
        #print(r.json())
        return r.json()

    # album query
    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')

    #artist query
    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')

    #base search function to model more complex queries off of
    def base_search(self, query_params):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return{}
        return r.json()

    #query including filtering operators
    def search(self, query=None, operator=None, operator_query=None, search_type='artist'):
        if query == None:
            raise Exception("No Query")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k,v in query.items()])
        if operator != None and operator_query !=None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        print(query_params)
        return self.base_search(query_params)



spotify = SpotifyAPI(client_id, client_secret)


# A song I like to test things out!
print(spotify.search(query="Only Human Four Tet", operator='', operator_query="", search_type="track"))
