from serpapi import GoogleSearch
import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

cx = os.getenv("CX_ID")
api_key = os.getenv("GOOGLE_API_KEY")


def get_source_url(keyword):
    try:
        start_time = time.time()
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': keyword,
            'cx': cx,
            'key': api_key,
        }
        response = requests.get(url, params=params)
        data = response.json()
        # print(data)
        print("serp time: ", time.time() - start_time)
        return data['items'][0]['link']
    except:
        return "https://stackoverflow.com/questions/27920928/google-api-request-limit-exceeded"


def get_image_url(search_term):
    try:
        start_time = time.time()
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': search_term,
            'cx': cx,
            'key': api_key,
            'searchType': 'image',
            'num': 3
        }
        response = requests.get(url, params=params)
        response_json = json.loads(response.text)
        print("serp time: ", time.time() - start_time)
        return response_json['items'][0]['link']
    except:
        return "https://www.lifespanpodcast.com/content/images/2022/01/Welcome-Message-Title-Card-2.jpg"


def get_map_image_url(serach_term):
    try:
        start_time = time.time()
        params = {
            "engine": "google_maps",
            "q": serach_term,
            "type": "search",
            "api_key": os.getenv("SERP_API_KEY")
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        print("result: ", results)
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
            search = GoogleSearch(params)
            results = search.get_dict()
            print("serp time: ", time.time() - start_time)
            return results['search_metadata']['google_maps_url']
        else:
            print("serp time: ", time.time() - start_time)
            print("No place results found.")
            return "https://www.google.com/maps/place/Granite/@38.038073,-75.7687759,3z/data=!4m10!1m2!2m1!1sgranite+restaurant+paris!3m6!1s0x47e66f1a1fb579eb:0x265362fbe8c6f7b5!8m2!3d48.8610438!4d2.3419215!15sChhncmFuaXRlIHJlc3RhdXJhbnQgcGFyaXNaGiIYZ3Jhbml0ZSByZXN0YXVyYW50IHBhcmlzkgEXaGF1dGVfZnJlbmNoX3Jlc3RhdXJhbnSaASRDaGREU1VoTk1HOW5TMFZKUTBGblNVTlNYMk54VFRkM1JSQULgAQA!16s%2Fg%2F11ny2076x0?entry=ttu"
    except Exception as e:
        print(e)
        return "https://www.google.com/maps/place/Granite/@38.038073,-75.7687759,3z/data=!4m10!1m2!2m1!1sgranite+restaurant+paris!3m6!1s0x47e66f1a1fb579eb:0x265362fbe8c6f7b5!8m2!3d48.8610438!4d2.3419215!15sChhncmFuaXRlIHJlc3RhdXJhbnQgcGFyaXNaGiIYZ3Jhbml0ZSByZXN0YXVyYW50IHBhcmlzkgEXaGF1dGVfZnJlbmNoX3Jlc3RhdXJhbnSaASRDaGREU1VoTk1HOW5TMFZKUTBGblNVTlNYMk54VFRkM1JSQULgAQA!16s%2Fg%2F11ny2076x0?entry=ttu"
