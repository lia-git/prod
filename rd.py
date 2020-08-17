import json

import redis

rdp = redis.ConnectionPool(host='localhost', port=6379)
r = redis.StrictRedis(connection_pool=rdp, decode_responses=True)
theme_list = r.keys("*")
s = {}
for theme_last in theme_list:
    last_val = r.get(theme_last)
    s[str(theme_last)] = str(last_val)

with open("rd.txt",mode="w+") as w:
    json.dump(s,w,ensure_ascii=False)

