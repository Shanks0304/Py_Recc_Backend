import base64
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse

from ..Utils.extra import get_transcription
from ..Utils.transcript import extract_video_id, get_transcript_from_youtube, get_title_from_youtube
from ..Utils.elevenlabs import text_to_speech
from ..Utils.extract_text import complete_image, complete_text, complete_youtube
import time
import asyncio
import os
from tempfile import NamedTemporaryFile

router = APIRouter()


def pipeline(value, functions):
    result = value
    for func in functions:
        result = func(result)
    return result

#---------- YouTube video transcription processing
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

    # with open('./data/avatar.jpg', 'wb') as handle:
    #     response = requests.get(avatar_url, stream=True)
    #     if not response.ok:
    #         print(response)
    #     for block in response.iter_content(1024):
    #         if not block:
    #             break
    #         handle.write(block)

    
    result['avatar'] = avatar_url
    current_time = time.time()
    print("Total Time: ", current_time - start_time)
    # insert_url_database(url, result)
    return result


#---------- plain text processing
@router.post("/extract_text_data")
async def extract_text_data(text: str = Form(...)):
    start_time = time.time()
    print(time.time() - start_time)
    result = await complete_text(text)
    return result

#---------- image processing
@router.post("/extract_image_data")
async def extract_image_data(image: UploadFile = File(...)):
    # UPLOAD_DIRECTORY = "./data/images"
    # image_path = os.path.join(UPLOAD_DIRECTORY, image.filename)
    # with open(image_path, "wb") as buffer:
    #     shutil.copyfileobj(image.file, buffer)
    # print("Image uploaded")
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Only JPEG and PNG are supported")
    
    try:
        content = image.file.read()
        base64_image = base64.b64encode(content).decode('utf-8')
    except Exception as e:
        raise HTTPException(500, detail=f"Error parsing file: {str(e)}")

    result = await complete_image(base64_image)
    # print(image_path)
    return result

#---------- whisper_model processing
@router.post("/transcript-audio-file")
async def transcript_audio_file(file: UploadFile = File(...)):
    try:
        with NamedTemporaryFile(delete=False, suffix=".opus") as temp_file:
            content = await file.read()  # Read the file content
            temp_file.write(content)  # Write it to the temp file
            temp_file_path = temp_file.name 
            transcription = get_transcription(temp_file_path)
            os.remove(temp_file_path)
            return JSONResponse(content={"text": transcription})
    except Exception as error:
        return JSONResponse(content={"error": str(error)}, status_code=500)

# # test processing
# @router.post("/v2/extract_text_data")
# async def extract_text_data(text: str = Form(...)):
#     start_time = time.time()
#     print(time.time() - start_time)
#     result = await complete_text_test(text)
#     return result