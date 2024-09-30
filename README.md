# Danaher-Droid
---
### Overview

I **suck** at Jiu-Jitsu and hate having to sift through all the instructionals online my attention span is too bad. Hence, I wanted to design a tool that could help me
not be so bad. With Danaher-Droid I hope that I can effectively perform retrieval augmented generation on transcripts contained within the BJJ Fanatics youtube channel.
So it's not really Danaher-Droid more like BJJ Fanatics droid but whatever Danaher sounds better.

With the Danaher-Droid I hope to:

 - Have the LLM respond with the right answers when asked about any BJJ position
 - To talk in John Danaher's voice
 - Look somewhat presentable

### Tech Stack

 #### RAG Pipeline
 1. Youtube Data API gets list of all the video_ids in the upload playlist
   - build imported from **googleapiclient** library creates client so we can make authorized requests to the api 
 ```python 
 youtube = build('youtube', 'v3', developerKey=api_key)
 ```
   - Requests made to API through **channels().list, playlistItems().list**

**gets the ID of uploads playlist** 
 ```
 python res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
 ```
 **creates loop where in each iteration we get 50 video ids in playlist**
 ```python 
    next_page_token = None
    while True:
        pl_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        pl_response = pl_request.execute()

        for item in pl_response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = pl_response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids
  ```
 2. youtube_transcript_api scrapes transcripts from youtube videos 

![Alt Text](https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fbjjfanatics.com%2Fcdn%2Fshop%2Farticles%2FJohn-Danaher_1024x1024.jpg%3Fv%3D1547846343&f=1&nofb=1&ipt=862a15c76eaabc76cb5947675f934a0b76f093a22f76af2ad26315467c3f2fa0&ipo=images)

3. Langchain Loads, Splits, Embeds and stores the document of transcripts


