# Remember to Credit Playsound Taylor Marks @taylor@marksfam.com

from moviepy.editor import VideoFileClip
from bs4 import BeautifulSoup
from pytube import YouTube
from playsound import playsound
import requests
import asyncio
import json
import sys
import re
import os


def play(file):
    playsound(file)
    os.remove(file)
    

async def convert_file(old, new):
    video = VideoFileClip(old)
    video.audio.write_audiofile(new)
    video.close()
    await asyncio.sleep(1)


def download(link):
    old_path = "yt-audio.mp4"
    new_path = "yt-audio.mp3"

    yt = YouTube(link)
    audio = yt.streams.filter(file_extension = "mp4").first()
    audio.download(filename = old_path)

    asyncio.run(convert_file(old_path, new_path))
    play(new_path)

    print("Song Finished")
    os.remove(old_path)


def query(s):
    query = f"https://www.youtube.com/results?search_query={s}"

    response = requests.get(query).text
    soup = BeautifulSoup(response, 'lxml')

    script = soup.find_all('script')[33]
    json_text = re.search('var ytInitialData = (.+)[,;]{1}', str(script)).group(1)
    json_data = json.loads(json_text)

    content_stream = (
        json_data
        ['contents']['twoColumnSearchResultsRenderer']['primaryContents']
        ['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    )

    if "showingResultsForRenderer" in content_stream[0] or "didYouMeanRenderer" in content_stream[0] or "channelRenderer" in content_stream[0]:
        for key in content_stream:
            if "videoRenderer" in key:
                video_id = key['videoRenderer']['videoId']
                video_thumbnail = key['videoRenderer']['thumbnail']['thumbnails'][0]['url']
                video_title = key['videoRenderer']['title']['runs'][0]['text']
                return {"link": f"https://www.youtube.com/watch?v={video_id}", "title": video_title, "img": video_thumbnail}
                break
    else:
        video_id = content_stream[0]['videoRenderer']['videoId']
        video_thumbnail = content_stream[0]['videoRenderer']['thumbnail']['thumbnails'][0]['url']
        video_title = content_stream[0]['videoRenderer']['title']['runs'][0]['text']
        return {"link": f"https://www.youtube.com/watch?v={video_id}", "title": video_title, "img": video_thumbnail}

async def sleep(secs):
    await asyncio.sleep(secs)

search = input("Song >")
search_query = query(search)
download(search_query['link'])