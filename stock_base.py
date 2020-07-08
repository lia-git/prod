# https://bk-kpb.cls.cn/quote/block/stocks?block=cls80082

import traceback

import pymysql
import requests

import setting


def get_all_stocks(theme):
    url = f'https://bk-kpb.cls.cn/quote/block/stocks?block={theme}'
    resp = requests.get(url=url).json()["data"]["stocks"]
    ret = []
    for item in resp:
        record = {}
        record["change_pct"] = item["change"]
        record["stock_code"] = item["symbol"]
        record["stock_name"] = item["name"]
        record["last_price"] = item["last"]
        record["description"] = item["desc"]
        record["head_num"] = item["head_num"]
        record["weight"] = item["weight"]
        ret.append(record)
    return ret


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
        cursor.execute(f"select stock_code from stock_base;")
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # cursor.close()
    # conn.close()
    exists = []
    for item in items:
        exists.append(item[0])
    try:
        # 执行SQL语句
        for record in new_stocks:
            if record["stock_code"] in exists:
                sql = f'''
                    update stock_base set stock_name = '{record['stock_name']}' ,change_pct = {record['change_pct']} ,
                    last_price = {record['last_price']},
                    description = '{record['description'].replace("'",'"')}',
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


def main():
    # new_themes = get_all_themes()
    exists = get_exist_themes()
    # all_stocks = []
    for ix, theme in enumerate(exists):
        print(f"stock base,theme {ix}:{theme[0]}",flush=True)
        stocks = get_all_stocks(theme[0])
        # all_stocks.extend(stocks)
        # if ix % 20 ==0:
        update_stocks(stocks)
        # all_stocks = []
    # update_stocks(all_stocks)


if __name__ == '__main__':
    main()
