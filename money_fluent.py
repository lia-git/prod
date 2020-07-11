import traceback

import pymysql
from chinese_calendar import find_workday, is_workday
from jqdatasdk import *
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt

import setting
from wechat_utl import WeChatPub

auth('16675588993', 'JoinQuant233708')

plt.rcParams['font.sans-serif']=['simhei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def get_median(code, day1,day2):
    df = get_price(f'{code}', start_date=day1, end_date=day2,
                   frequency='minute', skip_paused=True,
                   fields=['open', 'close', 'money'])
    # 获得000001.XSHG的2015年01月的分钟数据, 只获取open+close字段
    df["money"] = df["money"] / 10000
    x = df["money"].quantile(0.75)


    # x = df["money"].mean()
    return x if x >100 else 100


def get_current(code, base, date, now):
    df = get_price(f'{code}', start_date=date, end_date=now,
                   frequency='minute', skip_paused=True,
                   fields=['open', 'close', 'money'])
    # 获得000001.XSHG的2015年01月的分钟数据, 只获取open+close字段
    df["money"] = df["money"] / 10000
    new = df.values.tolist()
    res = []
    val = 0
    for start, end, money in new:
        if money < base:
            if res:
                res.append(res[-1])
            else:
                res.append(0)
            continue
        if end >= start:
            val += money
        else:
            val -= money
        res.append(val)
    return res


def excute(wechat,code, start="", end=""):
    # def excute():
    suffix = "XSHG" if code[0] == "6" else "XSHE"
    name = get_stock(code)
    end_day =dt.date.today()  if not end else end
    end = dt.datetime.now()
    if not is_workday(end):
        start = find_workday(delta_days=-1)
    else:
        start = end_day

    # yesterday = find_workday(delta_days=-1, date=start)

    base = get_median(f"{code}.{suffix}", start,end)
    res = get_current(f"{code}.{suffix}", base, start, end)
    data = pd.Series(res)
    data.plot()
    plt.title(name)
    # plt.show()
    plt.savefig(f"img/{code}.png")
    plt.clf()
    wechat.send_file(f"img/{code}.png")


def get_stock(code):

    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select stock_name from stock_base where stock_code like '%{code}';")
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    return item[0]


if __name__ == '__main__':
    code = "000037"

    excute(code)

# import traceback
#
# import pymysql
#
# import setting
#
#
# def get_mapping():
#     conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
#                            database=setting.db_name, charset="utf8")
#     # 得到一个可以执行SQL语句的光标对象
#     cursor = conn.cursor()
#     try:
#         # 执行SQL语句
#         cursor.execute(f"select theme_name,stock_names from theme_stocks_map;")
#         items = cursor.fetchall()
#         # 提交事务
#         conn.commit()
#     except Exception as e:
#         # 有异常，回滚事务
#         traceback.print_exc()
#         conn.rollback()
#     cursor.close()
#     conn.close()
#     return [[item[0],set(item[1].split("."))] for item in items]
#
#
# def get_base():
#     conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
#                            database=setting.db_name, charset="utf8")
#     # 得到一个可以执行SQL语句的光标对象
#     cursor = conn.cursor()
#     items = None
#     try:
#         # 执行SQL语句
#         cursor.execute(f"select stock_name from stock_base;")
#         items = cursor.fetchall()
#         # 提交事务
#         conn.commit()
#     except Exception as e:
#         # 有异常，回滚事务
#         traceback.print_exc()
#         conn.rollback()
#     cursor.close()
#     conn.close()
#     return set([item[0] for item in items])
#
#
# def get_dragon():
#     names = []
#     with open("master.txt") as writer:
#         for line in writer:
#             l = line.strip().replace("、"," ").replace("("," ").replace("痕股份","北玻股份")\
#                 .replace("馳朗殳","绿地控股").replace("西砂峰","西藏珠峰").replace("爰迪尔","爱迪尔").replace("盲丽国际","宣亚国际").replace("皖新彳","皖新传媒").replace("宝菜特","宝莱特").replace("华北制约","华北制药").replace("寒锐钻业","寒锐钴业").replace("盛夭网络","盛天网络").replace("紫光国徽","紫光国微").replace("华锂矿业","华钰矿业").replace("约业","药业")\
#                 .replace("（"," ").replace("）"," ").replace(")"," ")
#             i_s = [i for i in l.split(",") if i]
#             names.extend(i_s)
#     return set([name for name in names if 5>len(name)>2])
#
#
#
# def main():
#
#
# if __name__ == '__main__':
#     names = get_dragon()
#     bases = get_base()
#     ret = names & bases
#     print(names & bases)
#     print(names - bases)
#     # with open("master.txt","a+") as file:
#     #     file.write(",".join(ret) + "\n")
#     print()
