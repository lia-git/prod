import traceback

import pymysql

import setting
from wechat_utl import WeChatPub


def reply_stock_info(name):
    item = get_stock(name)
    name = item[2]
    wechat = WeChatPub()
    wechat.send_remind(title=name,content="<br>".join(item[3:]))

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
    print(item,flush=True)
    return [str(i) for i in  item]

