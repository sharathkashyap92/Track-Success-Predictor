import pandas as pd
import requests 
import numpy as np
import sys
import spotipy
import spotipy.util as util
import json
import json.decoder
import os
from  billboard_scrape import get_songs
import sys
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

def set_spotify_credentials():
    #requrired spotipy details
    cid = input('cid: ')
    secret = input('secret: ')
    redirect_url = 'http://www.google.com/'
    user_name = input('user_name: ')

    client_credentials_manager = SpotifyClientCredentials(client_id = cid, client_secret = secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Tokens to make the direct HTTP requests
    auth_token = "Bearer " + input('auth_token from spotify developer website: ')
    headers = {
            "Content-Type": "application/json", 
            "Authorization": auth_token
         }

    return sp, headers

def get_song_data():
    sp, headers = set_spotify_credentials()
    n_weeks = int(input('\nscrape billboard for how many weeks? '))

    print('scraping billboard for hits:')
    df = get_songs(n_weeks)
    print('done scraping billboard!\n')

    df.weeks = df.weeks.apply(lambda x: x + 1 if x < 2 else x)

    track_ids = []
    df_final = pd.DataFrame()
    counter = 1

    print('getting song data from spotify:')
    for i in range(df.shape[0]):
        try:         
            # get the unique track_id from spotify    
            track_info = sp.search(q = 'artist:' + df.iloc[i]['artist'] + ' track:' + df.iloc[i]['title'], type = 'track')
            
            # getting album features
            album_id = track_info["tracks"]["items"][0]['album']['id']  
            URL = "https://api.spotify.com/v1/albums/" + album_id
            r = requests.get(url = URL, headers = headers) 
            album_features = r.json()
            track_ids = album_features['tracks']['items']
            album_popularity = album_features['popularity']
            album_id = album_features['id']
            n_markets = len(album_features['available_markets'])
            album_name = album_features['name']
            record_label = album_features['label']
            
            for tracks in track_ids:
                a = pd.Series()
                a['album_popularity'] = album_popularity
                a['album_id'] = album_id
                a['n_markets'] = n_markets
                a['album_name'] = album_name
                a['record_label'] = record_label
                    
                #getting track details
                URL = "https://api.spotify.com/v1/tracks/" + tracks['id']
                r = requests.get(url = URL, headers = headers) 
                element = r.json()
                a['artist'] = element['album']['artists'][0]['name']
                a['artist_id'] = element['album']['artists'][0]['id']
                a['release_date'] = element['album']['release_date']
                a['track_name'] = element['name']
                a['duration'] = element['duration_ms']
                a['explicit'] = element['explicit']
                a['track_id'] = element['id']
                a['track_popularity'] = element['popularity']
                
                # getting audio features
                URL = "https://api.spotify.com/v1/audio-features/" + a['track_id']
                r = requests.get(url = URL, headers = headers) 
                song_features = r.json()
                b = pd.Series(song_features)

                # getting artist features
                URL = "https://api.spotify.com/v1/artists/" + a['artist_id'] 
                r = requests.get(url = URL, headers = headers) 
                artist_data = r.json()
                a['artist_followers'] = artist_data['followers']['total']
                a['artist_popularity'] = artist_data['popularity']

                df_final = df_final.append(a.append(b), ignore_index = True)

                if (counter % 50 == 0):
                    print('added ', counter, ' songs')

                counter += 1
            
        except:
            print('no track id for ', df.iloc[i]['artist'], ' : ', df.iloc[i]['title'])
            
    df_final = df_final.drop(['uri', 'type', 'track_href', 'id'], axis = 1)

    print ('done retreiving song data from spotify; dataset has ',  df_final.shape[1], ' features of ', df_final.shape[0], ' songs!')

    df_merged = pd.merge(df_final, df,  how = 'left', left_on = ['artist','track_name'], right_on = ['artist','title']).drop('title', axis = 1)
    df_merged = df_merged.fillna(0)
    df_merged.to_csv('final_dataset.csv')

get_song_data()