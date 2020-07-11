from flask import Flask, url_for, request, render_template

from money_fluent import excute
from wechat_utl import WeChatPub

wechat = WeChatPub()

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        args = request.args
        code = args.get("code","")
        type = args.get("type","")
        # if request.form['user'] == 'admin':
        #     return 'Admin login successfully!'
        # else:
        try:
            excute(wechat,code,type)
        except:
            wechat.send_msg(f"http://18.163.236.133:10001/?code={code}&type={type}")
        return 'No such user!'
    # title = request.args.get('title', 'Default')
    # return render_template('login.html', title=title)
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10001,debug=False)