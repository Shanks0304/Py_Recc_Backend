import base64
import time
from ..Utils.extra import get_ocr_image_result, get_title, get_structured_place_answer, get_structured_media_answer

async def complete_text(context: str):
    current_time =  time.time()
    # result = await asyncio.gather(get_title(context), get_structured_media_answer(context), get_structured_place_answer(context))
    # Run all async tasks concurrently and wait for all of them to finish.
    title_result = await get_title(context)
    media_result = await get_structured_media_answer(context)
    place_result = await get_structured_place_answer(context)
    # Combine the results into a single dictionary.
    result = {
        'title': title_result[0],
        'overview': title_result[1],
        'media': media_result['media'] + place_result['media']
    }
    print("total time: ", time.time() - current_time)
    return result

async def complete_youtube(context: str):
    current_time =  time.time()
    title_result = await get_title(context)
    media_result = await get_structured_media_answer(context)
    place_result = await get_structured_place_answer(context)
    
    result = {
        'overview': title_result[1],
        'media': media_result['media'] + place_result['media']
    }
    return result

async def complete_image(base64_image):
    image_to_text = get_ocr_image_result(base64_image)
    if image_to_text is None:
        return {
            "error": "There is no text found on the image."
        }
    return await complete_text(image_to_text)