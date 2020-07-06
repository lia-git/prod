import traceback

import pymysql
import requests

import setting


def get_all_themes():
    url = 'https://bk-kpb.cls.cn/quote/blocks?sv=743&app=cailianpress'
    resp = requests.get(url=url).json()["data"]["blocks"]
    ret = []
    for item in resp:
        record = {}
        record["change_pct"] = item["change"]
        record["theme_code"] = item["symbol"]
        record["theme_name"] = item["name"]
        record["type"] = item["type"]
        record["description"] = item["desc"]
        record["up"] = item["up_down"]["up"]
        record["down"] = item["up_down"]["down"]
        record["fair"] = item["up_down"]["fair"]
        ret.append(record)
    return ret


def get_exist_themes():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select theme_code from theme_info;")
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


def update_themes(new_themes,exists_themes):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        for record in new_themes:
            if record["theme_code"] in exists_themes:
                sql = f'''
                    update theme_info set theme_name = '{record['theme_name']}' ,change_pct = {record['change_pct']} ,
                    type = '{record['type']}',
                    description = '{record['description']}',
                    theme_name = '{record['theme_name']}',
                    up = {record['up']},
                    down = {record['down']},
                    fair = {record['fair']}
                    where theme_code = '{record['theme_code']}';
                '''
                cursor.execute(sql)
            else:
                sql = f"insert INTO theme_info({','.join(record.keys())}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                values =  [str(i) for i in  record.values()]
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
    new_themes = get_all_themes()
    exists = get_exist_themes()
    update_themes(new_themes,exists)




if __name__ == '__main__':
    main()