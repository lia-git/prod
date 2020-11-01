import datetime
import json
import traceback

import pymysql
import requests
import schedule
from chinese_calendar import is_workday

import setting
from mylog import fetch_logger
from wechat_utl import WeChatPub_3 as WeChatPub

logger = fetch_logger("notice")

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
    # print(items)
    for item in items:
         codes.append([item[0], json.loads(item[1]) if item[1] else []])

    for code,detail in codes:
        now_price = get_sina_info(code)
        if detail:
            if now_price != detail[-1]:
                detail.append(now_price)
        else:
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



def notice(hour):
    # if hour == 10:
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()

    try:
        # 执行SQL语句
        cursor.execute(f"select  b.stock_name,n.buy_price,n.price_detail,n.flag,b.stock_code  from price_notice n join stock_base b on n.stock_code = b.stock_code")

        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    records = []
    for item in items:
        records.append([item[0],item[1], json.loads(item[2]) if item[2] else [], json.loads(item[3]) if item[3] else {},item[4]])
    wechat = WeChatPub()
    pixel = 0.02
    for name,base_price,trend_price,flag,code in records:
        now_price = trend_price[-1]
        if now_price >= base_price:
            if not flag.get(f"down", 0) < 4:
                    wechat.send_msg(f"大事件：{name}触及买入\n价格：{now_price}")
                    flag[f"down"] = flag.get(f"down", 0) +1
                    update_flag(code, flag)
                    return

        # max_price = max(trend_price)
        # now_pct = round((now_price - base_price)/base_price,5)
        # max_pct = round((max_price - base_price)/base_price,5)
        # logger.info(f"{name}-now_pct:{now_pct},max_pct:{max_pct}")
        # print(now_pct)
        # logger.info(f"{[max_pct,now_pct]}")
        # if now_pct < -0.02:
        #     if not flag.get(f"down", 0) < 4:
        #         wechat.send_msg(f"大事件：{name}触及止损点\n价格：{now_price}")
        #         flag[f"down"] = flag.get(f"down", 0) +1
        #         update_flag(code, flag)
        #         return
        # for i in range(6,0,-1):
        #     # print(i)
        #     pct_bound =[pixel*i-0.01, pixel*i+ 0.01]
        #     price_bound = [base_price*(1+p) for p in pct_bound]
        #     if price_bound[0] <= now_price < price_bound[1] and max_price > price_bound[1]:
        #         if not flag.get(f"{i}th",0) <4:
        #             wechat.send_msg(f"大事件：{name} 回落第{i}止盈点\n价格：{now_price}")
        #             flag[f"{i}th"] = flag.get(f"{i}th",0) +1
        #             update_flag(code,flag)
        #             return
        # pixel = 0.05
        # if hour < 11:
        # for i in range(6):
        #         # print(i)
        #         pct_bound =[pixel*(i+1)- 0.01, pixel*(i+1)+ 0.01]
        #         price_bound = [base_price*(1+p) for p in pct_bound]
        #         if price_bound[0] <= now_price:
        #             if not flag.get(f"{i+1}kth",0) <4:
        #                 wechat.send_msg(f"小事件：{name} 突破{i+1}止盈点\n价格：{now_price}")
        #                 flag[f"{i+1}kth"] = flag.get(f"{i+1}kth",0)+1
        #                 update_flag(code,flag)
        #                 return


def update_flag(code,flag):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"update price_notice set flag= '{json.dumps(flag)}' where stock_code = '{code}'")
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()

def main():
    today = datetime.date.today()
    # if is_workday(today):
        # if True:
    time_now = datetime.datetime.now()
    hour, minute = time_now.hour, time_now.minute
    if hour in [10, 13, 14,22] or (hour == 11 and 0 <= minute <= 30) or (hour == 9 and minute >= 30):
        update_notice_price()
        notice(hour)


if __name__ == '__main__':
    # main()
    schedule.every(3).seconds.do(main)
    while True:
        # logger.info(f"now_ is {time.time()}")
        schedule.run_pending()