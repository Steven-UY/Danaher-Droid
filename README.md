# Danaher-Droid

## Overview

I **suck** at Jiu-Jitsu and hate having to sift through all the instructionals online—my attention span is too bad. Hence, I wanted to design a tool that could help me not be so bad. With Danaher-Droid, I hope that I can effectively perform retrieval augmented generation (RAG) on transcripts contained within the BJJ Fanatics YouTube channel. 

So, it's not really Danaher-Droid—more like BJJ Fanatics Droid—but whatever, Danaher sounds better.

### Goals:
- Have the LLM respond with accurate answers when asked about any BJJ position.
- Have responses in John Danaher’s voice.
- Create a tool that looks somewhat presentable.

---

## Tech Stack

### 1. RAG Pipeline

#### a. YouTube Data API - Retrieving Video IDs

- **API Client Setup**: Use the `googleapiclient` library to build the API client for making authorized requests.
    ```python
    youtube = build('youtube', 'v3', developerKey=api_key)
    ```

- **Fetching the Uploads Playlist**: Get the `uploads` playlist ID from the channel.
    ```python
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    ```

- **Fetching Video IDs from the Playlist**: A loop retrieves 50 video IDs per request.
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

#### b. YouTube Transcript API - Scraping Transcripts

- This uses the `youtube_transcript_api` to scrape transcripts from the retrieved video IDs.

---

### 2. Langchain - Processing and Storing the Transcripts

Langchain is used to:
- Load the transcripts.
- Split the transcripts into manageable chunks.
- Embed the text for efficient retrieval.
- Store the documents for use in RAG.

---

## Future Features

- Add a graphical user interface (GUI).
- Improve transcript analysis to ensure more accurate responses.
- Fine-tune the LLM to better match John Danaher’s speech patterns.

---

## Image

![John Danaher teaching Brazilian Jiu-Jitsu](https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fbjjfanatics.com%2Fcdn%2Fshop%2Farticles%2FJohn-Danaher_1024x1024.jpg%3Fv%3D1547846343&f=1&nofb=1&ipt=862a15c76eaabc76cb5947675f934a0b76f093a22f76af2ad26315467c3f2fa0&ipo=images)
