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
        # record = {}
        # record["change_pct"] = item["change"]
        # record["stock_code"] = item["symbol"]
        # record["stock_name"] = item["name"]
        # record["last_price"] = item["last"]
        # record["description"] = item["desc"]
        # record["head_num"] = item["head_num"]
        # record["weight"] = item["weight"]
        if "ST" not in item["name"]:
            ret.append(item["symbol"])
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


def update_mapping(new_stocks):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select theme_code from theme_stocks_map;")
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
        for theme_code,theme_name,stocks in new_stocks:
            if theme_code in exists:
                sql = f'''
                    update theme_stocks_map set theme_name = '{theme_name}' ,count = {len(stocks)},stock_names = '{".".join(stocks)}' 
                    where theme_code = '{theme_code}';
                '''
                cursor.execute(sql)
            else:
                sql = f"insert INTO theme_stocks_map(theme_code,theme_name,count,stock_names) VALUES (%s,%s,%s,%s)"
                cursor.execute(sql, [theme_code,theme_name,len(stocks),".".join(stocks)])
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()






def main():
    # new_themes = get_all_themes()
    exists = get_exist_themes()
    all_stocks = []
    for ix,theme in enumerate(exists):
        stocks = get_all_stocks(theme[0])
        print(f"mapping index {ix}:{theme[0]}",flush=True)
        all_stocks.append([theme[0],theme[1],stocks])
        if ix % 20 ==0:
            update_mapping(all_stocks)
            all_stocks = []
    update_mapping(all_stocks)




if __name__ == '__main__':
    main()