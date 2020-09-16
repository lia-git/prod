import os

db_password = os.environ.get("SP_DB_PWD","")
db_user = os.environ.get("SP_DB_USER","")

db_name = os.environ.get("SP_DB_NAME","")
corp_id = os.environ.get("SP_WX_CORP_ID","")
user_id = os.environ.get("SP_WX_USER_ID","")
user_id_2 = os.environ.get("SP_WX_USER_ID_2","")
user_id_3 = os.environ.get("SP_WX_USER_ID_3","")
device_id = os.environ.get("DEVICE_ID","")
# FFCAABAB-08AF-4412-AEF3-5D7DF3ECDEFC
token = os.environ.get("TOKEN","")
# beZ76XM9tmXAVgO4Cex6u0v1gvMGO5x5641119
sign = os.environ.get("sign","")
# 2f37a4c70288c9ff18d879655827bb53

black_list = ['"cls80410"', '"cls80358"', '"cls80250"', '"cls80272"','"cls80309"','"cls80361"','"cls80134"','"cls80390"','"cls80249"']
# black_list = ['"cls80410"', '"cls80358"', '"cls80366"', '"cls80368"', '"cls80360"', '"cls80272"', '"cls80361"',
#               '"cls80359"','"cls80223"','"cls80218"','"cls80393"','"cls80360"','"cls80382"','"cls80382"','"cls80249"',
#               '"cls80249"','"cls80250"','"cls80086"','"cls80143"','"cls80366"','"cls80296"','"cls80309"','"cls80362"',
#               '"cls80144"','"cls80299"','"cls80269"',]

def get_value(item):
    vls_ =[ int(i) if i else 0 for i in item ]
    vls_tmp = []
    for k in vls_:
        if k <= 1:
            break
        else:
            vls_tmp.append(k)

    vls = []
    for j in vls_tmp[::-1]:
        if j ==1:
            continue
        else:
            vls.append(j)
    return sum(vls)

# 重大事件日历
# https://api3.cls.cn/v2/time_axis/get_list_by_after?app=cailianpress&channel=0&cuid=FFCAABAB-08AF-4412-AEF3-5D7DF3ECDEFC&date=20200726&mb=iPhone12%2C5&net=1&os=ios&ov=13.5.1&platform=iphone&province_code=4403&sign=1f04e28e1ba6d03d744b840bbb9ee020&sv=7.4.4&token=beZ76XM9tmXAVgO4Cex6u0v1gvMGO5x5641119&uid=641119
# 涨停复盘
# https://api3.cls.cn/v1/market_daily_pro/get?app=cailianpress&channel=0&cuid=FFCAABAB-08AF-4412-AEF3-5D7DF3ECDEFC&mb=iPhone12%2C5&net=1&os=ios&ov=13.5.1&platform=iphone&province_code=4403&sign=5c8662e47158a34a38adff77ee6a9dca&sv=7.4.4&token=beZ76XM9tmXAVgO4Cex6u0v1gvMGO5x5641119&uid=641119