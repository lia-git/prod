import datetime
import json
import traceback

import pymysql
import requests
import schedule
from chinese_calendar import is_workday

import setting

def get_sina_info(code):
    url = f"http://hq.sinajs.cn/list={code}"
    resp = requests.get(url).text.split("=")[-1][1:-1].split(",")
    now =  round(float(resp[3]),2)
    return now


def update_notice_price():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()

    try:
        # 执行SQL语句
        cursor.execute(f"select  stock_code,price_detail  from price_notice")

        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # cursor.close()
    codes = []
    print(items)
    for item in items:
         codes.append([item[0], json.loads(item[1]) if item[1] else []])

    for code,detail in codes:
        now_price = get_sina_info(code)
        detail.append(now_price)
        try:
            # 执行SQL语句
            cursor.execute(f"update price_notice set price_detail = '{json.dumps(detail)}' where stock_code = '{code}'")
            # 提交事务
            conn.commit()
        except Exception as e:
            # 有异常，回滚事务
            traceback.print_exc()
            conn.rollback()


def main():
    today = datetime.date.today()
    if is_workday(today):
        # if True:
        time_now = datetime.datetime.now()
        hour, minute = time_now.hour, time_now.minute
        if hour in [10, 13, 14] or (hour == 11 and 0 <= minute <= 30) or (hour == 9 and minute >= 30):
            update_notice_price()


if __name__ == '__main__':
    # main()
    schedule.every(3).seconds.do(main)
    while True:
        # logger.info(f"now_ is {time.time()}")
        schedule.run_pending()