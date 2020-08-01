import hashlib

from flask import Flask, url_for, request, render_template

# from money_fluent import excute
# from wechat_utl import WeChatPub
#
# wechat = WeChatPub()

app = Flask(__name__)

@app.route('/robot', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        signature=request.args.get('signature')
        timestamp=request.args.get('timestamp')
        nonce=request.args.get('nonce')
        token = "maluguang"
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        sha1.update(list[0].encode('utf-8'))
        sha1.update(list[1].encode('utf-8'))
        sha1.update(list[2].encode('utf-8'))
        hashcode = sha1.hexdigest()
        echostr = request.args.get("echostr")
        if hashcode == signature:
            return echostr
        else:
            return ""

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
        return 'No such user!'
    # title = request.args.get('title', 'Default')
    # return render_template('login.html', title=title)
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80,debug=False)