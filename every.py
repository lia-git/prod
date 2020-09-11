import datetime
# 判断 2018年4月30号 是不是节假日
import json
import multiprocessing
import time
import traceback
import pandas as pd
import pymysql
import redis
import requests
from chinese_calendar import is_workday, is_holiday

import candicate_headers
import setting
import theme_base
from mylog import fetch_logger
from reply.pic_reply import reply_today_main_power
from stock_base import get_all_db, code_main_trend
from update_tmp_degree import get_tmp_theme_hot
from wechat_utl import WeChatPub
logger = fetch_logger("every")
rdp = redis.ConnectionPool(host='localhost', port=6379)


def get_all_stocks():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        for i in range(12, 1, -1):
            cursor.execute(f"select stock_code from stock_base;")
            items = cursor.fetchall()
            # 提交事务
            conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    return [item[0] for item in items]


def get_sina_info(code,time_col):
    url = f"http://hq.sinajs.cn/list={code}"
    resp = requests.get(url).text.split("=")[-1][1:-1].split(",")
    last, now = float(resp[2]), float(resp[3])
    pct = round(100 * (now - last) / last, 2)
    update_stock_base(code, now, pct,time_col)
    # return [code, now, pct]


def update_stock_intime(time_col):
    s = time.time()
    codes = get_all_stocks()
    logger.info(time.time()-s)
    ret = []
    pool = multiprocessing.Pool(processes=16)
    for code in codes:
        try:
            ret.append(pool.apply_async(get_sina_info, (code,time_col)))
            # ret.append([code, now, pct])
            # logger.info(time.time() - s)
            # update_stock_base(code, now, pct)
        except Exception as e:
            # 有异常，回滚事务
            traceback.print_exc()
            continue
    pool.close()
    pool.join()
    logger.info(time.time()-s)


def update_stock_base(code, now, pct,time_col):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    if time_col in ["0930","1430"]:
        sql_ = f"select price_{time_col} from stock_base  where stock_code = '{code}'"
        cursor.execute(sql_)
        item = cursor.fetchone()[0]
        sp = f"{item},{now}" if item else f"{now}"
        tiny_sql = f",price_{time_col} = '{sp}'"
    else:
        tiny_sql =''

    try:
        # for code, now, pct in ret:
        sql = f'''
                        update stock_base set change_pct = {pct} ,last_price = {now}  {tiny_sql} 
                        where stock_code = '{code}';
                    '''
        # if ",price_" in sql:
        #     logger.info(sql)
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        logger.info(sql)
        logger.error(traceback.format_exc())
        conn.rollback()
    cursor.close()
    conn.close()


def get_select_theme_change():

    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        sql = f''' select th.theme_code, th.theme_name,th.tmp_degree,th.bef_degree_1,th.bef_degree_2,th.bef_degree_3,th.bef_degree_4,th.bef_degree_5,tm.stock_names from theme_hot th join theme_stocks_map tm
                on th.theme_code = tm.theme_code  where th.theme_code not in ({','.join(setting.black_list)}) ;
                      '''
        cursor.execute(sql)
        ret = cursor.fetchall()
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        logger.info(sql)
        traceback.print_exc()
        conn.rollback()
    try:
        # 执行SQL语句
        cursor.execute(
            f"select stock_code,change_pct from stock_base  ;")
        candits = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    cursor.close()
    conn.close()
    limit_candits = set([can[0] for can in candits if can[1]>= 9.84])

    second_candits = set([can[0] for can in candits if 5<=can[1] < 9.84])
    high_candits = set([can[0] for can in candits if 1.8 <= can[1] < 5])
    low_candits = set([can[0] for can in candits if can[1]<1.8])
    ret_ = []
    for item in ret:
        limit_set = set(item[-1].split(".")) & limit_candits if item[-1] else set([])
        second_set = set(item[-1].split(".")) & second_candits if item[-1] else set([])
        high_set = set(item[-1].split(".")) & high_candits if item[-1] else set([])
        low_set = set(item[-1].split(".")) & low_candits if item[-1] else set([])
        record= [int(item[2].strip(",").split(",")[0]),item[:-1],[str(len(limit_set))
            ,str(len(second_set)),str(len(high_set))],get_names_order(limit_set),get_names_order(second_set),get_names_order(high_set),get_names_order(low_set)]
        ret_.append(record)
    final = ret_

    return final,(len(limit_candits),len(second_candits),len(high_candits)),(safe_length(limit_candits),safe_length(second_candits),safe_length(high_candits))

def safe_length(candi):
    i = 0
    for c in candi:
        if "sz300" not in c:
            i +=1
    return i


def get_names_order(codes):
    if not codes:
        return []
    code_str  =",".join([f"'{code}'" for code in codes])
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(
            f"select stock_name,change_pct from stock_base  where stock_code in ({code_str}) and  stock_code not  like 'sz300%' order by change_pct desc")
        ret = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    return [f"{i[0]}/{i[1]}" for i in ret]



def set_tmp_null():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        sql = ' update stocks.theme_hot set tmp_degree=null where 1;'
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        logger.info(sql)
        traceback.print_exc()
        conn.rollback()
        cursor.close()
        conn.close()


def check(lst):
    ls_ = lst.split(",")
    ls = []
    for ix,s in enumerate(ls_):
        if ls:
            if s != ls[-1]:
                ls.append(s)
        else:
            ls.append(s)
        if ix == len(ls_) -33:
            ls.append("#")
    return ",".join(ls)


def to_file(res,name,flag=True):
    # stocks = {}
    # with open("master.txt") as reader:
    #     for line in reader:
    #         code,name_ = line.strip().split("\t")
    #         stocks[code.lower()] = name_
    if flag:
        # setting.get_value(item[1][2:]),
        # res_ = [[item[1][0],setting.get_value(item[1][2:]),str(item[1][2:6][::-1]),int(item[0]),check(item[1][1]),",".join(item[2]),f"{len(item[3])}:{','.join(item[3])}",f"{len(item[4])}:{','.join(item[4][:15])}",f"{len(item[5])}:{','.join(item[5][:15])}",f"{len(item[6])}:{','.join(item[6][:15])}",] for item in res]
        # res_ = sorted(res_,key=lambda i:i[3],reverse=True)
        # df = pd.DataFrame(res_,columns=["版块","超热","近期指标","最新","涨停趋势","上涨分布","涨停","高位","中位","低位"])
        res_ = [["pct_"+item[1][0],item[1][1],setting.get_value(item[1][3:]),str(item[1][3:7][::-1]),int(item[0]),check(item[1][2]),",".join(item[2]),f"{len(item[3])}:{','.join(item[3])}",f"{len(item[4])}:{','.join(item[4][:15])}",f"{len(item[5])}:{','.join(item[5][:15])}",f"{len(item[6])}:{','.join(item[6][:15])}",] for item in res]
        res_ = sorted(res_,key=lambda i:i[4],reverse=True)
        df = pd.DataFrame(res_,columns=["代码","版块","超热","近期指标","最新","涨停趋势","上涨分布","涨停","高位","中位","低位"])
    else:
        df = pd.DataFrame(res)
    df.to_excel(name)

def get_headers(today):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")  # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(
            f"select b.stock_name,b.last_price,b.change_pct,h.limit_count,h.days,h.reason,b.description,h.recent_time from stock_base b join stock_headers h on b.stock_code = h.stock_code where recent_time > '{today}' order by recent_time desc,h.days asc,h.limit_count desc ;")
        ret = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    return ret

def update_theme_pct(moment):
    all_theme_pct = theme_base.get_all_themes(True)
    update_redis_theme_pct(all_theme_pct,moment)



def update_main_trend(moment):
    try:
        all_stocks  = get_all_db(False)
        logger.info("DB OK")
        code_list = [ele[0] for ele in all_stocks]
        code_main_trend(code_list,moment,logger)
        logger.info("TRend OK")
    except Exception as e:
            # 有异常，回滚事务
         logger.info(traceback.format_exc())
    # update_redis_main_trend(code_trend,moment)



def update_count_limit(moment,count):
    r = redis.StrictRedis(connection_pool=rdp,decode_responses=True)
    key = "all_limit_count"
    if not r.exists(key):
        pre_change_dict = {moment: count}
    else:
        pre_change_dict = json.loads(r.get(key))
        pre_change_dict[moment] =count
    r.set(key, json.dumps(pre_change_dict, ensure_ascii=False))
    # if moment[-4:] == "1500":
    if True:
        moment_ = moment[:-4]
        key_ = "day_limit_count"
        if not r.exists(key_):
            change_dict = {moment_: count}
        else:
            change_dict = json.loads(r.get(key_))
            change_dict[moment_] = count
        r.set(key_, json.dumps(change_dict, ensure_ascii=False))



def update_redis_main_trend(code_trend,moment):
    r = redis.StrictRedis(connection_pool=rdp,decode_responses=True)
    for code,trend,last_trend in code_trend:
        pivot_key = f"trend_{code}_pivot"
        change_key = f"trend_{code}_change"
        last_key = f"trend_{code}_last"
        # pre_change_list = []
        if not r.exists(pivot_key):
            r.set(pivot_key,last_trend)
        else:
            last_trend = float(r.get(pivot_key))
        if not r.exists(change_key):
            last_trend_change_dict = {moment:last_trend}
        else:
            last_trend_change_dict = json.loads(r.get(change_key))
            val =last_trend + trend
            last_trend_change_dict[moment] = val
            r.set(last_key,val)
        r.set(change_key,json.dumps(last_trend_change_dict,ensure_ascii=False))

def update_redis_theme_pct(all_pct,moment):
    r = redis.StrictRedis(connection_pool=rdp,decode_responses=True)
    for theme_pct in all_pct:
        pivot_key = f"pct_{theme_pct['theme_code']}_pivot"
        change_key = f"pct_{theme_pct['theme_code']}_change"
        last_key = f"pct_{theme_pct['theme_code']}_last"
        pre_pivot =0.1
        # pre_change_list = []
        if not r.exists(pivot_key):
            r.set(pivot_key,pre_pivot)
        else:
            pre_pivot = float(r.get(pivot_key))
        if not r.exists(change_key):
            pre_change_dict = {moment:pre_pivot}
        else:
            pre_change_dict = json.loads(r.get(change_key))
            val =round(pre_pivot * (1.0 + theme_pct["change_pct"]/100),3)
            pre_change_dict[moment] = val
            r.set(last_key,val)
        r.set(change_key,json.dumps(pre_change_dict,ensure_ascii=False))


def reset_pivot():
    r = redis.StrictRedis(connection_pool=rdp,decode_responses=True)
    theme_list = r.keys("*_last")
    for theme_last in theme_list:
        last_val = r.get(theme_last)
        # logger.info(f"{theme_last}pivot")
        r.set(theme_last.decode()[:-4]+"pivot",last_val)

def main():
    wechat = WeChatPub()
    start = time.time()
    today = datetime.date.today()
    # wechat.send_remind()
    if is_workday(today):
    # if True:
        time_now = datetime.datetime.now()
        logger.info(time_now)
        hour, minute = time_now.hour, time_now.minute
        if hour == 6 and 30 < minute < 35:
            wechat.send_msg("TODAY IS OK")
        if hour == 8 and 15 < minute < 17:
            wechat.send_msg("REBOOT IS OK")
        if hour in [7] and 30 < minute < 35:
        # if hour in [7,18] and  minute < 35:
            if minute % 3==0:
                set_tmp_null()
                reset_pivot()
                # update_mater_stocks()
                wechat.send_msg(f'开盘热度置空,重置REDIS PIVOT, Done--{int(time.time() -start)}s')
        if hour in (12,17,19,21) and  0<= minute <= 4:
        # if hour in (17,11,8,20) and minute < 49:
            if minute % 3 ==0:
                candicate_headers.main()
                # reply_today_main_power()
                file_name = str(time_now).replace("-", "").replace(":", "").replace(" ", "")[:12]
                header_info = get_headers(str(time_now)[:10])
                to_file(header_info, f"result/headers_{file_name}.xlsx",flag=False)
                wechat.send_file(f"result/headers_{file_name}.xlsx")
        file_name = str(time_now).replace("-", "").replace(":", "").replace(" ", "")[:12]

        if hour ==9 and 25<=minute<=30:
            update_main_trend(file_name)
        if hour in [10, 13, 14] or (hour == 11 and 0 <= minute <=33) or (hour == 9 and minute >= 30) or (hour in (15,) and minute < 6):
            update_theme_pct(file_name)
            logger.info(f"hour={hour},miniute ={minute}")
            # if (hour in (9,13) and minute % 3 ==0) or minute % 5==0:
            if minute % 3 ==0:
                # if hour ==13:
                #     wechat.send_remind()
                #
                # if hour == 9:
                #     logger.info("GOOD")
                #     wechat.send_remind("强提醒：10:00之前必须卖出")
            # if minute % 4 == 0 and minute % 6 !=0:
                update_stock_intime(file_name[-4:])
                # t1 = time.time()
                # wechat.send_msg(f"更新股价：{int(t1 -start)}s")
                update_main_trend(file_name)

                get_tmp_theme_hot()
                # t2 = time.time()
                # wechat.send_msg(f"更新日内临时热度：{int(t2 -t1)}s")
                ret,limit_count,safe_count = get_select_theme_change()
                to_file(ret,f"result/{file_name}.xlsx")
                update_count_limit(file_name,limit_count[0])
                wechat.send_msg(f"上涨分布{int(time.time() -start)}s:{limit_count}-{safe_count}")
                if minute in [0,30]:
                    wechat.send_file(f"result/{file_name}.xlsx")

    # update_custom_db()
    logger.info("complete")


if __name__ == '__main__':
    main()
    # schedule.every().minutes.do(main)
    # while True:
    #     # logger.info(f"now_ is {time.time()}")
    #     schedule.run_pending()
    # t = time.time()
    # update_main_trend("202008152018")
    # logger.info(time.time()-t) #cd workspace/prod && git pull origin master