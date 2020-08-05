import json

import requests

from setting import corp_id, user_id


class WeChatPub:
    s = requests.session()
    token = None

    def __init__(self):
        self.token = self.get_token(corp_id, user_id)
        # print("token is " + self.token)

    def get_token(self, corpid, secret):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(corpid, secret)
        rep = self.s.get(url)
        if rep.status_code == 200:
            return json.loads(rep.content)['access_token']
        else:
            print("request failed.")
            return None

    def get_tmp_id(self,file):
        url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.token}&type=file"
        with open(file, 'rb') as f:
            files = {"media": f}
            r = requests.post(url, files=files)
            rep = json.loads(r.text)
            # return re['media_id']
            if rep["errcode"] == 0:
                return rep["media_id"]
            else:
                print("request failed.")
                return None

    def send_file(self, file,type='file'):
        media_id = self.get_tmp_id(file)

        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        header = {
            "Content-Type": "application/json"
        }
        form_data = {
            "touser": "@all",
            "toparty": " PartyID1 | PartyID2 ",
            "totag": " TagID1 | TagID2 ",
            "msgtype": type,
            "agentid": 1000002,
            "file": {
                "media_id": media_id
            },
            "safe": 0
        }
        rep = self.s.post(url, data=json.dumps(form_data).encode('utf-8'), headers=header)
        if rep.status_code == 200:
            return json.loads(rep.content)
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
            "msgtype": "text",
            "agentid": 1000002,
            "text": {
                "content":content,
            },
            "safe": 0
        }
        rep = self.s.post(url, data=json.dumps(form_data).encode('utf-8'), headers=header)
        if rep.status_code == 200:
            return json.loads(rep.content)
        else:
            print("request failed.")
            return None

    def send_remind(self,title="操作准则,严格执行",content=""):
        if not content:
            content = '出手生意铁则(1.30以后)：<br>0.宁可不赚也不赔本,1:30后出手 <br>1.三势共振(大势，板块，个股)<br>2.个股近期趋势(价格、尤其是交易量)<br>3.日内走势(注意交易量)'
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        header = {
            "Content-Type": "application/json"
        }
        form_data = {
            "touser": "@all",
            "toparty": " PartyID1 | PartyID2 ",
            "totag": " TagID1 | TagID2 ",
            "msgtype": "textcard",
            "agentid": 1000002,
            "textcard": { "title":title,
                          "description": f"<div class=\"highlight\">{content}</div>",
                          "url": "URL",

       },
            "safe": 0
        }
        rep = self.s.post(url, data=json.dumps(form_data).encode('utf-8'), headers=header)
        print(rep.content)
        if rep.status_code == 200:
            return json.loads(rep.content)
        else:
            print("request failed.")
            return None

    def send_markdown(self, content):
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        header = {
            "Content-Type": "application/json"
        }
        form_data = {
            "touser": "@all",
            "toparty": " PartyID1 | PartyID2 ",
            "totag": " TagID1 | TagID2 ",
            "msgtype": "textcard",
            "agentid": 1000002,
            "textcard": { "title":content['code'],
                          "description": f"<div class=\"normal\">{content['desc']}</div>",
                          "url": content["url"],

       },
            "safe": 0
        }
        rep = self.s.post(url, data=json.dumps(form_data).encode('utf-8'), headers=header)
        print(rep.content)
        if rep.status_code == 200:
            return json.loads(rep.content)
        else:
            print("request failed.")
            return None


if __name__ == '__main__':
    wechat = WeChatPub()
    # x = wechat.send_msg(
    #     "<div class=\"gray\">热点名单</div> <div class=\"normal\"></div>")
    wechat.send_file("/System/Volumes/Data/data/workspace/prod/img/000037_now.png","image")
    print()
