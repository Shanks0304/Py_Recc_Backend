from ..Utils.google_API import get_source_url, get_image_url, get_map_image_url
import time
import json
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI,  AsyncOpenAI
import aiohttp
import asyncio
import os
import random
import requests

from typing import Tuple

client = OpenAI()
title_client = AsyncOpenAI()

load_dotenv()

tokenizer = tiktoken.get_encoding('cl100k_base')

transcript = ''

substring_to_replace = "https://www.google.com/maps/place/"

def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)
   
def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist

# def get_localImageURL(category, url, idx):
#     if not os.path.exists("./data/text"):
#         os.makedirs("./data/text")
#     with open(f"./data/text/{category}_{idx}.jpg", 'wb') as handle:
#         response = requests.get(url, stream=True, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
#         if not response.ok:
#             print(response)
#         for block in response.iter_content(1024):
#             if not block:
#                 break
#             handle.write(block)

def nullCheck(data: str):
    lowered_data = data.lower()
    if lowered_data == 'n/a' or lowered_data == 'not applicable' or lowered_data == 'unknown':
        return ''
    else:
        return data

# def convert_media_to_dict(item, idx):
#     # print(item)
#     try:
#         # if not check_media(item):
#         #     return {}
#         title = google_result[' '.join(item)]
#         # get_localImageURL('media', google_image_result[' '.join(item)], idx)
#         author = google_author_result[' '.join(item)]
#         image = f"https://api.recc.ooo/static/text/media_{idx}.jpg"
#         result = {
#             "Category": item[0],
#             "Title": nullCheck(item[1]),
#             "Author": nullCheck(item[2]),
#             "Description": item[3],
#             "imgURL": image,
#             "launchURL": title,
#             "authorURL": author,
#         }
#         return result
#     except Exception as e:
#         print(e)
#         result = {
#             "Category": "OpenAI Server Error",
#             "Title": "OpenAI Server Error",
#             "Title_Source": "",
#             "Author": "OpenAI Server Error",
#             "Author_Source": "",
#             "Description": "OpenAI Server Error",
#             "Image": "",
#             "Launch_URL": "",
#             "Key":""
#         }
#         print("convert media to dict error!")
#         return result

def convert_media_to_dict(item, idx):
    # print(item)
    try:
        # if not check_media(item):
        #     return {}
        title = google_result[' '.join(item)]
        author = google_author_result[' '.join(item)]
        image = google_image_result[' '.join(item)]
        result = {
            "Category": item[0],
            "Title": nullCheck(item[1]),
            "Author": nullCheck(item[2]),
            "Description": item[3],
            "imgURL": image,
            "launchURL": title,
            "authorURL": author,
        }
        return result
    except Exception as e:
        print(e)
        result = {
            "Category": "OpenAI Server Error",
            "Title": "OpenAI Server Error",
            "Title_Source": "",
            "Author": "OpenAI Server Error",
            "Author_Source": "",
            "Description": "OpenAI Server Error",
            "Image": "",
            "Launch_URL": "",
            "Key":""
        }
        print("convert media to dict error!")
        return result

def convert_place_to_dict(item):
    try:     
        # print(serp_image_result)
        # print(serp_result)

        # image = serp_image_result[' '.join(item)]
        map_launch = serp_result[' '.join(item)][0]
        map_title = serp_result[' '.join(item)][1]
        map_image = serp_result[' '.join(item)][2]
        result = {
            "Category": item[0],
            "Title": map_title,
            "Author": nullCheck(item[2]),
            "Description": item[3],
            "imgURL": map_image,
            "launchURL": map_launch,
            "authorURL": "",
        }
        return result
    except Exception as e:
        print(e)
        result = {
            "Category": "OpenAI Server Error",
            "Title": "OpenAI Server Error",
            "Title_Source": "",
            "Author": "OpenAI Server Error",
            "Author_Source": "",
            "Description": "OpenAI Server Error",
            "Image": "",
            "Launch_URL": "",
            "Key":""
        }
        print("convert place to dict error!")
        return result

serp_result = {}
# serp_image_result = {}
# serp_title_result = {}

google_result = {}
google_author_result = {}
google_image_result = {}

async def fetch_serp_results(session, query):
    alt_query = ' '.join(tuple(query[0:3]))
    # alt_query = unique_list(alt_query)
    # print(alt_query)
    try:
        params = {
            'api_key': os.getenv("SERP_API_KEY"),      # your serpapi api key: https://serpapi.com/manage-api-key
            "engine": "google_maps",
            "type": "search",  # from which device to parse data
            'q': alt_query, # search query
        }
        print('fetch place')
        try:
            async with session.get('https://serpapi.com/search.json', params=params) as response:
                results = await response.json()
                # print(results)
        except Exception as error:
            print(error)
    
        first_place = results.get('place_results')
        if not first_place:
            first_place = results.get('local_results')[0]
        if 'gps_coordinates' in first_place:
            lat = first_place['gps_coordinates']['latitude']
            lng = first_place['gps_coordinates']['longitude']
            data_id = first_place['data_id']
            params = {
                "engine": "google_maps",
                "type": "place",
                "data": f"!4m5!3m4!1s{data_id}!8m2!3d{lat}!4d{lng}",
                "api_key": os.getenv("SERP_API_KEY")
            }
            # print(first_place)
            try:
                async with session.get('https://serpapi.com/search.json', params=params) as response:
                    results = await response.json()
            except Exception as error:
                print(error)
            # print(results)
            map_url = results['search_metadata']['google_maps_url']
            if substring_to_replace in map_url:
                map_url = map_url.replace(substring_to_replace, substring_to_replace + f"@{lat},{lng},17z/")
            serp_result[' '.join(query)] = [map_url]
            serp_result[' '.join(query)].append(results['place_results']['title'])
            
            photo_params = {
                "engine": "google_maps_photos",
                "data_id": data_id,
                "api_key": os.getenv("SERP_API_KEY")
            }
            try:
                async with session.get('https://serpapi.com/search.json', params=photo_params) as response:
                    results = await response.json()
            except Exception as error:
                print(error)
            photo_url = results['photos'][0]['image']
            # serp_image_result[' '.join(query)] = photo_url
            serp_result[' '.join(query)].append(photo_url)
            # print("photo_url: ", photo_url)
            # print(serp_image_result[query])
            #print(serp_result[query])
    except Exception as error:
        print ("SERP fetch error:" ,error)
        serp_result[query] = "https://www.google.com/maps/place/Granite/@38.038073,-75.7687759,3z/data=!4m10!1m2!2m1!1sgranite+restaurant+paris!3m6!1s0x47e66f1a1fb579eb:0x265362fbe8c6f7b5!8m2!3d48.8610438!4d2.3419215!15sChhncmFuaXRlIHJlc3RhdXJhbnQgcGFyaXNaGiIYZ3Jhbml0ZSByZXN0YXVyYW50IHBhcmlzkgEXaGF1dGVfZnJlbmNoX3Jlc3RhdXJhbnSaASRDaGREU1VoTk1HOW5TMFZKUTBGblNVTlNYMk54VFRkM1JSQULgAQA!16s%2Fg%2F11ny2076x0?entry=ttu"

cx = os.getenv("CX_ID")

async def fetch_google_results(session, query, flag):
    alter_query = ' '.join(tuple(query[0:3])) + ' IMDB' if query[0] == 'movie' else ' '.join(tuple(query[0:3]))
    params = {
        'q': alter_query,
        'cx': cx,
        'key': os.getenv("GOOGLE_API_KEY"),
    }
    if flag:
        params['searchType'] = 'image'
        params['num'] = 3
    try:
        try:
            async with session.get("https://www.googleapis.com/customsearch/v1", params=params) as response:
                results = await response.json()
        except Exception as error: 
            print("GoogleAPI:", error)
        if flag:
            google_image_result[' '.join(query)] = results['items'][0]['link']
            # print("image: ", results['items'][0]['link'])
        else:
            # print(results)
            google_result[' '.join(query)] = results['items'][0]['link']

    except Exception as error:
        print("fetch google result error:", error)
        if flag:
            google_image_result[' '.join(query)] = "https://www.lifespanpodcast.com/content/images/2022/01/Welcome-Message-Title-Card-2.jpg"
        else:
            google_result[' '.join(query)] = "https://www.lifespanpodcast.com/content/images/2022/01/Welcome-Message-Title-Card-2.jpg"

async def fetch_google_author_results(session, query):
    alter_query = ' '.join(tuple(query[0:2])) + ' IMDB' if query[0] == 'movie' else ' '.join(tuple(query[0:2]))
    params = {
        'q': alter_query,
        'cx': cx,
        'key': os.getenv("GOOGLE_API_KEY"),
    }
    try:
        async with session.get("https://www.googleapis.com/customsearch/v1", params=params) as response:
            results = await response.json()
        # print(results)
        google_author_result[' '.join(query)] = results['items'][0]['link']
    except Exception as error:
        print('author result error:', error)
        google_author_result[' '.join(query)] = ""


# async def get_all_url_for_profile():
    # async with aiohttp.ClientSession() as session:
    #     tasks = []
    #     for query in serp_list:
    #         task = asyncio.ensure_future(fetch_serp_results(session, query))
    #         tasks.append(task)
    #     for query in google_list:
    #         task = asyncio.ensure_future(fetch_google_results(session, query, 0))
    #         tasks.append(task)
    #         task = asyncio.ensure_future(fetch_google_results(session, query, 1))
    #         tasks.append(task)
    #     results = await asyncio.gather(*tasks)

async def get_all_url_for_profile(apiResponse, typeCheckflag):
    if typeCheckflag == 'media':
        async with aiohttp.ClientSession() as session:
            tasks = []
            for query in apiResponse['media']:
                task = asyncio.ensure_future(fetch_google_results(session, query, 0))
                tasks.append(task)
                task = asyncio.ensure_future(fetch_google_results(session, query, 1))
                tasks.append(task)
                task = asyncio.ensure_future(fetch_google_author_results(session, query))
                tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for query in apiResponse['place']:
                task = asyncio.ensure_future(fetch_serp_results(session, query))
                tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)

# def insert_item_to_serp_list(item):
#     serp_list.append(item[2] + ' ' + item[1] + ' ' + item[0])   
# def insert_item_to_google_list(item):
#     google_list.append(item)

async def update_answer(apiResponse, typeCheckflag:str):
    answer = {'media': []}
    try:
        await get_all_url_for_profile(apiResponse, typeCheckflag)
        print("update_answer() is started")
        if typeCheckflag == 'media':
            for index, item in enumerate(apiResponse['media']):
                result = convert_media_to_dict(item, index)
                if not result:
                    continue
                else:
                    answer['media'].append(result)
        if typeCheckflag == 'place':
            for item in apiResponse['place']:
                result = convert_place_to_dict(item)
                if not result:
                    continue
                else:
                    answer['media'].append(result)
        category_list = []
        #     "restaurant",
        #     "unknown",
        #     "conversation area",
        #     "",
        #     "grocery store",
        #     "bakery",
        #     "vinyl record",
        #     "music band"
        # ]
        for recc in answer['media']:
            category_list.append(recc['Category'])
        primary_categories = get_primary_category('\n'.join(category_list))
        print(primary_categories)
        item_to_primary = {}
        for primary, items in primary_categories.items():
            for item in items:
                if item not in item_to_primary:
                    item_to_primary[item] = []
                if primary not in item_to_primary[item]:
                    item_to_primary[item].append(primary)
        print(item_to_primary)

        for recc in answer['media']:
            if recc['Category'] in item_to_primary:
                recc['Primary_Category'] = item_to_primary[recc['Category']]
        return answer
    except Exception as e:
        print(e)
        print("update answer error!")
        return []


async def get_structured_answer(context: str):
    # Step 1: send the conversation and available functions to GPT
    start_time = time.time()
    # instructor = f"""
    #     Get the mentioned media and place information from the body of the input content.
    #     You have to provide me all of the mentioned medias and places such as book, movie, article, poscast, attractions, restaurant, museum, hotel, Tourist destination.
    #     And then provide me detailed information about the category, author(only for media), subtitle(only for place), title, description about each media and place with your knowledge.
    #     Don't forget to output author and description for each media.
    #     Don't forget to output subtitle and description for each media.
    #     You have to analyze below content carefully and then extract all medias and places mentioned in that content.
    #     You shouldn't miss any one of the media and place such as book, movie, article, poscast, attractions, restaurant, museum, hotel, Tourist destination.
    #     But you should extract medias both title and author of which you know already.
    #     And you should extract all places.
    # """

    instructor = f"""
        Get the media and places information from input content.
    """
    functions = [
        {
            'name': 'extract_info',
            'description': f"{instructor}",
            'parameters': {
                'type': 'object',
                'properties': {
                    "media": {
                        'type': 'array',
                        # 'description': "Extract all of the mentioned medias such as book, movie, article, podcast in the body of the input text and description about them with your knowledge. All items must have Category, Title, Author, Description properties.",
                        'description': "Extract all of the mentioned media you find from the input content such as book, movie, article, podcast in the input text and description about them with your knowledge. Each item must have Category, Title, Author(only for media, neccessary), Description(perhaps it would be your knowledge) properties.",
                        'items': { 
                            'type': 'object',
                            'properties': {
                                'Category': {
                                    'type': 'string',
                                    'description': 'The most suitable category of the media. Such as book, movie, article, podcast.'
                                },
                                'Title': {
                                    'type': 'string',
                                    'description': "This item can't contain the content of not specified or not mentioned but only exact name of title for this media. You must come up with it with your own knowledge only if title of which is not mentioned in the input context. If you don't know the exact title, you should print 'unknown'."
                                },
                                'Author': {
                                    'type': 'string',
                                    'description': "In case of movie please provide any director or creator. Don't say you don't know it. You must come up with it with your own knowledge if author of which is not mentioned in the input context. If you don't know the exact author, you should find the Google search and extrach accurate author and if there is no result even in Google then print 'unknown'."
                                },
                                # 'Description': {
                                #     'type': 'string',
                                #     'description': "Detailed description about each media mentioned in input text. This item must contain detailed description about each media. Output as much as possible with your own knowledge as well as body of above text."
                                # },
                            }
                        }
                    },
                    "place": {
                        'type': 'array',
                        # 'description': "Extract all of the mentioned places such as retaurant, hotel, museum, Tourist destination in the body of the input text and description about that with your knowledge.  All items must have Category, Title, Subtitle, Description properties.",
                        'description': "Extract all of the mentioned places you find from the input content such as retaurant, hotel, museum, Tourist destination in the body of the input content and description about them with your knowledge. Each item must have Category, Title, Subtitle, Description properties." ,
                        'items': {
                            'type': 'object',
                            'properties': {
                                'Category': {
                                    'type': 'string',
                                    'description': 'The most suitable category of the place. Such as retaurant, hotel, museum, Tourist destination and etc. '
                                },
                                'Title': {
                                    'type': 'string',
                                    'description': "This item can't contain the content of not specified or not mentioned but only exact name for this place. But don't say unknown or you don't know it. You must come up with it with your own knowledge only if title of which is not mentioned in the input context. If you don't know the exact title, you should print 'unknown'."
                                },
                                'Subtitle': {
                                    'type': 'string',
                                    'description': "Suitable subtitle of given place such as simple introduction. If this subtitle doesn't mentioned in the input, you should create with your knowledge. For example, for the hotel, it can be 5-star tourist hotel and for restaurant, it can be Haute French restaurant."
                                },
                                # 'Description': {
                                #     'type': 'string',
                                #     'description': "Detailed description about each place mentioned in input text. This item must contain detailed description about each place. Output as much as possible with your own knowledge as well as body of above text."
                                # },
                            }
                        }
                    }
                }

            }
        },
    ]

    print('here2')

    try:
        response = client.chat.completions.create(
            model='gpt-4-1106-preview',
            max_tokens=2000,
            messages=[
                {'role': 'system', 'content': instructor},
                # {'role': 'user', 'content': f"""
                #     This is the input content you have to analyze.
                #     {context}
                #     Please provide me the data about places and media such as books, movies, articles, podcasts, attractions, restaurant, hotel, museum,  mentioned above.
                #     Please output the data with your own knowledge focusing on category, title, author, subtitle.

                # """}
                {'role': 'user', 'content': f"""
                    This is the input content you have to analyze.
                    {context}                    
                """}
            ],
            seed=2425,
            functions=functions,
            function_call={"name": "extract_info"}
        )
        response_message = response.choices[0].message
        system_fingerprint = response.system_fingerprint
        print(system_fingerprint)
        current_time = time.time()
        print("Elapsed Time: ", current_time - start_time)
        if hasattr(response_message, "function_call"):
            # print("response_message: ",
            #       response_message.function_call.arguments)
            json_response = json.loads(
                response_message.function_call.arguments)
            print(json_response)
            answer = await update_answer(json_response)

            return {"transcript": transcript, "media": answer}
        else:
            print("function_call_error!\n")
            return {}
    except Exception as e:
        print(e)
        print("hello")
        return {}


async def get_structured_answer_not_functionCalling(context: str):
    # Step 1: send the conversation and available functions to GPT
    start_time = time.time()  
    print(tiktoken_len(context))
    try:
        response = client.chat.completions.create(
            model='gpt-4-0125-preview',
            max_tokens=2000,
            messages=[
                {'role': 'system', 'content': "Get the 'media's and 'place's from the input content in json, Dont' forget that the category of media must be the media type, not the place like restaurant, museum or other words associated to places. Dont' forget that category of place must be the place type, not the media like book, movies and other words associated to media type."},
                {'role': 'user', 'content': f"""
                    This is the input content you have to analyze.
                    {context}""" +
                    """
                    Please extract the following information from the above text:
                    In the input, there will be'media's such as books, movies, articles, podcasts, attractions, and places such as restaurants, museums, hotels, tourist destinations, and bars.

                    For media, please output category, title, author, and description.
                    Dont' forget that the category of media must be the media type, not the place like restaurant, museum or other words associated to places.
                    Don't forget that the description must be in the input content and should be the simple part (less than 100 words) of the input, not your knowledge.
                    Dont' forget that author must be the person's name and the most famous, only one person and you should.
                    Dont' forget that if 1 or 2 of the other 3 properties (category, title, and author) are not mentioned in the input content, then you must come up with them using your knowledge.
                    Dont' forget you must find title and author using your knowledge and must not output 'unknown'. It is illegal.
                    
                    For place, please output category, title, subtitle, and only one sentence description.
                    Dont' forget that category of place must be the place type, not the media like book, movies and other words associated to media type.
                    Don't forget that the description must be in the input content and should be the simple part (less than 100 words) of the input, not your knowledge.
                    Dont' forget that if 1 or 2 of the other 3 properties (category, title and subtitle) are not mentioned in the input content, then you must come up with them using your knowledge.                 
                    Dont' forget you must find the title using your knowledge and not output 'unknown'. It is illegal.

                    Sample output format is below:
                        {"media": [["book", "Fight Club", "Chuck Palahniuk", "Abcdefefddd"]],"place": [["bookstore", "The Painted Porch", "Historical bookstore in Bastrop, Texas", "This bookstore "]]}
                    You should output this type.
                """}
            ],
            seed=2425,
            temperature = 0.7,
            response_format={"type": "json_object"}
        )
        response_message = response.choices[0].message.content
        json_response = json.loads(response_message)
        print(json_response)
        # system_fingerprint = response.system_fingerprint
        print("Elapsed Time: ", time.time() - start_time)

        answer = await update_answer(json_response)
        return answer
    except Exception as e:
        print(e)
        print("hello")
        return {}

async def get_title(context: str):
    # Step 1: send the conversation and available functions to GPT
    start_time = time.time()
    print("get_title() is started")
    try:
        response = await title_client.chat.completions.create(
            model='gpt-4-0125-preview',
            max_tokens=2000,
            messages=[
                {'role': 'system', 'content': "Get the extracted title and brief overview from the input content."},
                {'role': 'user', 'content': f"""
                    This is the input context you have to analyze.
                    {context}""" +
                    """
                    Extract this context and create the title of this context and brief overview focusing on the entire context meaning.
                    Remember that title has less than 10 words and brief overview has less than 50 words.
                    Main point is extraction focusing on date, place, name, etc.
                    Sample output list format is below:
                    ["Remene in Italy.","This is Joe's vocation journey in Italy."]
                """}
            ],
            seed= 4826,
            temperature = 0.5,
        )
        response_message = response.choices[0].message.content
        json_response = json.loads(response_message)
        # print(type(response_message))
        print("title result is:", response_message)
        system_fingerprint = response.system_fingerprint
        # print("media_fingerprint: ", system_fingerprint)
        # print(randon_seed)
        print("Elapsed Time: ", time.time() - start_time)
    except Exception as e:
        print(e)
        print("hello")
        return {}
    try:
        print()
        return json_response
    except Exception as error:
        print(error)
        return {}

def get_primary_category(context:str):
    try:
        response = client.chat.completions.create(
            model='gpt-4-0125-preview',
            max_tokens=2000,
            messages=[
                {'role': 'system', 'content': "please categorize items."},
                {'role': 'user', 'content': f"""
                    primary categories are 'restaurant', 'hotel', 'shopping', 'entertainment', 'servicies', 'health & medical', 'travel', 'food', 'Automative', 'professional services', 'education', 'finance', 'home services',etc.
                    This is the input list of items you have to categorize.
                    {context}""" +
                    """
                    I'd like to categorize them on the basis of primary cateogry.
                    output result is below:
                     {primary_category1:[item1, item2, item3], primary_category2: [item4, item5, item6]}
                    Don't need to use all the primary categories and you just show the primary categories which has proper items.
                    Last one, remember you can not find out the proper primary category of specific item, then you should give 'other' as primary category.
                    You should output this type as JSON.
                    """
                }
            ],
            seed= 4826,
            temperature = 0.5,
            response_format={"type": "json_object"}
        )
        response_message = response.choices[0].message.content
        json_response = json.loads(response_message)
        return json_response
    except Exception as e:
        print(e)
        print("hello")
        return {}

async def get_structured_media_answer(context: str):

    # Step 1: send the conversation and available functions to GPT
    start_time = time.time()
    print("media function is started")
    try:
        response = client.chat.completions.create(
            model='gpt-4-0125-preview',
            max_tokens=2000,
            messages=[
                {'role': 'system', 'content': "Get the 'media's from the input content."},
                {'role': 'user', 'content': f"""
                    This is the input context you have to analyze.
                    {context}""" +
                    """
                    Extract and Output category, title, author, and description of media.
                    Category of 'media' should be media type such as book, movie, article, podcasts, attractions.
                    Always focus on the category of media and dont' forget that the category of media must be the media type, not the place like restaurant, museum or other words associated to places.
                    Don't forget that the description must be in the input content and should be the simple part (less than 50 words) of the input, not your knowledge.
                    Dont' forget that author must be the person's name and the most famous, only one person and you should.
                    Dont' forget that if 1 or 2 of the other 3 properties (category, title, and author) are not mentioned in the input content, then you must come up with them using your knowledge.
                    Dont' forget you must find title and author using your knowledge and must not output 'unknown'. It is illegal.
                    Sample output json format is below:
                        {'media':[["book", "Fight Club", "Chuck Palahniuk", "Abcdefefddd"],["movie", "World War 2", "Allen AMsi", "Amcifer"]]}
                    You should output this type.
                """}
            ],
            seed= 4826,
            temperature = 0.5,
            response_format={"type": "json_object"}
        )
        response_message = response.choices[0].message.content
        json_response = json.loads(response_message)
        print(json_response)
        # print(type(json_response))
        system_fingerprint = response.system_fingerprint
        # print("media_fingerprint: ", system_fingerprint)
        # print(randon_seed)
        print("Elapsed Time: ", time.time() - start_time)
    except Exception as e:
        print(e)
        print("hello")
        return {}
    try:
        answer = await update_answer(json_response, 'media')
        return answer
    except Exception as error:
        print(error)
        return {}

async def get_structured_place_answer(context: str):
    # Step 1: send the conversation and available functions to GPT
    start_time = time.time()
    print("place function is started")
    try:
        response = client.chat.completions.create(
            model='gpt-4-0125-preview',
            max_tokens=2000,
            messages=[
                {'role': 'system', 'content': "Get 'place's from the input content in json"},
                {'role': 'user', 'content': f"""
                    This is the input content you have to analyze.
                    {context}""" +
                    """
                    Extract and Output category, title, subtitle, and description of place.
                    Category of 'place' should be place type such as restaurants, museums, hotels, tourist destinations and bars.
                    Dont' forget that category of place must be the place type, not the media like book, movies and other words associated to media type.
                    Don't forget that the description must be in the input content and should be the simple part (less than 50 words) of the input, not your knowledge.
                    Dont' forget that if 1 or 2 of the other 3 properties (category, title and subtitle) are not mentioned in the input content, then you must come up with them using your knowledge and must contain the area or country in title or subtitle that helps to find correct place among the places which has same names.                 
                    Dont' forget you must find the title using your knowledge and not output 'unknown'. It is illegal.

                    Sample output format is below:
                        {"place": [["bookstore", "The Painted Porch in Bastrop, Texas", "Historical bookstore in Bastrop, Texas", "This bookstore "]]}
                    You should output this type.
                """}
            ],
            seed= 6601,
            temperature = 0.5,
            response_format={"type": "json_object"}
        )
        response_message = response.choices[0].message.content
        json_response = json.loads(response_message)
        print(json_response)
        system_fingerprint = response.system_fingerprint
        # print(random_seed)
        print("place_fingerprint: ", system_fingerprint)
        print("Elapsed Time1: ", time.time() - start_time)
    except Exception as e:
        print(e)
        print("hello")
        return {}

    try: 
        answer = await update_answer(json_response,'place')
        return answer
    except Exception as error:
        print(error)
        return {}
