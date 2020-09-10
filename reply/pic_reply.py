import datetime
import json
import multiprocessing
import time
import traceback
import pandas as pd
import pymysql
import redis
from pyecharts.charts import Line, Page, Bar
from pyecharts import options as opts

import setting
from mylog import fetch_logger
from wechat_utl import WeChatPub_2 as WeChatPub
logger = fetch_logger("picture")

# plt.rcParams['font.sans-serif']=['simhei'] #用来正常显示中文标签
# plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
# import datetime as dt


def check_():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    key = f'trend_time'
    now = int(time.time())
    if r.exists(key):
        v = r.get(key)
        # logger.info(key)
        time_1 = int(v)
    else:
        time_1 = now
    r.set(key, str(now))
    logger.info(f"{now - time_1}s")
    if 0< now - time_1 < 7:
        return True
    else:
        return False



#
# def reply_dragon_trend():
#     if check_():
#         return
#     rg = [4,5,6.8,7.1,8,10,15,20,30,100]
#
#     pool = multiprocessing.Pool(processes=10)
#     for ix in range(len(rg)-1):
#         try:
#             # ret.append(get_cls_info(code))
#
#             pool.apply_async(part_dragon_trend, (rg[ix],rg[ix+1]))
#             # ret.append([code, now, pct])
#             # print(time.time() - s)
#             # update_stock_base(code, now, pct)
#         except Exception as e:
#             # 有异常，回滚事务
#             traceback.print_exc()
#             continue
#     pool.close()
#     pool.join()


def reply_dragon_trend():
    if check_():
            return
    # for i in range(6):
    #     logger.info(f"offset {i}")
    # try:
    codes,names,cmcs,ups = zip(*get_dragon_code_sp())
    # logger.info(codes,names)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    cnt = 0
    page = Page(layout=Page.SimplePageLayout,page_title="行业龙头池")
    for ix,code in enumerate(codes):
        key = f'trend_{code}_change'
        try:
            if r.exists(key):
                v = r.get(key)
                # logger.info(key)
                pcts = json.loads(v)
                # logger.info(pcts)

                # pcts =[float(p_str) for p_str in pct_str]
                # logger.info(pcts.values())
                # name = "全市场"
                vals_ = [(v - min(pcts.values()))/1000 for v in pcts.values()]
                # if round(max(vals_)/cmcs[ix],5) > 0.05:
                #     continue
                line = (
                    Bar(init_opts=opts.InitOpts(height="500px",width="2100px",js_host="/js/",page_title=names[ix]))
                        .add_xaxis(list(pcts.keys()))
                        .add_yaxis(names[ix], vals_)
                        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"{names[ix]}-{ups[ix]}-{cmcs[ix]}-{round(max(vals_)/cmcs[ix],5)}-{round(vals_[-1]/cmcs[ix],5)}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=0,max_=max(vals_),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
                )
                # lines.append(line)
                cnt += 1
                page.add(line)
        except:
            continue
    name_ = f'dragon{int(time.time())}'
    page.render(path=f"templates/{name_}.html")
    content = {"code":f"所有龙头-{cnt}动向","desc":"关注龙头主力走势","url":f"http://182.254.205.123:8080/show/{name_}"}
    # logger.info(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)
        # except:
        #     logger.info(str(traceback.format_exc()))
        #     continue
def reply_all_trend():
    if check_():
            return
    for i in range(4):
        logger.info(f"offset {i}")
        try:
            codes,names,cmcs,ups = zip(*get_dragon_code(i*800))
            # logger.info(codes,names)
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            cnt = 0
            page = Page(layout=Page.SimplePageLayout,page_title="全部股票池")
            for ix,code in enumerate(codes):
                key = f'trend_{code}_change'
                try:
                    if r.exists(key):
                        v = r.get(key)
                        # logger.info(key)
                        pcts = json.loads(v)
                        # logger.info(pcts)

                        # pcts =[float(p_str) for p_str in pct_str]
                        # logger.info(pcts.values())
                        # name = "全市场"
                        vals_ = [(v - min(pcts.values()))/1000 for v in pcts.values()]
                        # if round(max(vals_)/cmcs[ix],5) > 0.05:
                        #     continue
                        line = (
                            Bar(init_opts=opts.InitOpts(height="500px",width="2100px",js_host="/js/",page_title=names[ix]))
                                .add_xaxis(list(pcts.keys()))
                                .add_yaxis(names[ix], vals_)
                                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                                .set_global_opts(title_opts=opts.TitleOpts(title=f"{names[ix]}-{ups[ix]}-{cmcs[ix]}-{round(max(vals_)/cmcs[ix],5)}-{round(vals_[-1]/cmcs[ix],5)}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=0,max_=max(vals_),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
                        )
                        # lines.append(line)
                        cnt += 1
                        page.add(line)
                except:
                    continue
            name_ = f'dragon{int(time.time())}'
            page.render(path=f"templates/{name_}.html")
            content = {"code":f"全部股票池{i*800}-{(i+1)*800}动向","desc":"关注全部股票主力走势","url":f"http://182.254.205.123:8080/show/{name_}"}
            # logger.info(content)
            wechat = WeChatPub()
            wechat.send_markdown(content)
        except:
            logger.info(str(traceback.format_exc()))
            continue

def reply_stock_main_power(name):
    code,cmc,up = get_stock_code(name)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    title = "日内"
    key = f'trend_{code}_change'
    pcts = json.loads(r.get(key))
    # pcts =[float(p_str) for p_str in pct_str]
    logger.info(pcts.keys())
    # name = "全市场"
    vals_ = [(v - min(pcts.values()))/1000 for v in pcts.values()]
    logger.info(vals_)
    line = (
        Bar(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, vals_)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"{name}-{up}-{cmc}-{round(max(vals_)/cmc,5)}-{round(vals_[-1]/cmc,5)}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=0,max_=max(vals_),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    name_ = f"{key}{int(time.time())}"
    line.render(path=f"templates/{name_}.html")
    content = {"code":f"{name}主力动向","desc":f"{code}-{name}走势","url":f"http://182.254.205.123:8080/show/{name_}"}
    logger.info(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)


def reply_short_power():
    if check_():
            return
    code_list,names,cmcs,ups,prices = zip(*get_today_short())
    logger.info(code_list)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    page = Page(layout=Page.SimplePageLayout,page_title="SHORT_UP")
    cnt = 0
    file_table = []
    for ix, code in enumerate(code_list):
        try:
            trend_key = f'trend_{code}_change'
            if r.exists(trend_key):
                pcts = json.loads(r.get(trend_key))
                if len(pcts) <5:
                    continue
                logger.info(f"{ix}:{names[ix]}")
                vals_ = [(v - min(pcts.values()))/1000 for v in pcts.values()]
                # if round(max(vals_) / cmcs[ix], 5) > 0.05:
                #     continue
                line = (
                    Bar(init_opts=opts.InitOpts(height="500px",width="1800px",js_host="/js/",page_title=names[ix]))
                        .add_xaxis(list(pcts.keys()))
                        .add_yaxis(names[ix], vals_)
                        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"{names[ix]}-{ups[ix]}-{cmcs[ix]}-{round(max(vals_)/cmcs[ix],5)}-{round(vals_[-1]/cmcs[ix],5)}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=0,max_=max(vals_),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
                )
                # lines.append(line)
                # logger.info(trend_key)
                cnt += 1
                page.add(line)
                file_table.append([names[ix],cmcs[ix],ups[ix],prices[ix]])

        except:
            continue
    name = "超短主力变化"
    h_name = f"short{int(time.time())}"
    logger.info(h_name)
    page.render(path=f"templates/{h_name}.html")
    content = {"code":f"{name}{cnt}动向","desc":"关注超短走势","url":f"http://182.254.205.123:8080/show/{h_name}"}
    logger.info(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)
    to_file(file_table,f"ups/{h_name}.xlsx")
    wechat.send_file(f"ups/{h_name}.xlsx")

def reply_today_uppest_power(flag=False):
    if check_():
            return
    code_list,names,cmcs,ups,prices = zip(*get_uppest(flag))
    logger.info(code_list)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    page = Page(layout=Page.SimplePageLayout,page_title="TODAY_UP")
    cnt = 0
    file_table = []
    for ix, code in enumerate(code_list):
        try:
            trend_key = f'trend_{code}_change'
            if r.exists(trend_key):
                pcts = json.loads(r.get(trend_key))
                if len(pcts) <5:
                    continue
                logger.info(f"{ix}:{names[ix]}")
                vals_ = [(v - min(pcts.values()))/1000 for v in pcts.values()]
                # if round(max(vals_) / cmcs[ix], 5) > 0.05:
                #     continue
                line = (
                    Bar(init_opts=opts.InitOpts(height="500px",width="1800px",js_host="/js/",page_title=names[ix]))
                        .add_xaxis(list(pcts.keys()))
                        .add_yaxis(names[ix], vals_)
                        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"{names[ix]}-{ups[ix]}-{cmcs[ix]}-{round(max(vals_)/cmcs[ix],5)}-{round(vals_[-1]/cmcs[ix],5)}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=0,max_=max(vals_),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
                )
                # lines.append(line)
                # logger.info(trend_key)
                cnt += 1
                page.add(line)
                file_table.append([names[ix],cmcs[ix],ups[ix],prices[ix]])

        except:
            continue
    name = "自选池主力变化"
    h_name = f"pool{int(time.time())}"
    logger.info(h_name)
    page.render(path=f"templates/{h_name}.html")
    content = {"code":f"{name}{cnt}动向","desc":"关注主力走势","url":f"http://182.254.205.123:8080/show/{h_name}"}
    logger.info(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)
    to_file(file_table,f"ups/{h_name}.xlsx")
    wechat.send_file(f"ups/{h_name}.xlsx")


def to_file(res,name):
    # stocks = {}
    # with open("master.txt") as reader:
    #     for line in reader:
    #         code,name_ = line.strip().split("\t")
    #         stocks[code.lower()] = name_

    df = pd.DataFrame(res)
    df.to_excel(name)
    print()
def reply_today_main_power():
    if check_():
            return
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    # title = "日内"
    key = 'tom_selected'
    names_ = json.loads(r.get(key))
    if not names_:
        return 0
    code_list,names,cmcs,ups = zip(*get_select_code(names_))
    logger.info(code_list)
    page = Page(layout=Page.SimplePageLayout,page_title="近期题材")
    cnt = 0
    for ix, code in enumerate(code_list):
        trend_key = f'trend_{code}_change'
        try:
            if r.exists(trend_key):
                pcts = json.loads(r.get(trend_key))
                if len(pcts) <5:
                    continue
                logger.info(f"{ix}:{names[ix]}")
                vals_ = [(v - min(pcts.values()))/1000 for v in pcts.values()]
                if round(max(vals_) / cmcs[ix], 5) > 0.05:
                    continue
                line = (
                    Bar(init_opts=opts.InitOpts(height="500px",width="1800px",js_host="/js/",page_title=names[ix]))
                        .add_xaxis(list(pcts.keys()))
                        .add_yaxis(names[ix], vals_)
                        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                        .set_global_opts(title_opts=opts.TitleOpts(title=f"{names[ix]}-{ups[ix]}-{cmcs[ix]}-{round(max(vals_)/cmcs[ix],5)}-{round(vals_[-1]/cmcs[ix],5)}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=0,max_=max(vals_),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
                )
                # lines.append(line)
                # logger.info(trend_key)
                cnt += 1
                page.add(line)
        except:
            continue
    name = "自选池主力变化"
    h_name = f"pool{int(time.time())}"
    logger.info(h_name)
    page.render(path=f"templates/{h_name}.html")
    content = {"code":f"{name}{cnt}动向","desc":"关注主力走势","url":f"http://182.254.205.123:8080/show/{h_name}"}
    logger.info(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)


def reply_all_limit_change(day=False):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    title = "日内"
    if day:
        change_key = "day_limit_count"
        title = "日间"
    else:
        change_key = "all_limit_count"
    pcts = json.loads(r.get(change_key))
    # pcts =[float(p_str) for p_str in pct_str]
    logger.info(pcts.values())
    name = "全市场"
    vals_ = [v - 0 for v in pcts.values()]
    line = (
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, vals_)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=0,max_=max(vals_),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    h_name = f"{change_key}{int(time.time())}"
    line.render(path=f"templates/{h_name}.html")
    content = {"code":f"整个{title}市场变化","desc":"关注大盘走势","url":f"http://182.254.205.123:8080/show/{h_name}"}
    logger.info(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)

def reply_theme_day_limit_change(code):
    item = get_tmp_degree(code,pat="*")
    name = item[2]
    now_point = item[3].split(",")[0]
    final_points = list(item[4:-1])
    tmp_points =item[-1].split(",")[:-4]
    final_points.insert(0,now_point)
    final_points.extend(tmp_points)
    tmp_degree =[int(i) for i in final_points[::-1]]
    l = len(tmp_degree)
    line = (
        Bar(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(range(l)))
            .add_yaxis(name, tmp_degree)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(tmp_degree),max_=max(tmp_degree),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    html_name = f"day{int(time.time())}"
    line.render(path=f"templates/{html_name}.html")
    content = {"code":f"{code}-{name}","desc":"日间涨停变化趋势","url":f"http://182.254.205.123:8080/show/{html_name}"}
    wechat = WeChatPub()
    wechat.send_markdown(content)


def reply_theme_limit_change(code):
    name,tmp_degree = get_tmp_degree(code)
    tmp_degree =[ int(i) for i in tmp_degree.split(",")][::-1]
    l = len(tmp_degree)
    line = (
        Bar(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(range(l)))
            .add_yaxis(name, tmp_degree)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(tmp_degree),max_=max(tmp_degree),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    h_name = f"limit{int(time.time())}"
    line.render(path=f"templates/{h_name}.html")
    content = {"code":f"{code}-{name}","desc":"涨停变化趋势","url":f"http://182.254.205.123:8080/show/{h_name}"}
    wechat = WeChatPub()
    wechat.send_markdown(content)


def reply_block_pct(code):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    change_key = f"pct_{code}_change"
    pcts = json.loads(r.get(change_key))
    # pcts =[float(p_str) for p_str in pct_str]
    logger.info(pcts.values())
    name,desc = get_name(code)
    vals_ = [v - min(pcts.values()) for v in pcts.values()]
    line = (
        Bar(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, vals_)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=0,max_=max(vals_),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    h_name = f"{change_key}{int(time.time())}"
    line.render(path=f"templates/{h_name}.html")
    content = {"code":f"{code}-{name}","desc":desc,"url":f"http://182.254.205.123:8080/show/{h_name}"}
    # logger.info(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)


def get_name(code):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        sql = f"select theme_name,description from theme_info where theme_code = '{code}';"
        cursor.execute(sql)
        logger.info(sql)
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    logger.info(item)
    return item

def get_tmp_degree(code,pat="theme_name,tmp_degree"):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        sql = f"select {pat} from theme_hot where theme_code = '{code}';"
        logger.info(sql)

        cursor.execute(sql)
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # logger.info(f"SS{item}")
    return item


def get_dragon_code_sp():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    items = []
    try:
        # 执行SQL语句
        sql = f'''
                select stock_code,stock_name,cmc,change_pct from stock_base where head_theme != '' and  stock_code not  like 'sz300%'  and stock_name not like '%ST%'  and last_price >4.0 order by change_pct desc,cmc desc ;
                '''
        logger.info(sql)
        cursor.execute(sql)
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    logger.info(f"{len(items)}:{items[0]}")
    return items

def get_dragon_code(offset):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    items = []
    try:
        # 执行SQL语句
        sql = f'''
                select stock_code,stock_name,cmc,change_pct from stock_base where  stock_code not  like 'sz300%'  and stock_name not like '%ST%'  and last_price >4.0 order by cmc desc limit {offset},800;
                '''
        logger.info(sql)
        cursor.execute(sql)
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    logger.info(f"{len(items)}:{items[0]}")
    return items

def get_stock_code(name):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        sql = f"select stock_code,cmc,change_pct from stock_base where stock_name = '{name}';"
        logger.info(sql)
        cursor.execute(sql)
        item = cursor.fetchone()
        logger.info(item)
        return item

    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()

def get_uppest(flag):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    if flag:
        bd =" > 9.8 "
    else:
        bd =" between 2 and 9.8 "

    cursor = conn.cursor()
    try:
        # 执行SQL语句
        sql =f"select stock_code,stock_name,cmc,change_pct,last_price from stock_base where stock_code not  like 'sz300%'  and stock_name not like '%ST%'  and last_price between 4.0 and 50 and change_pct {bd} order by change_pct desc, cmc desc;"
        logger.info(sql)
        cursor.execute(sql)
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # logger.info(item)
    return items
def get_select_code(name_list):
    name_str = ",".join([f"'{name}'" for name in name_list ])
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象

    cursor = conn.cursor()
    try:
        # 执行SQL语句
        sql =f"select stock_code,stock_name,cmc,change_pct from stock_base where stock_name in ({name_str}) order by change_pct desc,cmc desc;"
        logger.info(sql)
        cursor.execute(sql)
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # logger.info(item)
    return items


def get_today_short():
    time_now = datetime.datetime.now()
    # logger.info(time_now)
    hour, minute = time_now.hour, time_now.minute
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user, password=setting.db_password,
                           database=setting.db_name, charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(
            f'''select stock_code,stock_name,price_0930,price_1430,cmc from stock_base where stock_code not  like 'sz300%'  and stock_name not like '%ST%'  and last_price between 4.0 and 50 order by cmc desc''')
        items = cursor.fetchall()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    ret = []
    for code,name,p_09,p_14,c in items:
        try:
            p9 = float(p_09.split(",")[-1])
            if hour <=14:
                p14 = float(p_14.split(",")[-1])
            else:
                p14 = float(p_14.split(",")[-2])
            shot_p = round((p9 - p14)/p14,5)
            if shot_p >= 0.013:
                ret.append([code,name,c,shot_p,p9])
        except:
            continue
    return ret
