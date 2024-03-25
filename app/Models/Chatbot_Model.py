from app.Database import db

URL_DB = db.urls


def check_already_searched(url):
    try:
        URL_DB.delete_one({"url": url})
        result = URL_DB.find_one({"url": url})
        if result == None:
            return result
        return result['media']
    except Exception as e:
        print(e)
        print("delete database error!")
        return None


def insert_url_database(url, media):
    try:
        result = URL_DB.insert_one({"url": url, "media": media})
    except Exception as e:
        print(e)
        print("insert_url_database error!")
