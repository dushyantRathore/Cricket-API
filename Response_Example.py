import requests
import json

url = "https://powerful-tor-13817.herokuapp.com/live"

headers = {
    'cache-control': "no-cache",
    'postman-token': "e4db8c8c-1774-f923-3400-5f8b29be5bde"
    }

response = requests.request("POST", url, headers=headers)

news = response.text

json_object = json.loads(news)

print json_object





