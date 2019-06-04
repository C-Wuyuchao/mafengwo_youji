from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Liquid
from sqlalchemy import create_engine
import pandas as pd
from pyecharts.charts import WordCloud
from collections import Counter
import re



# 从数据库读取信息
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/mafengwoyouji?charset=utf8mb4')

def bar_base_1():
    fromlist = pd.read_sql('select * from youji', con=engine)
    fromlist = fromlist.drop_duplicates(["url"])
    fromlist = fromlist.loc[:, 'url']

    # 查询所有数据库中cost中不为空的值，其中where cost后面也可写成  <> ""
    without_cost_fromlist = pd.read_sql('select * from youji where cost != ""', con=engine)
    # 去掉重复项
    without_cost_fromlist = without_cost_fromlist.drop_duplicates(["url"])
    without_cost_fromlist = without_cost_fromlist.loc[:, 'url']

    y = without_cost_fromlist.size
    x = fromlist.size - y

    bar = Bar(init_opts=opts.InitOpts(page_title="bar页面"))  # 设置html页面标题
    bar.add_xaxis(["没有参数的游记", "有参数的游记"])
    bar.add_yaxis("文章数量", [x, y])
    # 设置全局配置项，可选
    bar.set_global_opts(opts.TitleOpts(title="关于游记参数的分析", subtitle=""))
    # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件
    bar.render("bar.html")

def liquid_base() -> Liquid:
    fromlist = pd.read_sql('select * from youji', con=engine)
    fromlist = fromlist.drop_duplicates(["url"])
    fromlist = fromlist.loc[:, 'url']

    # 查询所有数据库中cost中不为空的值，其中where cost后面也可写成  <> ""
    without_cost_fromlist = pd.read_sql('select * from youji where cost != ""', con=engine)
    # 去掉重复项
    without_cost_fromlist = without_cost_fromlist.drop_duplicates(["url"])
    without_cost_fromlist = without_cost_fromlist.loc[:, 'url']

    y = without_cost_fromlist.size
    x = fromlist.size - y
    c = (
        Liquid()
        .add("lq", [y/(x+y), x/(x+y)])
        .set_global_opts(title_opts=opts.TitleOpts(title="Liquid-游记参数分析"))
    )
    return c

def bar_base_2():
    costs = []
    cost_0to1000 = []
    cost_1000to2000 = []
    cost_2000to3000 = []
    cost_3000to4000 = []
    cost_4000up = []
    fromlist = pd.read_sql('select * from youji where cost != ""', con=engine)
    fromlist = fromlist.drop_duplicates(["url"])
    cost_list = list(fromlist["cost"])
    for cost in cost_list:
        cost = cost[:-3]
        costs.append(cost)

    for i in costs:
        if int(i) <= 1000:
            cost_0to1000.append(i)
        if int(i) > 1000 and int(i) <= 2000:
            cost_1000to2000.append(i)
        if int(i) > 2000 and int(i) <= 3000:
            cost_2000to3000.append(i)
        if int(i) > 3000 and int(i) <= 4000:
            cost_3000to4000.append(i)
        if int(i) > 4000:
            cost_4000up.append(i)
    bar = Bar(init_opts=opts.InitOpts(page_title="bar页面"))  # 设置html页面标题
    bar.add_xaxis(["0~1000", "1000~2000", "2000~3000", "3000~4000", "4000以上"])
    bar.add_yaxis("旅游花费金额", [len(cost_0to1000), len(cost_1000to2000), len(cost_2000to3000), len(cost_3000to4000), len(cost_4000up)])
    # 设置全局配置项，可选
    bar.set_global_opts(opts.TitleOpts(title="关于游记花费情况的分析", subtitle=""))
    # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件
    bar.render("bar2.html")

def wordcloud_base() -> WordCloud:
    fromlist = pd.read_sql('select * from youji', con=engine)
    fromlist = fromlist.drop_duplicates(["url"])
    author_names = list(fromlist["author_name"])
    author_names_list = []
    for author_name in author_names:
        if '(' in author_name:
            try:
                result = re.findall(r'[(](.*?)[)]', author_name)[0]
                author_names_list.append(result)
            except:
                continue
    result = Counter(author_names_list)
    # 排序
    top_10 = sorted(result.items(), key=lambda x: x[1], reverse=True)
    c = (
        WordCloud().add("", top_10, word_size_range=[20, 50], shape="diamond", word_gap=10).set_global_opts(title_opts=opts.TitleOpts(title="游记作者归属地词云展示"))
    )
    return c

def pie_base() -> Pie:
    months_1 = []
    months = []
    attr = []
    play_time_months = []
    fromlist = pd.read_sql('select * from youji where cost <> ""', con=engine)
    fromlist = fromlist.drop_duplicates(["url"])
    play_times = list(fromlist["play_time"])
    for play_time in play_times:
        play_time_month = play_time.split('-')[1]
        play_time_months.append(play_time_month)
    result = Counter(play_time_months)
    print(result)
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
    c = (
        Pie()
        .add("", [list(z) for z in zip(months, attr)])
        .set_global_opts(title_opts=opts.TitleOpts(title=" "))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c

def pie_rosetype() -> Pie:
    months_1 = []
    months = []
    attr = []
    play_time_months = []
    fromlist = pd.read_sql('select * from youji where cost <> ""', con=engine)
    fromlist = fromlist.drop_duplicates(["url"])
    play_times = list(fromlist["play_time"])
    for play_time in play_times:
        play_time_month = play_time.split('-')[1]
        play_time_months.append(play_time_month)

    result = Counter(play_time_months)
    # 排序
    tops = sorted(result.items(), key=lambda x: x[1], reverse=True)
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



if __name__ == "__main__":
 bar_base_1()
 bar_base_2()
 wordcloud_base().render("wordCloud.html")
 pie_base().render("play_time_analysit1.html")
 pie_rosetype().render("play_time_analysit2.html")
 liquid_base().render("shuidi.html")