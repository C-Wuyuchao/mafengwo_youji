from sqlalchemy import create_engine
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar


costs = []
cost_0to3000 = []
cost_3000to5000 = []
cost_5000up = []
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/mafengwoyouji?charset=utf8mb4')
fromlist = pd.read_sql('select * from youji where cost <> ""', con=engine)
cost_list = list(fromlist["cost"])
for cost in cost_list:
    cost = cost[:-3]
    costs.append(cost)
for i in costs:
    if int(i) <= 3000:
        cost_0to3000.append(i)
    if int(i)>3000 and int(i)<= 5000:
        cost_3000to5000.append(i)
    else:
        cost_5000up.append(i)
def bar_base():

    bar = Bar(init_opts=opts.InitOpts(page_title="bar页面"))  # 设置html页面标题
    bar.add_xaxis(["0~3000", "3000~5000", "5000以上"])
    bar.add_yaxis("文章数量", [len(cost_0to3000), len(cost_3000to5000), len(cost_5000up)])
    # 设置全局配置项，可选
    bar.set_global_opts(opts.TitleOpts(title="关于游记花费情况的分析", subtitle="hello"))
    # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件
    bar.render("bar2.html")



if __name__ == "__main__":
 bar_base()