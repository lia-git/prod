import json

import requests

from setting import corp_id, user_id


class WeChatPub:
    s = requests.session()
    token = None

    def __init__(self):
        self.token = self.get_token(corp_id, user_id)
        print("token is " + self.token)

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

    def send_file(self, file):
        media_id = self.get_tmp_id(file)

        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        header = {
            "Content-Type": "application/json"
        }
        form_data = {
            "touser": "@all",
            "toparty": " PartyID1 | PartyID2 ",
            "totag": " TagID1 | TagID2 ",
            "msgtype": "file",
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


if __name__ == '__main__':
    wechat = WeChatPub()
    x = wechat.send_msg(
        "<div class=\"gray\">热点名单</div> <div class=\"normal\"></div>")
    print()
