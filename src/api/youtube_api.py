
# Sample Python code for youtube.commentThreads.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
import json
import googleapiclient.discovery
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

with open("azure_pg_database_connection.key", "r") as file:
    conn_string = file.read()
    conn_string = "postgresql" + conn_string
    
engine = create_engine(fr"{conn_string}")




def api_call():

    #dict added to DataFrame
    dict_to_df = {
        "publish_date": [],
        "comment_text": []
    }

    #setup from calling to youtube api
    api_service_name = "youtube"
    api_version = "v3"
    with open(fr"..\..\..\..\google_api_key.key") as file: #add you googleapikey
        DEVELOPER_KEY = file.read()

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId="retIj7ztcSE",
        maxResults=10
    )
    response = request.execute()

    #use loop under only for extracting more comments by pageToken
    #______________________________________________________________________________________________
    flag = 5 #how many time you going to loop next page
    while flag > 0:
        request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId="retIj7ztcSE",
        pageToken=response['nextPageToken'],
        maxResults=50 # decide how many comments to extract for each request
        )
        response = request.execute()

        for comments in response['items']:
            text_display = comments['snippet']['topLevelComment']['snippet']['textOriginal']
            publishdate = comments['snippet']['topLevelComment']['snippet']['publishedAt']
            
        
            dict_to_df['publish_date'].append(publishdate)
            dict_to_df['comment_text'].append(text_display)
            
        

      
        flag -= 1

    
    df = pd.DataFrame(data=dict_to_df)
    return df

df = api_call()


df.to_sql('youtube_comments', con=engine, if_exists='append', index=False)

