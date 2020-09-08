import datetime
import json
import time
import traceback

import pymysql
import redis

import setting
from wechat_utl import WeChatPub
import pandas as pd



def get_four_hot():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(
            f'''select i.theme_code,t.theme_name, t.bef_degree_1,t.bef_degree_2,t.bef_degree_3,t.bef_degree_4,t.bef_degree_5,i.type 
                from theme_hot t join theme_info i on t.theme_code = i.theme_code where t.theme_code not in ({','.join(setting.black_list)});''')
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()

    items = [[item[0],item[1], setting.get_value(item[2:5]),  item[2], item[3], item[4], item[5], item[6], item[7]] for item in items ]
    items_super_hot = [item for item in items if item[2] >= 7]
    items_hot = [item for item in items if item[2] < 7]

    items_super_hot = sorted(items_super_hot, key=lambda i: i[3], reverse=True)
    items_hot = sorted(items_hot, key=lambda i: i[3], reverse=True)
    return items_super_hot,items_hot

def to_file(res,name,flag=True):
    # res_ = [[item[1][0],str(item[1][2:][::-1]),item[0],item[1][1]] for item in res]
    if flag:
        df = pd.DataFrame(res,columns=["代码","版块","总热点","今天","昨天","前天","4th","5th","类型"])
    else:
        df = pd.DataFrame(res)
    df.to_excel(name)
    print()

def write_super_block_num(num,moment):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    key = f'super_block_num'

    if not r.exists(key):
        change_dict = {moment: num}
    else:
        change_dict = json.loads(r.get(key))
        change_dict[moment] = num
    r.set(key, json.dumps(change_dict, ensure_ascii=False))


def main():
    today = str(datetime.date.today())
    super_hot,hot = get_four_hot()
    to_file(super_hot,f'day_hot/super-{today}.xlsx')
    to_file(hot,f'day_hot/normal-{today}.xlsx')
    write_super_block_num(len(super_hot), today.replace("-",""))

    wechat = WeChatPub()
    wechat.send_file(f'day_hot/super-{today}.xlsx')
    wechat.send_file(f'day_hot/normal-{today}.xlsx')
    # shorts = get_today_short()
    # to_file(shorts,f'day_hot/short-{today}.xlsx',False)
    # wechat.send_file(f'day_hot/short-{today}.xlsx')

if __name__ == '__main__':
    main()
