import os

db_password = os.environ.get("SP_DB_PWD","")
db_user = os.environ.get("SP_DB_USER","")

db_name = os.environ.get("SP_DB_NAME","")
corp_id = os.environ.get("SP_WX_CORP_ID","")
user_id = os.environ.get("SP_WX_USER_ID","")

black_list = ['"cls80410"', '"cls80358"', '"cls80366"', '"cls80368"', '"cls80360"', '"cls80272"', '"cls80361"',
              '"cls80359"','"cls80223"','"cls80218"','"cls80393"','"cls80360"','"cls80382"','"cls80382"','"cls80249"',
              '"cls80249"','"cls80250"','"cls80086"','"cls80143"','"cls80366"','"cls80296"','"cls80309"','"cls80362"',
              '"cls80144"','"cls80299"','"cls80269"',]

