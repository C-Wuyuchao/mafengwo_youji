from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/mafengwoyouji?charset=utf8mb4')
title_list = pd.read_sql('select * from youji', con=engine)
title_list = title_list["title"]
title_list = list(title_list)
for title in title_list:
    with open('titles.txt', 'a', encoding='utf-8') as f:
        f.write(title)
        f.write("\n")