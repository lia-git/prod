import json
import multiprocessing
import time
import traceback

import pymysql
import redis
import requests

import setting


def get_all_stocks():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(
            f"select stock_code from stock_base  where  stock_code not  like 'sz300%' ")
        ret = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
    return [i[0] for i in ret]



def get_sina_info(code,now):
    url = f"http://hq.sinajs.cn/list={code}"
    print(url)
    resp = requests.get(url).text.split("=")[-1][1:-3]
    items = resp.strip().split(",")
    now_p, now_v, now_m = float(items[3]), float(items[8]) , float(items[9])
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    key = f"stock_{code}_previous"
    pre_p,pre_v,pre_m = 0,0,0
    now_info = [now_p, now_v, now_m]
    if not r.exists(key):
        pass
    else:
        pre_info = json.loads(r.get(key))
        # if now_info != pre_info:
        pre_p, pre_v, pre_m = pre_info
    r.set(key, json.dumps(now_info, ensure_ascii=False))
    now_p, now_v, now_m = float(items[3]), float(items[8]) - pre_v, float(items[9]) - pre_m
    buy = {float(items[11]): int(items[10]) * 100,
           float(items[13]): int(items[12]) * 100,
           float(items[15]): int(items[14]) * 100,
           float(items[17]): int(items[16]) * 100,
           }
    sell = {float(items[21]): int(items[20]) * 100,
            float(items[23]): int(items[22]) * 100,
            float(items[25]): int(items[24]) * 100,
            float(items[27]): int(items[26]) * 100,
            }

    key_power = f"stock_power_{code}"
    if not r.exists(key_power):
        stock_dict= {now:[[now_p, now_v / 10000, now_m / 10000], buy, sell]}
    else:
        stock_dict = json.loads(r.get(key_power))
        stock_dict[now]=[[now_p, now_v / 10000, now_m / 10000], buy, sell]
    r.set(key_power, json.dumps(stock_dict, ensure_ascii=False))






def main():
    x= time.time()
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    stock_list = r.keys("stock_power_*")
    if not stock_list:
        stock_list = ["sz002241"]*400
        # stock_list = get_all_stocks()
    else:
        stock_list = [stock[12:] for stock in stock_list]*400
    while True:
        now = int(time.time())
        pool = multiprocessing.Pool(processes=16)
        for code in stock_list:
            try:
                # get_sina_info(code, now)
                pool.apply_async(get_sina_info, (code,now))
                # ret.append([code, now, pct])
                # print(time.time() - s)
                # update_stock_base(code, now, pct)
            except Exception as e:
                # 有异常，回滚事务
                traceback.print_exc()
                continue
        pool.close()
        pool.join()
        break
    print(time.time()-x)











if __name__ == '__main__':
    main()