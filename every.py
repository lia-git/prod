import datetime

# 判断 2018年4月30号 是不是节假日
import json
import traceback
import pandas as pd
import pymysql
import requests
from chinese_calendar import is_workday, is_holiday

import setting
from update_tmp_degree import get_tmp_theme_hot
from wechat_utl import WeChatPub


def get_all_stocks():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        for i in range(12, 1, -1):
            cursor.execute(f"select stock_code from stock_base;")
            items = cursor.fetchall()
            # 提交事务
            conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    return [item[0] for item in items]


def update_stock_intime():
    codes = get_all_stocks()
    for code in codes:
        try:
            url = f"http://hq.sinajs.cn/list={code}"
            resp = requests.get(url).text.split("=")[-1][1:-1].split(",")
            last, now = float(resp[2]), float(resp[3])
            pct = round(100 * (now - last) / last, 2)
            update_stock_base(code, now, pct)
        except Exception as e:
            # 有异常，回滚事务
            traceback.print_exc()
            continue


def update_stock_base(code, now, pct):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        sql = f'''
                        update stock_base set change_pct = {pct} ,last_price = {now}
                        where stock_code = '{code}';
                    '''
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        print(sql)
        traceback.print_exc()
        conn.rollback()
        cursor.close()
        conn.close()


def get_select_theme_change():

    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        sql = f''' select th.theme_name,th.tmp_degree,th.bef_degree_1,th.bef_degree_2,th.bef_degree_3,tm.masters from theme_hot th join theme_stocks_map tm
                on th.theme_code = tm.theme_code  where th.theme_code not in ({','.join(setting.black_list)}) ;
                      '''
        cursor.execute(sql)
        ret = cursor.fetchall()
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        print(sql)
        traceback.print_exc()
        conn.rollback()
    try:
        # 执行SQL语句
        cursor.execute(
            f"select stock_code,change_pct from stock_base  where stock_code not  like 'sz300%' ;")
        candits = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()
    limit_candits = set([can[0] for can in candits if can[1]>9.84])
    high_candits = set([can[0] for can in candits if 1.8 <= can[1] <= 5])
    low_candits = set([can[0] for can in candits if can[1]<1.8])
    ret = [[int(item[1].strip(",").split(",")[0]),
            item[:-1],
            set(item[-1].split(".")) & limit_candits if item[-1] else set([]),
            set(item[-1].split(".")) & high_candits if item[-1] else set([]),
           set(item[-1].split(".")) & low_candits if item[-1] else set([])] for item in ret]
    final = sorted(ret,key=lambda i:i[0],reverse=True)
    return final


def set_tmp_null():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        sql = ' update stocks.theme_hot set tmp_degree=null where 1;'
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        print(sql)
        traceback.print_exc()
        conn.rollback()
        cursor.close()
        conn.close()


def to_file(res,name):
    stocks = {}
    with open("master.txt") as reader:
        for line in reader:
            code,name_ = line.strip().split("\t")
            stocks[code.lower()] = name_
    res_ = [[item[1][0],str(item[1][2:][::-1]),item[0],item[1][1],",".join([stocks[code] for code in item[2]]),",".join([stocks[code] for code in item[3]]),",".join([stocks[code] for code in item[4]])] for item in res]
    df = pd.DataFrame(res_,columns=["版块","历史","最新","趋势","涨停","候选","低位"])
    df.to_excel(name)
    print()


def update_mater_stocks():
    stocks = {}
    with open("master.txt") as reader:
        for line in reader:
            code,name = line.strip().split("\t")
            stocks[code.lower()] = name

    code_set,name_set = set(stocks.keys()),set(stocks.values())
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        sql = f''' select theme_code,stock_names from theme_stocks_map ;
                      '''
        cursor.execute(sql)
        ret = cursor.fetchall()
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        print(sql)
        traceback.print_exc()
        conn.rollback()
    ret = [[ele[0],set(ele[1].split("."))] for ele in ret]

    try:
        for code,stocks in ret:
            headers = stocks & code_set
            if headers:
                sql = f''' update theme_stocks_map set masters = '{".".join(headers)}' where theme_code = '{code}' ;
                              '''
                cursor.execute(sql)
                conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        print(sql)
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()
    # return final



def main():
    today = datetime.date.today()
    if is_workday(today):
        time_now = datetime.datetime.now()
        print(time_now)
        hour, minute = time_now.hour, time_now.minute
        if hour == 8 and 40 < minute < 58:
            set_tmp_null()
            update_mater_stocks()
            wechat = WeChatPub()
            wechat.send_msg('开盘热度置空')
        if hour in [10, 13, 14] or (hour == 11 and 0 <= minute <= 30) or (hour == 9 and minute > 4) or (hour in (23,) and minute < 46):
            update_stock_intime()
            get_tmp_theme_hot()
            file_name = str(time_now).replace("-","").replace(":","").replace(" ","")[:12]
            ret = get_select_theme_change()
            to_file(ret,f"result/{file_name}.xlsx")
            wechat = WeChatPub()
            wechat.send_file(f"result/{file_name}.xlsx")

    # update_custom_db()
    print()


if __name__ == '__main__':
    main()
