import hashlib
from urllib.parse import unquote

from flask import Flask, url_for, request, render_template

# from money_fluent import excute
# from wechat_utl import WeChatPub
#
# wechat = WeChatPub()
from wx import WXBizMsgCrypt

app = Flask(__name__)

@app.route('/robot', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # print(request.url)
        nonce=request.args.get('nonce')
        signature=request.args.get('msg_signature')
        timestamp=request.args.get('timestamp')
        data = request.data
        token = "lPGx80LMeIvkQvS7oIqhPVJOt5FSuz"
        sEncodingAESKey = "cErjBfNfr8hEAv2DpHmMDJPJvFmg2ESngAfvuIObmZf"
        sCorpID = "ww49433899fdbb10f8"
        wxcpt = WXBizMsgCrypt(token, sEncodingAESKey, sCorpID)
        # signature = "ba5b7200ecd10286f58f8df8cd2f896098b6e5e9"
        # timestamp = "1596292903"
        # nonce = "1596954841"
        # echostr = "pvtc%2FYjdND0%2FE7ia%2BCo71xND%2BQ%2BUil2sIoUrSYHajAuwICF0TYHOoy%2B7R5d1wNf3mILUsxdmPgHZ8akzdaewJA%3D%3D"
        # echostr = unquote(data)
        # sVerifyMsgSig=HttpUtils.ParseUrl("msg_signature")
        # ret = wxcpt.VerifyAESKey()
        # print ret
        # sVerifyEchoStr = "fsi1xnbH4yQh0+PJxcOdhhK6TDXkjMyhEPA7xB2TGz6b+g7xyAbEkRxN/3cNXW9qdqjnoVzEtpbhnFyq6SVHyA=="
        print(data)
        ret,msg = wxcpt.DecryptMsg(signature, timestamp, nonce, data)
        print(ret)
        if (ret != 0):
            print(msg)
            return msg
        # list = [token, timestamp, nonce]
        # list.sort()
        # sha1 = hashlib.sha1()
        # sha1.update(list[0].encode('utf-8'))
        # sha1.update(list[1].encode('utf-8'))
        # sha1.update(list[2].encode('utf-8'))
        # hashcode = sha1.hexdigest()
        # echostr = request.args.get("echostr")
        # if hashcode == signature:
        #     return echostr
        # else:
        #     return ""

        # print(request.url)
        # print(request.get_data())
        # args = request.args
        # code = args.get("code","")
        # type = args.get("type","")
        # # if request.form['user'] == 'admin':
        # #     return 'Admin login successfully!'
        # # else:
        # try:
        #     excute(wechat,code,type)
        # except:
        #     wechat.send_msg(f"http://18.163.236.133:10001/?code={code}&type={type}")
        # return 'No such user!'
    # title = request.args.get('title', 'Default')
    # return render_template('login.html', title=title)
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80,debug=False)