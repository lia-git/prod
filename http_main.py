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
        start = args.get("start","")
        end = args.get("end","")
        # if request.form['user'] == 'admin':
        #     return 'Admin login successfully!'
        # else:
        try:
            excute(wechat,code)
        except:
            wechat.send_msg(f"htttp://127.0.0.1:10001/?code=000037&start=20200710&end=20200710")
        return 'No such user!'
    # title = request.args.get('title', 'Default')
    # return render_template('login.html', title=title)
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10001,debug=False)