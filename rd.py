import json
import traceback

import pymysql
import redis
import requests

import setting

rdp = redis.ConnectionPool(host='localhost', port=6379)
r = redis.StrictRedis(connection_pool=rdp, decode_responses=True)
def get_redis_all():
    theme_list = r.keys("*")
    s = {}
    for theme_last in theme_list:
        last_val = r.get(theme_last)
        if "b'" not  in theme_last.decode():
            print(theme_last.decode())
            s[theme_last.decode()] = last_val.decode()
        else:
            print(theme_last.decode())
    return s


def get_all_keys():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    item = []
    try:
        # 执行SQL语句
        sql = f"select key from redis_back;"
        # logger.info(sql)

        cursor.execute(sql)
        item = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # logger.info(f"SS{item}")
    return [] if not item else [i[0] for i in item ]



def main():
    redis_db = get_redis_all()
    exist_keys = get_all_keys()
    for key,value in redis_db.items():
        print(type(key),type(value))
        update_back_db(key,value,exist_keys)


def update_back_db(key,value,exist_keys):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        if key in exist_keys:
        # 执行SQL语句
            sql = f"update redis_back set value = '{value[:20]}' where key = '{key}'"
        # logger.info(sql)
        else:
            sql = f"insert into redis_back(key,value) values('{key}','{value[:20]}');"

        print(sql)
        cursor.execute(sql)
        # item = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # logger.info(f"SS{item}")
    # return [] if not item else [i[0] for i in item ]





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



if __name__ == '__main__':
    main()

