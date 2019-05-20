from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time
from lxml import etree
import redis
import re
import pymysql


# Redis配置
client = redis.StrictRedis()

# mysql配置，其中charset设置成utf8mb4，避免出现特殊符号无法存入数据库问题
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='123456',
    database='mafengwoyouji',
    charset='utf8mb4'
)
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = conn.cursor()

def parse_html_content(source, html):
    """
    获取游记的正文内容以及图片的url，并将其保存在本地中。
    :param source:
    :return:
    """
    # 存入本地的路径
    path = "D:\Mafengwo\wenzhang\\"
    # h2代表游记内容里面的章节标题
    h2 = source.xpath('//div[(@class="_j_content_box")]/div/h2/span/text()')
    # 游记正文内容
    text = source.xpath('//div[(@class="_j_content_box")]')[0].xpath("string(.)").split()
    # 获取游记标题
    title = source.xpath('//div[@class="vi_con"]/h1/text()')[0]
    # 图片链接的正则表达式
    pattern = 'data-src="(.*?)"'
    pictures = re.findall(pattern, html)
    # 处理掉特殊字符，避免不能创建文件
    for cha in '\/:*?"<>|':
        title = title.replace(cha, "")
    try:
        with open(path + '{}.txt'.format(title), 'a', encoding='utf-8') as f:
            # 这里规范txt里面的格式
            j = 1
            for i in text:
                if i in h2:
                    if j != 1:
                        f.write("\n")
                        f.write("第{}节标题：".format(j) + i)
                        f.write("\n")
                        j = j + 1
                    else:
                        f.write("第{}节标题：".format(j) + i)
                        f.write("\n")
                        j = j + 1
                if i not in h2:
                    f.write(i)
            f.write('下面是游记中图片链接地址:')
            f.write("\n")
            for picture in pictures:
                f.write(picture)
                f.write("\n")
        print('写入本地成功')
    except Exception:
        print('写入本地失败')


def parse_html_author_info(selector):
    """
    获取作者名字,发布时间，以及观看数。
    :param selector:
    :return:
    """
    author_name = selector.xpath('//div[@class="person"]/strong/a/text()')[0]
    vc_time = selector.xpath('//div[@class="vc_time"]/span[1]/text()')[0]
    ico_view = selector.xpath('//div[@class="vc_time"]/span[2]/text()')[0]
    return author_name, vc_time, ico_view

def parse_html_travel_title(selector):
    """
    获取文章标题
    :param selector:
    :return:
    """
    title = selector.xpath('//div[@class="vi_con"]/h1/text()')[0]
    return title

def parse_html_travel_dir_list(selector):
    """
    获取游玩时间，游玩天数，游玩人数，以及游玩费用。
    :param selector:
    :return:
    """
    main_temp = selector.xpath('//div[@class="view_con"]/div[2]/div[1]/@class')
    list_temp = selector.xpath('//div[@class="view_con"]/div[2]/div[1]/ul/li[last()]/@class')
    if main_temp == ['tarvel_dir_list clearfix']:
        # 这是4个的
        if list_temp == ['cost']:
            play_time = selector.xpath('//div[@class="view_con"]/div[2]/div[1]/ul/li[1]/text()[2]')[0]
            days = selector.xpath('//div[@class="view_con"]/div[2]/div[1]/ul/li[2]/text()[2]')[0]
            people = selector.xpath('//div[@class="view_con"]/div[2]/div[1]/ul/li[3]/text()[2]')[0]
            cost = selector.xpath('//div[@class="view_con"]/div[2]/div[1]/ul/li[4]/text()[2]')[0]
            return play_time, days, people, cost
        # 这是返回3个游记信息
        else:
            play_time = selector.xpath('//div[@class="view_con"]/div[2]/div[1]/ul/li[1]/text()[2]')[0]
            days = selector.xpath('//div[@class="view_con"]/div[2]/div[1]/ul/li[2]/text()[2]')[0]
            people = selector.xpath('//div[@class="view_con"]/div[2]/div[1]/ul/li[3]/text()[2]')[0]
            cost = None
            return play_time, days, people, cost
    # 没有游记信息
    else:
        print('该网页没有tarvel_dir_list\n')
        play_time = None
        days = None
        people = None
        cost = None
        return play_time, days, people, cost

def parse_html(html, url):
    """
    把获取的内容放在一个函数里
    :param html:
    :return:
    """
    selector = etree.HTML(html)
    parse_html_content(selector, html)
    title = parse_html_travel_title(selector)
    play_time, days, people, cost = parse_html_travel_dir_list(selector)
    author_name, vc_time, ico_view = parse_html_author_info(selector)
    try:
        sql = "insert into youji (url, play_time, days, people, cost,author_name, vc_time, ico_view, title)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (url, play_time, days, people, cost, author_name, vc_time, ico_view, title))
        # 连接完数据库并不会自动提交，所以需要手动 commit 你的改动
        conn.commit()
    except:
        # 如果发生错误则回滚
        print(title+' 数据库发生错误')
        conn.rollback()

def main():
    """
    主函数
    :return:
    """
    main_url = 'http://www.mafengwo.cn'
    num = 1
    while(client.llen('youji')>0):
        driver = webdriver.Chrome()
        # 从Redis中List中的youji里面取出来
        half_url = client.lpop('youji').decode()
        url = main_url + half_url
        # 设置超时时间为10S
        driver.set_page_load_timeout(10)
        try:
            driver.get(url)
        except TimeoutException:
            print('网页超时超过10S，继续下个网页')
            driver.close()
            continue
        print('正在爬取第{}个网页 {} '.format(num, url))
        for i in range(2, 1200):  # 也可以设置一个较大的数，一下到底
            js = "var q=document.documentElement.scrollTop={}".format(i * 100)  # javascript语句
            driver.execute_script(js)
        time.sleep(2)
        for i in range(2, 2000):  # 防止某些网页过长，再滑一次较大的数
            js = "var q=document.documentElement.scrollTop={}".format(i * 100)  # javascript语句
            driver.execute_script(js)
        # 等待个别内容很长的网页加载
        time.sleep(1)
        html = driver.page_source
        try:
            parse_html(html, url)
        except Exception:
            driver.close()
            continue
        print('爬取完成{}个网页 '.format(num))
        num += 1
        driver.close()
    print('Done！')
    conn.close()

if __name__ == '__main__':
    main()




