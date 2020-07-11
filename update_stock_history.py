import datetime
import traceback

import pymysql
from chinese_calendar import is_workday

import setting


def clone_hot_db():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        for i in range(12, 1, -1):
            cursor.execute(f"update stock_hot_history set bef_up_{i} = bef_up_{i - 1} where 1;")
            # 提交事务
            conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()


def copy_day_stock():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        for i in range(12, 1, -1):
            cursor.execute(f"select stock_code, change_pct from stock_base;")
            items = cursor.fetchall()
            # 提交事务
            conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    for code, change_pct in items:
        try:
            # 执行SQL语句
            cursor.execute(f"update stock_hot_history set bef_up_1 = {change_pct} where stock_code = '{code}';")
            # 提交事务
            conn.commit()
        except Exception as e:
            # 有异常，回滚事务
            traceback.print_exc()
            conn.rollback()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    today = datetime.date.today()
    if is_workday(today):
        clone_hot_db()
        copy_day_stock()
