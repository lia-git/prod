import json

import redis
import requests

rdp = redis.ConnectionPool(host='localhost', port=6379)
r = redis.StrictRedis(connection_pool=rdp, decode_responses=True)
theme_list = r.keys("*")
s = {}
for theme_last in theme_list[:10]:
    last_val = r.get(theme_last)
    data = {"key": theme_last.decode(), "val": last_val.decode()}
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
    }
    resp = requests.post("http://120.79.164.150:8080/x", data=json.dumps(data), headers=headers)




