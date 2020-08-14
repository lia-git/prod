# https://bk-kpb.cls.cn/quote/block/stocks?block=cls80082

import traceback

import pymysql
import requests

import setting
import pandas as pd

from wechat_utl import WeChatPub_2 as WeChatPub


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
        record["stock_name"] = item["name"]
        record["last_price"] = item["last"]
        record["description"] = item["desc"].replace("\n",".")
        record["head_num"] = item["head_num"]
        record["weight"] = item["weight"]
        ret.append(record)
        stock_code.add(item["symbol"])
    return ret,stock_code

def get_all_db():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select * from stock_base where stock_code not  like 'sz300%';")
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


def update_stocks(new_stocks):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select stock_code,description from stock_base;")
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
        description_dict[item[0]] = item[1]
    try:
        # 执行SQL语句
        for record in new_stocks:
            if record["stock_code"] in description_dict:
                _desc = description_dict[record["stock_code"]].split("\n")
                if record['description'].replace("'",'"') not in _desc:
                    _desc.append(record['description'].replace("'",'"'))
                all_desc = "\n".join(_desc)
                sql = f'''
                    update stock_base set stock_name = '{record['stock_name']}' ,change_pct = {record['change_pct']} ,
                    last_price = {record['last_price']},
                    description = '{all_desc}',
                    head_num = {record['head_num']},
                    weight = {record['weight']}
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

def main():
    # new_themes = get_all_themes()
    exists = get_exist_themes()
    all_stocks_set = set([])
    for ix, theme in enumerate(exists):
        print(f"stock base,theme {ix}:{theme[0]}",flush=True)
        try:
            stocks,stocks_set = get_all_stocks(theme[0])
        # tmp_set = stocks_set - all_stocks_set
        # all_stocks_set = stocks_set | all_stocks_set
        # if ix % 20 ==0:
            update_stocks(stocks)
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
