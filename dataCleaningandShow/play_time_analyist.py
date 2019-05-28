from sqlalchemy import create_engine
import pandas as pd
from collections import Counter
from pyecharts import options as opts
from pyecharts.charts import Pie


months_1 = []
months = []
attr = []
play_time_months = []
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/mafengwoyouji?charset=utf8mb4')
fromlist = pd.read_sql('select * from youji where cost <> ""', con=engine)
play_times = list(fromlist["play_time"])
for play_time in play_times:
    play_time_month = play_time.split('-')[1]
    play_time_months.append(play_time_month)

result = Counter(play_time_months)
# 排序
tops = sorted(result.items(), key=lambda x: x[1], reverse=True)
print(tops)
for top in tops:
    months_1.append(top[0])
    attr.append(top[1])
for month in months_1:
    if month[0] == '0':
        month = month[1]
        month = month + '月份'
        months.append(month)
    else:
        month = month + '月份'
        months.append(month)
def pie_base() -> Pie:
    c = (
        Pie()
        .add("", [list(z) for z in zip(months, attr)])
        .set_global_opts(title_opts=opts.TitleOpts(title=" "))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c

def pie_rosetype() -> Pie:
    c = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(months, attr)],
            radius=["30%", "75%"],
            center=["75%", "50%"],
            rosetype="area",
        )
        .set_global_opts(title_opts=opts.TitleOpts(title=" "))
    )
    return c

pie_base().render("play_time_analysit1.html")
pie_rosetype().render("play_time_analysit2.html")