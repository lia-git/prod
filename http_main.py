from flask import Flask, request, render_template
import xml.etree.cElementTree as ET
import setting
from reply.pic_reply import reply_block_pct, reply_all_limit_change, reply_theme_limit_change, \
    reply_theme_day_limit_change, reply_today_main_power, reply_stock_main_power, reply_dragon_trend, \
    reply_today_uppest_power
from reply.text_reply import reply_stock_info, set_custom_tom, store_buy_stock
from wx import WXBizMsgCrypt

app = Flask(__name__,static_folder="js")

@app.route('/robot', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # print(request.url)
        # reply_block_pct('cls80054')

        nonce=request.args.get('nonce')
        signature=request.args.get('msg_signature')
        timestamp=request.args.get('timestamp')
        data = request.data
        token = "lPGx80LMeIvkQvS7oIqhPVJOt5FSuz"
        sEncodingAESKey = "cErjBfNfr8hEAv2DpHmMDJPJvFmg2ESngAfvuIObmZf"
        sCorpID = setting.corp_id
        wxcpt = WXBizMsgCrypt(token, sEncodingAESKey, sCorpID)
        ret,msg = wxcpt.DecryptMsg( data,signature, timestamp, nonce)
        xml_tree = ET.fromstring(msg)
        content = xml_tree.find("Content").text
        if (ret == 0):
            print(content)
            if "big_dragon" == content.strip():
                # 板块涨幅变化情况
                reply_dragon_trend()
            elif "get_today" == content.strip():
                # 板块涨幅变化情况
                reply_today_main_power()
            elif "get_up" == content.strip():
                # 板块涨幅变化情况
                reply_today_uppest_power()
            elif "trend:" in content.strip():
                # 板块涨幅变化情况
                reply_stock_main_power(content[6:])
            elif "buy:" in content.strip():
                # 板块涨幅变化情况
                store_buy_stock(content[4:])
            elif "pct_" in content[:8]:
                # 板块涨幅变化情况
                reply_block_pct(content[4:])
            elif "all_day" in content:
                # 大盘涨停趋势情况
                reply_all_limit_change(day=True)
            elif "all" in content:
                # 大盘涨停趋势情况
                reply_all_limit_change()
            elif "limit_" in content[:8]:
                # 板块日内涨停趋势情况
                reply_theme_limit_change(content[6:])
            elif "day_" in content[:5]:
                # 板块日间涨停趋势情况
                reply_theme_day_limit_change(content[4:])
            elif "TOM:" in content[:5].upper():
                # 板块日间涨停趋势情况
                set_custom_tom(content[4:].strip().upper())
            else:
                reply_stock_info(content)
            #     return 0
            return "0"

@app.route('/show/<string:id>/')
def get_html(id):
    # print(id+"kkkkkkkkkk")
    # return app.send_static_file(f'html/{id}.html')
    return render_template(f'{id}.html')
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080,debug=True)