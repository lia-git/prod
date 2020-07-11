import json
import time
import traceback

import pymysql
import random

import requests

import setting


def get_his_hot_stock():
    codes = get_stocks()
    for code in codes:
        url = f"https://q.stock.sohu.com/hisHq?code=cn_{code[2:]}&start=20200614&end=20200710&stat=1&order=D&period=d&callback=historySearchHandler&rt=json"
        resp = requests.get(url).json()
        if resp:
            his_list = resp[0]["hq"]
            for ix,his in enumerate(his_list):
                insert_today_hot(code,float(his[4][:-1]),ix+1)


    #
    # base_stock = Req_Jbase(url=url)
    # ret = base_stock.get()["data"]["list"]
    # # to_file(ret,"../origin_data","stock")
    #
    #
    # to_db(ret)
    # return ret


def get_stocks():

    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select stock_code from stock_base;")
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()


    items = [ item[0] for item in items]
    return items

def insert_today_hot(code,change_pct,ix):

    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句

        cursor.execute(f"update stock_hot_history set bef_up_{ix} = {change_pct} where stock_code = '{code}';")

        # cursor.execute(sql)
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()





def main():
    get_his_hot_stock()

if __name__ == '__main__':
    # get_theme_info()
    # get_theme_hot_info()
    main()
