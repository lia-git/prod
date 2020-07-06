import traceback

import pymysql

import setting


def clone_hot_db():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        for i in range(12,1,-1):
            cursor.execute(f"update stock_hot_history set bef_up_{i} = bef_up_{i-1} where 1;")
        # 提交事务
            conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()
def clone_hot_theme():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        for i in range(12,1,-1):
            cursor.execute(f"update theme_hot_history set bef_degree_{i} = bef_degree_{i-1} where 1;")
            cursor.execute(f"update theme_hot_history set tmp_degree = null where 1;")
            cursor.execute(f"update themes_stocks_hot_history set hot_stocks_{i} = hot_stocks_{i-1} where 1;")
            cursor.execute(f"update themes_stocks_hot_history set tmp_stocks = null where 1;")
            # 提交事务
            conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()

