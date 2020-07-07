import time
import traceback

import pymysql

import setting
from wechat_utl import WeChatPub

black_list = ['"cls80410"', '"cls80358"', '"cls80366"', '"cls80368"', '"cls80360"', '"cls80272"', '"cls80361"',
              '"cls80359"',
              '"cls80250"']


def get_four_hot():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(
            f'''select t.theme_name, t.bef_degree_1,t.bef_degree_2,t.bef_degree_3,i.type 
                from theme_hot t join theme_info i on t.theme_code = i.theme_code where t.theme_code not in ({','.join(black_list)});''')
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()

    items = [[item[0], item[1] + item[2] + item[3], item[1], item[2], item[3], item[4]] for item in items if
             item[1] + item[2] + item[3] >= 5 and item[1] > 0 and item[2] >1 and  item[2] + item[3]>2]
    items_super_hot = [item for item in items if item[1] >= 7]
    items_hot = [item for item in items if item[1] < 7]

    items_super_hot = sorted(items_super_hot, key=lambda i: i[1], reverse=True)
    items_hot = sorted(items_hot, key=lambda i: i[1], reverse=True)
    return items_super_hot,items_hot


def main():
    ken = 30
    super_hot,hot = get_four_hot()
    super_hot_str = [f"{i[0]}\t{i[1]}\t{i[2]}\t{i[3]}\t{i[4]}\t{i[5]}" for i in super_hot]
    wechat = WeChatPub()
    epoc = int(len(super_hot_str)/ken)
    wechat.send_msg(f"超热总数:{len(super_hot)}")
    for i in range(epoc+1):
        time.sleep(3)
        wechat.send_msg("\n".join(super_hot_str[i*ken:(i+1)*ken]))
        print(i)

    hot_str = [f"{i[0]}\t{i[1]}\t{i[2]}\t{i[3]}\t{i[4]}\t{i[5]}" for i in hot]
    epocs = int(len(hot_str)/ken)
    time.sleep(3)
    wechat.send_msg(f"普热总数:{len(hot)}")
    for k in range(epocs):
        time.sleep(3)
        wechat.send_msg("\n".join(hot_str[k*ken:(k+1)*ken]))
        print(i)

if __name__ == '__main__':
    main()
