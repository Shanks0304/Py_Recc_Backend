import time
from app.Utils.extra import get_title, get_structured_place_answer, get_structured_media_answer

async def complete_text(context: str):
    current_time =  time.time()
    # result = await asyncio.gather(get_title(context), get_structured_media_answer(context), get_structured_place_answer(context))
    # Run all async tasks concurrently and wait for all of them to finish.
    title_result = await get_title(context)
    media_result = await get_structured_media_answer(context, False)
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
    media_result = await get_structured_media_answer(context, False)
    place_result = await get_structured_place_answer(context)
    # Combine the results into a single dictionary.
    temp_result = {
        'media': media_result['media'] + place_result['media']
    }

    new_dict = {}
    for item in temp_result['media']:
        new_item = {
            k: item[k] for k in ["Title", "Author", "Description", "imgURL", "launchURL", "authorURL"]
        }
        if item['Category'] not in new_dict:
            new_dict[item['Category']] = [new_item]
        else:
            new_dict[item['Category']].append(new_item)

    # print(new_dict)
    result = {'media': new_dict}
    print("YouTube total time: ", time.time() - current_time)
    return result


async def complete_text_test(context: str):
    current_time =  time.time()
    # result = await asyncio.gather(get_title(context), get_structured_media_answer(context), get_structured_place_answer(context))
    # Run all async tasks concurrently and wait for all of them to finish.
    title_result = await get_title(context)
    media_result = await get_structured_media_answer(context, True)
    place_result = await get_structured_place_answer(context)

    # Test part
    temp_result = {
        'media': media_result['media'] + place_result['media']
    }

    new_dict = {}
    for item in temp_result['media']:
        new_item = {
            k: item[k] for k in ["Title", "Author", "Description", "imgURL", "launchURL", "authorURL"]
        }
        if item['Category'] not in new_dict:
            new_dict[item['Category']] = [new_item]
        else:
            new_dict[item['Category']].append(new_item)

    # Combine the results into a single dictionary.
    result = {
        'title': title_result[0],
        'overview': title_result[1],
    }
    result['media'] = media_result['media'] + place_result['media']
    print("total time: ", time.time() - current_time)
    return result