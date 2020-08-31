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
        print(theme_last.decode())
        s[theme_last.decode()] = last_val.decode()
    else:
        print(theme_last.decode())

with open("rdx.txt",mode="w+") as r_:
    json.dump(s,r_,ensure_ascii=False)



# with open("rdx.txt",mode="r") as r_:
#     res = json.load(r_)
#     for k,v in res.items():
#         r.set(k,v)
    # data = {"key": theme_last.decode(), "val": last_val.decode()}
    # print(data)
    # headers = {
    #     'Content-Type': 'application/json; charset=UTF-8',
    # }
    # resp = requests.post("http://120.79.164.150:8080/x", data=json.dumps(data), headers=headers)




