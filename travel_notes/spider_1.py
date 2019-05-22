import requests
from lxml import etree
import time
from multiprocessing import Pool
import redis

client = redis.StrictRedis()
"""
author:
目标网站:马蜂窝旅游网
抓取内容：游记
"""

def get_article_links(page_urls):
    """
    把所有关于成都的游记网址存入到Redis的List中。
    :param page_urls:
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
        AppleWebKit/537.36 (KHTML, like Gecko)\
         Chrome/46.0.2490.80 Safari/537.36'
    }
    half_url = []
    html = requests.get(url=page_urls, headers=headers)
    print(html)
    selector = etree.HTML(html.text)
    lis = selector.xpath('//div[@class="post-list"]/ul/li')
    for li in lis:
            temp = li.xpath('./h2/a[1]/@class')[0]
            time.sleep(1)
            # 这里要进行判断，因为文章要分星级，和普通的文章，网页结构不同。
            if temp == 'tn-from-app':
                youji_url = li.xpath('./h2/a[2]/@href')[0]
                client.lpush('youji_1', youji_url)
            elif temp == 'xjicon':
                xjicon_temp = li.xpath('./h2/a[2]/@class')[0]
                if xjicon_temp == 'tn-from-app':
                    youji_url = li.xpath('./h2/a[3]/@href')[0]
                    client.lpush('youji_1', youji_url)
                else:
                    youji_url = li.xpath('./h2/a[2]/@href')[0]
                    client.lpush('youji_1', youji_url)
            elif temp == 'title-link':
                youji_url = li.xpath('./h2/a[1]/@href')[0]
                client.lpush('youji_1', youji_url)
            else:
                print(0)
def construct_urls():
    main_url = 'http://www.mafengwo.cn/yj/10035/1-0-{}.html'
    page_urls = []
    # 把网址添加到一个列表中
    for i in range(1, 201):
        url = main_url.format(i)
        page_urls.append(url)
    return page_urls

if __name__ == '__main__':
    pool = Pool(5)
    a = construct_urls()
    pool.map(get_article_links, a)


