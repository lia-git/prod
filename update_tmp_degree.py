import traceback

import pymysql

import setting


def get_all_uplimit():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(
            f"select stock_name from stock_base  where change_pct >= 9.9;")
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
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
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


def get_tmp_theme_hot():
    themes = get_all_themes()

    hots = get_all_uplimit()
    last_hot = get_last_hot()
    for theme in themes:
        limits = set(hots) & set(theme[4].split("."))
        # if limits:
        if theme[1] == "300843":
            print()
        update_db(theme[1], last_hot, len(limits), limits)


def get_last_hot():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象

    cursor = conn.cursor()
    try:
        # 执行SQL语句

        cursor.execute(
            f"select theme_code,tmp_degree from theme_hot ")
        items = cursor.fetchall()
        # cursor.execute(sql)
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()
    ret = {}
    for item in items:
        ret[item[0]] = item[1]
    return ret


def update_db(code, last_hot, hot_num_, stocks):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        tuple_ = last_hot[code]
        if tuple_:
            hot_num = tuple_.split(",")
            hot_num.insert(0, str(hot_num_))
            hot_num_str = ",".join(hot_num)
        else:
            hot_num_str = str(hot_num_)
            # hot_stocks_str = ",".join(stocks)

        cursor.execute(f"update theme_hot set tmp_degree = '{hot_num_str}' where theme_code = '{code}';")
        # cursor.execute(
        #     f"update themes_stocks_hot_history set tmp_stocks = '{hot_stocks_str}' where theme_code = '{code}';")

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
    get_tmp_theme_hot()
