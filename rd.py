import json

import redis
import requests

rdp = redis.ConnectionPool(host='localhost', port=6379)
r = redis.StrictRedis(connection_pool=rdp, decode_responses=True)
theme_list = r.keys("*")
s = {}
for theme_last in theme_list:
    last_val = r.get(theme_last)
    if "b'" not  in theme_last.decode():
        s[theme_last.decode()] = last_val.decode()
    else:
        print(theme_last.decode())

with open("rdx.txt",mode="w+") as w:
    json.dump(s,w,ensure_ascii=False)
    # data = {"key": theme_last.decode(), "val": last_val.decode()}
    # print(data)
    # headers = {
    #     'Content-Type': 'application/json; charset=UTF-8',
    # }
    # resp = requests.post("http://120.79.164.150:8080/x", data=json.dumps(data), headers=headers)




