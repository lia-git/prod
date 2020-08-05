import time
import traceback

import pymysql
import redis
from pyecharts.charts import Line
from pyecharts import options as opts

import setting
from wechat_utl import WeChatPub

# plt.rcParams['font.sans-serif']=['simhei'] #用来正常显示中文标签
# plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
# import datetime as dt

def reply_block_pct(code):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    change_key = f"pct_{code}_change"
    pct_str = r.get(change_key).split(",")
    pcts =[float(p_str) for p_str in pct_str]
    print(pcts)
    name,desc = get_name(code)
    line = (
        Line(init_opts=opts.InitOpts(height="700px",page_title=name))
            .add_xaxis(list(range(len(pcts))))
            .add_yaxis(name, pcts)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=f"版块{name}趋势"),yaxis_opts=opts.AxisOpts(type_="value", min_=min(pcts),max_=max(pcts),axistick_opts=opts.AxisTickOpts(is_show=True),splitline_opts=opts.SplitLineOpts(is_show=True)))
    )
    line.render(path=f"templates/{change_key}{int(time.time())}.html")
    content = {"code":f"{code}-{name}","desc":desc,"url":f"http://ec2-18-163-236-133.ap-east-1.compute.amazonaws.com/show/{change_key}{int(time.time())}"}
    print(content)
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
    return item[0]
