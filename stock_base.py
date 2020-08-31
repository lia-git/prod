# https://bk-kpb.cls.cn/quote/block/stocks?block=cls80082
import json
import multiprocessing
import time
import traceback

import pymysql
import redis
import requests

import setting
import pandas as pd

from wechat_utl import WeChatPub_2 as WeChatPub

rdp = redis.ConnectionPool(host='localhost', port=6379)

def strQ2B(ustring):
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # 全角空格直接转换
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return "".join(ss)

def get_all_stocks(theme):
    url = f'https://bk-kpb.cls.cn/quote/block/stocks?block={theme}'
    resp = requests.get(url=url).json()["data"]["stocks"]
    ret = []
    stock_code =set([])
    for item in resp:
        if "ST" in item["name"]:
            continue
        record = {}
        record["change_pct"] = item["change"]
        record["stock_code"] = item["symbol"]
        record["stock_name"] = strQ2B(item["name"])
        record["last_price"] = item["last"]
        record["cmc"] = round(item["cmc"]/100000000,3)
        record["description"] = item["desc"].replace("\n",".")
        record["head_num"] = item["head_num"]
        record["weight"] = item["weight"]
        ret.append(record)
        stock_code.add(item["symbol"])
    return ret,stock_code

def get_all_db(flag=True):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    if flag:
        segment = "*"
    else:
        segment = "stock_code"
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select  {segment}  from stock_base where stock_code not  like 'sz300%' and stock_name not like '%ST%' and last_price between 4.0 and 50 ;")

        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # cursor.close()
    return items

def get_dragon(flag=True):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    if flag:
        segment = "*"
    else:
        segment = "stock_code"
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select  {segment}  from stock_base where stock_code not  like 'sz300%' and stock_name not like '%ST%' and description like '%龙头%' and last_price between 3.0 and 100;")

        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # cursor.close()
    return items


def get_exist_themes():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select theme_code,theme_name from theme_info;")
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()
    # ret = []
    # for item in items:
    #     ret.append([item[0])
    return items


def update_stocks(new_stocks,theme):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select stock_code,description,head_theme,rel_theme from stock_base;")
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # cursor.close()
    # conn.close()
    # exists = []
    description_dict = {}
    for item in items:
        # exists.append(item[0])
        description_dict[item[0]] =[item[1].strip() if item[1] else "",item[2].strip() if item[2] else "",item[3].strip() if item[3] else ""]
    try:
        # 执行SQL语句
        for record in new_stocks:
            if record["stock_code"] in description_dict:
                _desc = description_dict[record["stock_code"]][0].split("\n")
                _head = description_dict[record["stock_code"]][1].split("\n")
                _rel = description_dict[record["stock_code"]][2].split(",")
                if record['description'].replace("'",'"') not in _desc:
                    _desc.append(record['description'].replace("'",'"'))
                if "龙头" in record['description']:
                    _head.append(theme)
                _rel.append(theme)
                all_desc = "\n".join(set(_desc)).strip()
                all_head = "\n".join(set(_head)).strip()
                all_rel = ",".join(set(_rel)).strip(",")
                sql = f'''
                    update stock_base set stock_name = '{record['stock_name']}' ,change_pct = {record['change_pct']} ,
                    last_price = {record['last_price']},
                    description = '{all_desc}',
                    head_num = {record['head_num']},
                    head_theme = '{all_head}',
                    rel_theme = '{all_rel}',
                    weight = {record['weight']},
                    cmc = {record['cmc']} 
                    where stock_code = '{record['stock_code']}';
                '''
                cursor.execute(sql)
            else:
                sql = f"insert INTO stock_base({','.join(record.keys())}) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                values = list(record.values())
                cursor.execute(sql, values)  # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        print(sql)
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()

def to_file(res,name):
    # stocks = {}
    # with open("master.txt") as reader:
    #     for line in reader:
    #         code,name_ = line.strip().split("\t")
    #         stocks[code.lower()] = name_

    df = pd.DataFrame(res)
    df.to_excel(name)
    print()


def get_cls_info(code,moment):
    t1 = time.time()
    url = f"https://kpb3.cls.cn/quote/stock/fundflow?symbol={code}"
    resp = requests.get(url).text
    now_trend = round(json.loads(resp)["data"]["main_fund_diff"]/100000.0,3)
    last_trend = round(json.loads(resp)["data"]["d5"]["sum_fund_diff"]/100000.0,3)
    update_redis_main_trend([[code,now_trend,last_trend]],moment)
    print(f"{code} time cost {time.time()-t1}s")
    # return [code, now_trend, last_trend]


def code_main_trend(code_list,moment,logger):
    ret = []

    # pool = multiprocessing.Pool(processes=4)
    for ix,code in enumerate(code_list):
        try:
            logger.info(f"ix={ix}")
            # ret.append(get_cls_info(code))
            get_cls_info(code,moment)
            # pool.apply_async(get_cls_info, (code,moment))
            # ret.append([code, now, pct])
            # print(time.time() - s)
            # update_stock_base(code, now, pct)
        except Exception as e:
            logger.info(traceback.format_exc())

            # 有异常，回滚事务
            # traceback.print_exc()
            continue
    # pool.close()
    # pool.join()
    # ret = [i.get() for i in ret]
    # update_trend(ret,moment)
    # return ret

def update_trend(ret,moment):
    key = 'all_main_power'
    r = redis.StrictRedis(connection_pool=rdp, decode_responses=True)
    if not r.exists(key):
        res = {}
    else:
        res = json.loads(r.get(key))
    for code, trend, last_trend in ret:
        # pre_change_list = []
        ele = res.get(code,[])
        if ele:
            moment_dict = ele[2]
            moment_dict[moment] = ele[0] + trend
            ele[2] = moment_dict
            ele[1] = ele[0] + trend
        else:
            ele = [last_trend,last_trend+trend,{moment:last_trend+trend}]
        res[code] = ele
    r.set(key, json.dumps(res, ensure_ascii=False))
    print("DONE")




def update_base_main_trend(code_trend,moment):
    with open(f"trends/trend_{code_trend[0]}.txt",mode="w+") as writer:
        pt = code_trend[2]
        main_trend = {moment:code_trend[1]}
        writer.write(f"{pt}\n{json.dumps(main_trend,ensure_ascii=False)}")


# def update_base_main_trend(code_trend,moment):
#     # 得到一个可以执行SQL语句的光标对象
#     conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
#                            database=setting.db_name, charset="utf8")
#     cursor = conn.cursor()
#     try:
#         # 执行SQL语句
#         cursor.execute(f"select pivot, main_change from stock_base where stock_code = '{code_trend[0]}';")
#         items = cursor.fetchone()
#         print(f'item:{items}')
#         pt_,main_trend_ = items
#         if not pt_:
#             pt = code_trend[2]
#         else:
#             pt = pt_
#         if not main_trend_:
#             main_trend = {}
#         else:
#             main_trend = json.loads(main_trend_)
#         main_trend[moment] = pt + code_trend[1]
#         cursor.execute(f"update stock_base set pivot ={pt}, main_change='{json.dumps(main_trend,ensure_ascii=False)}'  where stock_code = '{code_trend[0]}';")
#
#
#         # 提交事务
#         conn.commit()
#     except Exception as e:
#         # 有异常，回滚事务
#         traceback.print_exc()
#         conn.rollback()
def update_redis_main_trend(code_trend,moment):
    # r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r = redis.StrictRedis(connection_pool=rdp,decode_responses=True)
    for code,trend,last_trend in code_trend:
        pivot_key = f"trend_{code}_pivot"
        change_key = f"trend_{code}_change"
        last_key = f"trend_{code}_last"
        # pre_change_list = []
        if not r.exists(pivot_key):
            r.set(pivot_key,last_trend)
        else:
            last_trend = float(r.get(pivot_key))
        if not r.exists(change_key):
            last_trend_change_dict = {moment:last_trend}
        else:
            last_trend_change_dict = json.loads(r.get(change_key))
            val =last_trend + trend
            last_trend_change_dict[moment] = val
            r.set(last_key,val)
        r.set(change_key,json.dumps(last_trend_change_dict,ensure_ascii=False))

def set_desc_null():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"update stock_base set description =null where 1;")
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()


def main():
    # new_themes = get_all_themes()
    # set_desc_null()
    exists = get_exist_themes()
    all_stocks_set = set([])
    for ix, theme in enumerate(exists):
        print(f"stock base,theme {ix}:{theme[0]}")
        try:
            stocks,stocks_set = get_all_stocks(theme[0])
        # tmp_set = stocks_set - all_stocks_set
        # all_stocks_set = stocks_set | all_stocks_set
        # if ix % 20 ==0:
            update_stocks(stocks,theme[1])
        except Exception as e:
            # 有异常，回滚事务
            traceback.print_exc()
            continue
    ret = get_all_db()
    to_file(ret, f"result/base.xlsx")
    wechat = WeChatPub()
    wechat.send_file(f"result/base.xlsx")
        # all_stocks = []
    # update_stocks(all_stocks)


if __name__ == '__main__':
    main()
