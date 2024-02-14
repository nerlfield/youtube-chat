
import re
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

def get_yt_metadata(video_id):
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    yt = YouTube(video_url)

    return {
        "title": yt.title,
        "author": yt.author
    }

def extract_youtube_video_id(url: str) -> str:
    regex_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)', # Standard format
        r'(?:https?://)?youtu\.be/([^?&]+)' # Shortened format
    ]
    
    for pattern in regex_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def chunk_with_overlap(arr, chunk_size, overlap):
    if len(arr) < chunk_size:
        return [arr]  # Return the array as a single chunk
    
    chunks = []
    i = 0
    while i + chunk_size <= len(arr):
        chunks.append(arr[i:i+chunk_size])
        i += chunk_size - overlap
    if i < len(arr) and not chunks[-1] == arr[-chunk_size:]:
        chunks.append(arr[-chunk_size:])
    return chunks

def get_transcription(video_id):
    result = []
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        for segment in transcript_list:
            start_time = segment['start']
            duration = segment['duration']
            text = segment['text']

            result.append({
                "start": segment['start'],
                "duration": segment['duration'],
                "text": text
            })
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return f"Error fetching transcript: {e}"
    
    return result