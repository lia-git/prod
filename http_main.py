from flask import Flask, request
import xml.etree.cElementTree as ET
import setting
from reply.pic_reply import reply_block_pct
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
        sCorpID = setting.corp_id
        wxcpt = WXBizMsgCrypt(token, sEncodingAESKey, sCorpID)
        ret,msg = wxcpt.DecryptMsg( data,signature, timestamp, nonce)
        xml_tree = ET.fromstring(msg)
        content = xml_tree.find("Content").text
        if (ret == 0):
            if "pct_" in content:
                reply_block_pct(content[4:])
                return 0


            return msg
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80,debug=False)