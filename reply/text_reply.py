import json
import traceback

import pymysql
import redis

import setting
from wechat_utl import WeChatPub_2 as WeChatPub


def store_buy_stock(stock_price):
    stock_name,price = stock_price.split("#")
    code = get_stock(stock_name.strip())[1]
    insert_buy(code,price.strip())
    wechat = WeChatPub()
    wechat.send_msg("buy ok")




def insert_buy(code,price):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select * from price_notice where stock_code = '{code}';")
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    if item:
        try:
            # 执行SQL语句
            cursor.execute(f"update price_notice set buy_price = {price},buy_date = now() where stock_code = '{code}';")
            # 提交事务
            conn.commit()
        except Exception as e:
            # 有异常，回滚事务
            traceback.print_exc()
            conn.rollback()
    else:
        try:
            # 执行SQL语句
            cursor.execute(f"insert into price_notice(stock_code,buy_price) values('{code}',{price})")
            # 提交事务
            conn.commit()
        except Exception as e:
            # 有异常，回滚事务
            traceback.print_exc()
            conn.rollback()





def reply_stock_info(name):
    item = get_stock(name)
    name = item[2]
    wechat = WeChatPub()
    wechat.send_remind(title=f"{name}日K线图",content="<br>".join(item[3:7]),url_=f"http://image.sinajs.cn/newchart/daily/n/{item[1]}.gif")
    wechat.send_remind(title=f"{name}分时图",content="<br>".join(item[3:7]),url_=f"http://image.sinajs.cn/newchart/min/n/{item[1]}.gif")

def get_stock(name):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select * from stock_base where stock_name = '{name}';")
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    print(item)
    return [str(i) for i in item]


def set_custom_tom(stocks):
    sts = stocks.replace("\n",",").replace("，",",").\
        replace("、",",").replace(".",",").replace("。",",").\
        replace("\t",",").split(",")
    sts = [s.strip() for s in sts]
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    key = "tom_selected"
    if not r.exists(key):
        pass
    else:
        pre_list= json.loads(r.get(key))
        for s in pre_list:
            if s not in sts:
                sts.append(s)
    status = r.set(key,json.dumps(sts,ensure_ascii=False))
    wechat = WeChatPub()
    wechat.send_msg(f"OK:{status},len:{len(sts)}")










def get_one_stock(ele):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select * from stock_base where stock_name = '{ele}' or stock_code like '%{ele}';")
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    print(item)
    return [str(i) for i in item]

