#
import datetime
import time
import traceback

import pymysql
import requests

import setting


def get_master():
    ret = []
    url = f"https://kpb3.cls.cn/quote/limit/detail?app=cailianpress&channel=0&cuid={setting.device_id}&field=limit_short_focus&mb=iPhone12%2C5&net=1&os=ios&ov=13.5.1&platform=iphone&province_code=4403&sign={setting.sign}&sv=7.4.4&token={setting.token}&uid=641119#"
    print(url)
    resp = requests.get(url).json()["data"]
    for item in resp:
        if "sz300" not in item["symbol"] and "ST" not in item["name"]:
            record = {}
            record["days"] = item["trade_days"]
            record["limit_count"] = item["limit_up_days"]
            record["stock_code"] = item["symbol"]
            record["stock_name"] = item["name"]
            record["reason"] = item.get("reason","nothing")
            ret.append(record)
    url_ = f"https://api3.cls.cn/v1/market_daily_pro/get?app=cailianpress&channel=0&cuid={setting.device_id}&mb=iPhone12%2C5&net=1&os=ios&ov=13.5.1&platform=iphone&province_code=4403&sign=5c8662e47158a34a38adff77ee6a9dca&sv=7.4.4&token={setting.token}&uid=641119"
    # print(url_)
    # resp_ = requests.get(url_).json()
    resp_ = requests.get(url_).json()["data"]["stock_up"]
    for part in resp_:
        for item in part["stock_list"]:
            record ={}
            if item['up_freq'] >1 and "sz300" not in item["stock_code"] and "ST" not in item["stock_name"]:
                print("great")
                record["days"] = item['up_freq']
                record["limit_count"] = item['up_freq']
                record["stock_code"] = item["stock_code"]
                record["stock_name"] = item["stock_name"]
                record["reason"] = item.get("up_reason","nothing")

    return ret
    # last, now = float(resp[2]), float(resp[3])
    # pct = round(100 * (now - last) / last, 2)

def get_exist_headers():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select stock_code from stock_headers;")
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()
    ret = []
    for item in items:
        ret.append(item[0])
    return ret


def update_headers(new_stocks, exists_stocks):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        for record in new_stocks:
            record["recent_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if record["stock_code"] in exists_stocks:
                sql = f'''
                    update stock_headers set stock_name = '{record['stock_name']}',limit_count = {record['limit_count']},
                    days = {record['days']},reason = '{record['reason']}',recent_time = '{record["recent_time"]}'
                    where stock_code = '{record['stock_code']}';
                '''
                cursor.execute(sql)
            else:
                keys,values = [],[]
                for k,v in record.items():
                    keys.append(k)
                    if k in ["days","limit_count","recent_time"]:
                        values.append(v)
                    else:
                        values.append(str(v))
                sql = f"insert INTO stock_headers({','.join(keys)}) VALUES (%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, values)
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()



def main():
    headers = get_master()
    exists_stocks = get_exist_headers()
    update_headers(headers,exists_stocks)
    




if __name__ == '__main__':
    main()