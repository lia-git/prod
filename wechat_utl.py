import json

import requests


class WeChatPub:
    s = requests.session()
    token = None

    def __init__(self):
        self.token = self.get_token("ww49433899fdbb10f8", "topiogezNAENFqfzFspMUlc03FSICcfN8rTEA4E58ng")
        print("token is " + self.token)

    def get_token(self, corpid, secret):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(corpid, secret)
        rep = self.s.get(url)
        if rep.status_code == 200:
            return json.loads(rep.content)['access_token']
        else:
            print("request failed.")
            return None

    def send_msg(self, content):
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        header = {
            "Content-Type": "application/json"
        }
        form_data = {
            "touser": "@all",
            "toparty": " PartyID1 | PartyID2 ",
            "totag": " TagID1 | TagID2 ",
            "msgtype": "textcard",
            "agentid":1000002,
            "textcard": {
                "title": "领奖通知",
                "description": content,
                "url": "URL",
                "btntxt": "更多"
            },
            "safe": 0
        }
        rep = self.s.post(url, data=json.dumps(form_data).encode('utf-8'), headers=header)
        if rep.status_code == 200:
            return json.loads(rep.content)
        else:
            print("request failed.")
            return None


if __name__ == '__main__':
    wechat = WeChatPub()
    x = wechat.send_msg("<div class=\"gray\">2016年9月26日</div> <div class=\"normal\">恭喜你抽中iPhone 7一台，领奖码：xxxx</div><div class=\"highlight\">请于2016年10月10日前联系行政同事领取</div>")
    print()