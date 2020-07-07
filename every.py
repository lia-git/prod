import datetime

# 判断 2018年4月30号 是不是节假日
import json
import traceback

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
            url =f"http://hq.sinajs.cn/list={code}"
            resp = requests.get(url).text.split("=")[-1][1:-1].split(",")
            last,now = float(resp[2]),float(resp[3])
            pct = round(100*(now-last)/last, 2)
            update_stock_base(code,now,pct)
        except Exception as e:
        # 有异常，回滚事务
            traceback.print_exc()
            continue


def update_stock_base(code,now,pct):
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


def get_select_theme_change(file):
    themes = []
    with open(file) as file:
        for line in file:
            themes.append(line.strip())

    themes = [repr(theme)  for theme in themes]
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        sql = f''' select theme_name,tmp_degree from theme_hot where theme_name in ({",".join(themes)});
                      '''
        cursor.execute(sql)
        ret = cursor.fetchall()
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        print(sql)
        traceback.print_exc()
        conn.rollback()
        cursor.close()
        conn.close()
    return ret

def main():
    today = datetime.date.today()
    today_str = str(today).replace("-","")
    if is_workday(today):
        time = datetime.datetime.now()
        hour, minute = time.hour, time.minute
        if hour in [10,13,14,22] or (hour ==11 and 0<=minute<=34) or (hour ==9 and minute >25):
            update_stock_intime()
            get_tmp_theme_hot()
            ret = get_select_theme_change(f'custom_theme/{today_str}.txt')
            ret =[f"{ele[0]}:\t{ele[1]}" for ele in ret]
            wechat = WeChatPub()
            ret_str = '\n'.join(ret)
            wechat.send_msg(f"实时趋势:\n{ret_str}")

    # update_custom_db()
    print()



if __name__ == '__main__':
    main()