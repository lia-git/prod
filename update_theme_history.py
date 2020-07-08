import traceback

import pymysql

import setting


def clone_hot_theme():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        for i in range(12, 1, -1):
            cursor.execute(f"update theme_hot set bef_degree_{i} = bef_degree_{i - 1} where 1;")
            # 提交事务
            conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()


def copy_day_theme():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
            cursor.execute(f"select theme_code, tmp_degree from theme_hot;")
            items = cursor.fetchall()
            # 提交事务
            conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    for code, hot_num in items:
        if hot_num:
            try:
                # 执行SQL语句
                first = hot_num.split(",")[0]
                cursor.execute(f"update theme_hot set bef_degree_1 = {first} where theme_code = '{code}';")
                # 提交事务
                conn.commit()
            except Exception as e:
                # 有异常，回滚事务
                traceback.print_exc()
                conn.rollback()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    clone_hot_theme()
    copy_day_theme()
