import multiprocessing
import time
import traceback

import requests
def get_square(code):
    return code *code

def code_main_trend():
    t1 = time.time()
    ret = []
    ret_ = []
    code_list = list(range(30000))

    for code in code_list:
        ret_.append(get_square(code))
    print(time.time()-t1)
    pool = multiprocessing.Pool(processes=16)
    for code in code_list:
        try:
            ret.append(get_square(code))

            # ret.append(pool.apply_async(get_square, (code,)))
            # ret.append([code, now, pct])
            # print(time.time() - s)
            # update_stock_base(code, now, pct)
        except Exception as e:
            # 有异常，回滚事务
            traceback.print_exc()
            continue
    # pool.close()
    # pool.join()
    print(time.time()-t1)
    # print(ret)
    return ret

code_main_trend()
# https://api3.cls.cn/v1/market_daily_pro/get?app=cailianpress&channel=0&cuid=FFCAABAB-08AF-4412-AEF3-5D7DF3ECDEFC&mb=iPhone12%2C5&net=1&os=ios&ov=13.5.1&platform=iphone&province_code=4403&sign=5c8662e47158a34a38adff77ee6a9dca&sv=7.4.4&token=beZ76XM9tmXAVgO4Cex6u0v1gvMGO5x5641119&uid=641119
# https://api3.cls.cn/v1/market_daily_pro/get?app=cailianpress&channel=0&cuid=&mb=iPhone12%2C5&net=1&os=ios&ov=13.5.1&platform=iphone&province_code=4403&sign=5c8662e47158a34a38adff77ee6a9dca&sv=7.4.4&token=&uid=641119