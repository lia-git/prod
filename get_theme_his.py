import traceback

import pymysql

import setting


def get_all_uplimit(ix):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select b.stock_name  from stock_base b join stock_hot_history h on b.stock_code = h.stock_code where h.bef_up_{ix}>=9.9;")
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()
    items = [item[0] for item in items]
    return items




def get_all_themes():

    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select * from theme_stocks_map;")
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()
    return items

def insert_his_theme():
    themes = get_all_themes()

    for ix in range(11):
        hots = get_all_uplimit(ix+1)
        for theme in themes:
            limits = set(hots) & set(theme[4].split("."))
            # if limits:
            # if theme[1] =="300843":
            #     print()
            update_db(theme[1],theme[2],ix+1,len(limits))





def update_db(code,name,ix,hot_num):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句

        # cursor.execute(f"insert into theme_hot(theme_code,theme_name,bef_degree_{ix}) values ('{code}','{name}',{hot_num});")
        cursor.execute(f"update theme_hot set bef_degree_{ix} = {hot_num} where theme_code = '{code}';")
        # cursor.execute(f"update themes_stocks_hot_history set hot_stocks_{ix} = '{stocks}' where theme_code = '{code}';")

        # cursor.execute(sql)
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    insert_his_theme()