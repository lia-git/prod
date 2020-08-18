import json
import time
import traceback

import pymysql
import redis
from pyecharts.charts import Line
from pyecharts import options as opts

import setting
from wechat_utl import WeChatPub_2 as WeChatPub

# plt.rcParams['font.sans-serif']=['simhei'] #用来正常显示中文标签
# plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
# import datetime as dt

def reply_stock_main_power(name):
    code = get_stock_code(name)
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    title = "日内"
    key = f'trend_{code}_change'
    pcts = json.loads(r.get(key))
    # pcts =[float(p_str) for p_str in pct_str]
    print(pcts.values())
    # name = "全市场"
    line = (
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="https://cdn.bootcss.com/echarts/4.8.0/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, list(pcts.values()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"{name}主力趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts.values()),max_=max(pcts.values()),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    line.render(path=f"templates/{key}{int(time.time())}.html")
    content = {"code":f"整个{name}主力动向","desc":"关注主力走势","url":f"http://120.79.164.150:8080/show/{key}{int(time.time())}"}
    print(content)
    wechat = WeChatPub()
    wechat.send_markdown(content)
def reply_today_main_power():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    title = "日内"
    key = 'tom_selected'
    pcts = json.loads(r.get(key))
    # pcts =[float(p_str) for p_str in pct_str]
    print(pcts.values())
    name = "全市场"
    line = (
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="https://cdn.bootcss.com/echarts/4.8.0/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, list(pcts.values()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts.values()),max_=max(pcts.values()),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    line.render(path=f"templates/{key}{int(time.time())}.html")
    content = {"code":f"整个{title}动向","desc":"关注主力走势","url":f"http://120.79.164.150:8080/show/{key}{int(time.time())}"}
    print(content)
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
    print(pcts.values())
    name = "全市场"
    line = (
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="https://cdn.bootcss.com/echarts/4.8.0/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, list(pcts.values()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts.values()),max_=max(pcts.values()),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    line.render(path=f"templates/{change_key}{int(time.time())}.html")
    content = {"code":f"整个{title}市场变化","desc":"关注大盘走势","url":f"http://120.79.164.150:8080/show/{change_key}{int(time.time())}"}
    print(content)
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
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="https://cdn.bootcss.com/echarts/4.8.0/",page_title=name))
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
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="https://cdn.bootcss.com/echarts/4.8.0/",page_title=name))
            .add_xaxis(list(range(l)))
            .add_yaxis(name, tmp_degree)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(tmp_degree),max_=max(tmp_degree),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    line.render(path=f"templates/limit{int(time.time())}.html")
    content = {"code":f"{code}-{name}","desc":"涨停变化趋势","url":f"http://120.79.164.150:8080/show/limit{int(time.time())}"}
    wechat = WeChatPub()
    wechat.send_markdown(content)


def reply_block_pct(code):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    change_key = f"pct_{code}_change"
    pcts = json.loads(r.get(change_key))
    # pcts =[float(p_str) for p_str in pct_str]
    print(pcts.values())
    name,desc = get_name(code)
    line = (
        Line(init_opts=opts.InitOpts(height="700px",width="1800px",js_host="https://cdn.bootcss.com/echarts/4.8.0/",page_title=name))
            .add_xaxis(list(pcts.keys()))
            .add_yaxis(name, list(pcts.values()))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts.values()),max_=max(pcts.values()),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    line.render(path=f"templates/{change_key}{int(time.time())}.html")
    content = {"code":f"{code}-{name}","desc":desc,"url":f"http://120.79.164.150:8080/show/{change_key}{int(time.time())}"}
    # print(content,flush=True)
    wechat = WeChatPub()
    wechat.send_markdown(content)


def get_name(code):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select theme_name,description from theme_info where theme_code = '{code}';")
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    print(item,flush=True)
    return item

def get_tmp_degree(code,pat="theme_name,tmp_degree"):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select {pat} from theme_hot where theme_code = '{code}';")
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    # print(f"SS{item}",flush=True)
    return item


def get_stock_code(name):
    conn = pymysql.connect(host="127.0.0.1", user=setting.db_user,password=setting.db_password,database=setting.db_name,charset="utf8")
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 执行SQL语句
        cursor.execute(f"select stock_code from stock_base where stock_name = '{name}';")
        item = cursor.fetchone()
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        traceback.print_exc()
        conn.rollback()
    print(item,flush=True)
    return item[0]