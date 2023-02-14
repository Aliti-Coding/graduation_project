
# Sample Python code for youtube.commentThreads.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
import json
import googleapiclient.discovery


#bygger url for å gjøre call

comments_lst = []
comment_published_lst = []


api_service_name = "youtube"
api_version = "v3"
with open("google_api_key.key") as file:
    DEVELOPER_KEY = file.read()

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)

nextpagetoken = ""

request = youtube.commentThreads().list(
    part="snippet,replies",
    videoId="retIj7ztcSE",
    maxResults=1000
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
    maxResults=10 # decide how many comments to extract for each request
    )
    response = request.execute()


    for comments in response['items']:
        text_display = comments['snippet']['topLevelComment']['snippet']['textOriginal']
        publishdate = comments['snippet']['topLevelComment']['snippet']['publishedAt']
        comments_lst.append(text_display)
        comment_published_lst.append(publishdate)

    # nextpagetoken = response['nextPageToken']
    flag -= 1



    # with open(fr'youtube_data_{flag}.json', 'w') as outfile:
    #     json.dump(response, outfile, indent=4)




print(len(comments_lst))
