import json
import time
import traceback

import pymysql
import redis
from pyecharts.charts import Line, Page
from pyecharts import options as opts

import setting
from mylog import fetch_logger
from wechat_utl import WeChatPub_2 as WeChatPub
logger = fetch_logger("picture")

# plt.rcParams['font.sans-serif']=['simhei'] #用来正常显示中文标签
# plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
# import datetime as dt

def reply_dragon_trend():
    codes,names = zip(*get_dragon_code())
    # logger.info(codes,names)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    lines = []
    page = Page(layout=Page.SimplePageLayout)
    for ix,code in enumerate(codes):
        key = f'trend_{code}_change'
        v = r.get(key)
        if not v :
            continue
        logger.info(key)
        pcts = json.loads(v)
        # logger.info(pcts)

        # pcts =[float(p_str) for p_str in pct_str]
        # logger.info(pcts.values())
        # name = "全市场"
        line = (
            Line(init_opts=opts.InitOpts(height="500px",width="1800px",js_host="/js/",page_title=names[ix]))
                .add_xaxis(list(pcts.keys()))
                .add_yaxis(names[ix], list(pcts.values()))
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(title_opts=opts.TitleOpts(title=f"{names[ix]}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts.values()),max_=max(pcts.values()),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
        )
        # lines.append(line)
        page.add(line)
    name_ = f'all_dragon{int(time.time())}'
    page.render(path=f"templates/{name_}.html",)
    content = {"code":f"所有龙头主力动向","desc":"关注龙头主力走势","url":f"http://120.79.164.150:8080/show/{name_}"}
    logger.info(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)

def reply_stock_main_power(name):
    code = get_stock_code(name)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    title = "日内"
    key = f'trend_{code}_change'
    pcts = json.loads(r.get(key))
    # pcts =[float(p_str) for p_str in pct_str]
    # logger.info(pcts.)
    # name = "全市场"
    line = (
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, list(pcts.values()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"{name}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts.values()),max_=max(pcts.values()),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    name_ = f"{key}{int(time.time())}"
    line.render(path=f"templates/{name_}.html")
    content = {"code":f"{name}主力动向","desc":f"{code}-{name}走势","url":f"http://120.79.164.150:8080/show/{name_}"}
    logger.info(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)


def reply_today_main_power():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    # title = "日内"
    key = 'tom_selected'
    names_ = json.loads(r.get(key))
    if not names_:
        return 0
    code_list,names = zip(*get_select_code(names_))
    logger.info(code_list)
    page = Page(layout=Page.SimplePageLayout)

    for ix, code in enumerate(code_list):
        trend_key = f'trend_{code}_change'
        logger.info(trend_key)
        pcts = json.loads(r.get(trend_key))
        if pcts:
            line = (
                Line(init_opts=opts.InitOpts(height="500px",width="1800px",js_host="/js/",page_title=names[ix]))
                    .add_xaxis(list(pcts.keys()))
                    .add_yaxis(names[ix], list(pcts.values()))
                    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                    .set_global_opts(title_opts=opts.TitleOpts(title=f"{names[ix]}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts.values()),max_=max(pcts.values()),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
            )
            # lines.append(line)
            page.add(line)
    #     record_list = [[k,v]for k,v in record.items()]
    #     record_list = sorted(record_list,key= lambda i:i[0],reverse=False)
    #     if len(record.keys()) <= max_len:
    #         max_len = len(record.keys())
    #     records.append(record_list)
    #     final_names.append(name_list[ix])
    # key = []
    # vals = []
    # for record in records:
    #     k,v = zip(*record)
    #     key = k[-max_len:]
    #     if max_val < max(v[-max_len:]):
    #         max_val = max(v[-max_len:])
    #     if min_val > min(v[-max_len:]):
    #         min_val = min(v[-max_len:])
    #
    #     vals.append(v[-max_len:])
        # final.append(record[:max_len])

    # keys_ = final[0].keys()
    # keys = sorted(keys_,reverse=False)
    # # pcts =[float(p_str) for p_str in pct_str]
    # for key in keys:
    #     for record in records:
    #
    # logger.info(pcts.values())
    name = "自选池主力变化"
    # line_op = Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name)).add_xaxis(key)
    # for ix,v in enumerate(vals):
    #     line_op = line_op.add_yaxis(final_names[ix], v)
    # line = (line_op.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    #         .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min_val,max_=max_val,axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    # )
    h_name = f"pool{int(time.time())}"
    page.render(path=f"templates/{h_name}.html")
    content = {"code":f"{name}动向","desc":"关注主力走势","url":f"http://120.79.164.150:8080/show/{h_name}"}
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
    line = (
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, list(pcts.values()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts.values()),max_=max(pcts.values()),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    h_name = f"{change_key}{int(time.time())}"
    line.render(path=f"templates/{h_name}.html")
    content = {"code":f"整个{title}市场变化","desc":"关注大盘走势","url":f"http://120.79.164.150:8080/show/{h_name}"}
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
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(range(l)))
            .add_yaxis(name, tmp_degree)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(tmp_degree),max_=max(tmp_degree),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    html_name = f"day{int(time.time())}"
    line.render(path=f"templates/{html_name}.html")
    content = {"code":f"{code}-{name}","desc":"日间涨停变化趋势","url":f"http://120.79.164.150:8080/show/{html_name}"}
    wechat = WeChatPub()
    wechat.send_markdown(content)


def reply_theme_limit_change(code):
    name,tmp_degree = get_tmp_degree(code)
    tmp_degree =[ int(i) for i in tmp_degree.split(",")][::-1]
    l = len(tmp_degree)
    line = (
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(range(l)))
            .add_yaxis(name, tmp_degree)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(tmp_degree),max_=max(tmp_degree),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    h_name = f"limit{int(time.time())}"
    line.render(path=f"templates/{h_name}.html")
    content = {"code":f"{code}-{name}","desc":"涨停变化趋势","url":f"http://120.79.164.150:8080/show/{h_name}"}
    wechat = WeChatPub()
    wechat.send_markdown(content)


def reply_block_pct(code):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    change_key = f"pct_{code}_change"
    pcts = json.loads(r.get(change_key))
    # pcts =[float(p_str) for p_str in pct_str]
    logger.info(pcts.values())
    name,desc = get_name(code)
    line = (
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="/js/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, list(pcts.values()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts.values()),max_=max(pcts.values()),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    h_name = f"{change_key}{int(time.time())}"
    line.render(path=f"templates/{h_name}.html")
    content = {"code":f"{code}-{name}","desc":desc,"url":f"http://120.79.164.150:8080/show/{h_name}"}
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


def get_dragon_code():
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        sql = f"select stock_code,stock_name from stock_base where head_theme is not null and head_theme !='' and stock_code not  like 'sz300%' and stock_name not like '%ST%'  and last_price between 4.0 and 50;"
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

def get_stock_code(name):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        sql = f"select stock_code from stock_base where stock_name = '{name}';"
        logger.info(sql)
        cursor.execute(sql)
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    logger.info(item)
    return item[0]

def get_select_code(name_list):
    name_str = ",".join([f"'{name}'" for name in name_list ])
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象

    cursor = conn.cursor()
    try:
        # 执行SQL语句
        sql =f"select stock_code,stock_name from stock_base where stock_name in ({name_str});"
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