from fastapi import APIRouter, Form, UploadFile, File, Request
from app.Utils.transcript import extract_video_id, get_transcript_from_youtube, get_title_from_youtube
from app.Utils.elevenlabs import text_to_speech
from app.Utils.extract_text import complete_text, complete_text_test, complete_youtube
import time
import asyncio
import os
import shutil
import requests

router = APIRouter()


def pipeline(value, functions):
    result = value
    for func in functions:
        result = func(result)
    return result

# YouTube video transcription processing
@router.post("/extract_mentioned_data")
def extract_mentioned_data(url: str = Form(...)):
    print(url)
    # if url == "":
    #     return {}
    # search_result = check_already_searched(url)
    # if search_result != None:
    #     return search_result

    print("start")
    start_time = time.time()
    video_id = extract_video_id(url)

    if (video_id == None):
        return {}
    data=[]
    data = get_title_from_youtube(video_id)
    title = data[0]
    author = data[1]
    avatar_url = data[2]
    print("Title Time: ", time.time() - start_time)

    transcript = get_transcript_from_youtube(video_id)
    print(time.time() - start_time)
    print(transcript)
    # content = extract_data(transcript)
    result = asyncio.run(complete_youtube(transcript))
    #print(result)
    # if 'media' in result:
    #     current_category = "---"
    #     for item in result['media']:
    #         if item["Category"] == current_category:
    #             item["Category"] = ""
    #         else:
    #             current_category = item["Category"]
    result['author'] = author
    result['title'] = title
    result['url'] = url

    with open('./data/avatar.jpg', 'wb') as handle:
        response = requests.get(avatar_url, stream=True)
        if not response.ok:
            print(response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

    
    result['avatar'] = 'https://api.recc.ooo/static/avatar.jpg'
    current_time = time.time()
    print("Total Time: ", current_time - start_time)
    # insert_url_database(url, result)
    return result


# test processing
@router.post("/v2/extract_text_data")
async def extract_text_data(text: str = Form(...)):
    start_time = time.time()
    print(time.time() - start_time)
    result = await complete_text_test(text)
    return result


# plain text processing
@router.post("/extract_text_data")
async def extract_text_data(text: str = Form(...)):
    start_time = time.time()
    print(time.time() - start_time)
    result = await complete_text(text)
    return result


@router.post("/transcript-audio-file")
async def transcript_audio_file(file: UploadFile = File(...)):
    text_to_speech()
    print(file.filename)

    UPLOAD_DIRECTORY = "./data"
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file.filename + " - goldrace"