from sqlalchemy import create_engine
import pandas as pd
import re
from collections import Counter
from pyecharts.charts import WordCloud
from pyecharts import options as opts

engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/mafengwoyouji?charset=utf8mb4')
fromlist = pd.read_sql('select * from youji', con=engine)
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
def wordcloud_base() -> WordCloud:
    c = (
        WordCloud().add("", top_10, word_size_range=[20, 50], shape="diamond", word_gap=10).set_global_opts(title_opts=opts.TitleOpts(title="游记作者归属地词云展示"))
    )
    return c


if __name__ == "__main__":
 wordcloud_base().render("wordCloud.html")
