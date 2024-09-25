from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import json

# Replace with your API key
API_KEY = 'AIzaSyDHXrOki7RpO6F5ziU41t_ZKRyeNq3DRLQ'

# Replace with the channel ID you want to fetch videos from
CHANNEL_ID = 'UCAqme-CE-yLm01BV5nUjPPA'

def get_video_ids(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_ids = []

    # Get Uploads playlist ID
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Retrieve all videos in the uploads playlist
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

        #If there are more videos don't break out of loop
        next_page_token = pl_response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

video_ids = get_video_ids(API_KEY, CHANNEL_ID)
print(f'Total videos found: {len(video_ids)}')

transcripts = {}

for video_id in video_ids:
    try:
        #Fetch transcript for each video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        fetched_transcript = transcript.fetch()

        # Combine transcript texts
        transcript_text = ' '.join([entry['text'] for entry in fetched_transcript])
        transcripts[video_id] = transcript_text

        print(f'Transcript fetched for video ID: {video_id}')
    except Exception as e:
        print(f'Could not retrieve transcript for video ID {video_id}: {e}')

# Save transcripts to a JSON file
with open('youtube_transcripts.json', 'w', encoding='utf-8') as f:
    json.dump(transcripts, f, ensure_ascii=False, indent=4)
