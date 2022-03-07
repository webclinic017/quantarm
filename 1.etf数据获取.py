
import jqdatasdk
import pandas as pd
jqdatasdk.auth('17611196958', 'Zt123456')

widthfund = [
    510050,  # 上证50ETF
    513550,  # 港股通50ETF
    510500,  # 中证500ETF
    159920,  # 恒生ETF
    510900,  # H股ETF
    510300,  # 沪深300ETE
    512100,  # 中证1000ETF
    513500,  # 标普500ETF
    513520,  # 日经ETF
    159901,  # 深证100ETF易方达
    588000,  # 科创50ETF
    513100,  # 纳指ETF
    159781,  # 双创50ETF
    159967,  # 创成长ETF
    159915,  # 创业板ETF易方达,
    159949,  # 创业板50ETF
]
# ['510050.XSHG', '513550.XSHG', '510500.XSHG', '159920.XSHE', '510900.XSHG', '510300.XSHG', '512100.XSHG', '513500.XSHG', '513520.XSHG', '159901.XSHE', '588000.XSHG', '513100.XSHG', '159781.XSHE', '159967.XSHE', '159915.XSHE', '159949.XSHE']

industryfund = [
    515220,   # 煤炭ETF
    159980,   # 有色ETF
    159766,   # 旅游EF
    512800,   # 银行ETF
    512200,   # 房地产ETF
    516970,   # 基建50ETF
    515210,   # 钢铁ETF
    159825,   # 农IPETF
    159745,   # 建材ETF
    516780,   # 稀土ETF
    515790,   # 光伏ETF
    515230,   # 软件ETF
    159996,   # 家电ETF
    512690,   # 酒ETF
    513330,   # 恒生互联网ETF
    512170,   # 医疗ETF
    516110,   # 汽车ETF
    512660,   # 军工ETF
    512980,   # 传媒EF
    513360,   # 教育ETF
]
fund_code = jqdatasdk.normalize_code(widthfund)
for code in fund_code:
    df = jqdatasdk.get_bars(code, 200000, unit='1d', fields=[
                            'date', 'open', 'close', 'high', 'low', 'money'], include_now=False, end_dt='2022-03-05')
    df.to_csv('widthfund_1d/'+code+'.csv')
    print(df)
