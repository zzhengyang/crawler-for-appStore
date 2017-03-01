# coding:utf-8
import re
import time
import urllib
import datetime
from urllib import quote
import urllib2
import MySQLdb
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

CONNECT_USERNAME = "root"
CONNECT_SECRET = "root"
DB_NAME = "aso"
TABLE_NAME = "huawei"
class HWASO:
    def __init__(self):
        self.siteURL = 'http://appstore.huawei.com/'
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}

    # 获得页面html
    def getPage(self, url):
        try:

            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            page = response.read()
            pageCode = re.sub(r'<br[ ]?/?>', '\n', page)
            return pageCode
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print e.reason
                return None

    # 获得App信息

    def getAppInfoList(self, page):
        soup = BeautifulSoup(page, 'html.parser')
        appInfos = soup.findAll("div", class_="game-info whole")
        return appInfos

    def getAppInfo(self, appInfo, keyword):
        appID = re.findall(r'/app/(.*)', str(appInfo.h4.a['href']))[0]
        appName = str(appInfo.h4.a.getText())
        appScore = appInfo.h4.span['class'][0]
        appRating = float(re.findall('score_(.*)', appScore)[0]) / 2
        appDownLoad = int(re.findall('下载:(.*)次', str(appInfo.findAll("span")[3].string))[0])
        appReleaseTime = re.findall('发布时间： (.*)', str(appInfo.findAll("span")[1].string))[0]
        queryDate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        return [appID, appName, appRating, appDownLoad, appReleaseTime,queryDate,keyword]


    def start(self):
        conn = MySQLdb.connect(
            host='127.0.0.1',
            user=CONNECT_USERNAME,
            passwd=CONNECT_SECRET,
            db=DB_NAME,
            port=3306,
            charset="utf8"
        )
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS huawei(`id` int(10) unsigned NOT NULL AUTO_INCREMENT,\
                                                      `app_id` varchar(50) NOT NULL,\
                                                      `app_name` varchar(50) NOT NULL,\
                                                      `app_rating` float(2,1) NOT NULL,\
                                                      `app_download` int(20) NOT NULL,\
                                                      `app_release_time` date NOT NULL,\
                                                      `query_date` date NOT NULL,\
                                                      `keyword`	varchar(50) NOT NULL,\
                                                      PRIMARY KEY (`id`)\
                                                    ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 ")
        print "抓取中..."
        a = 0
        for i in range(1, len(sys.argv)):
            a = 0
            keyword = sys.argv[i]
            print "关键词" + keyword + "抓取:"
            for pagePerKeyword in range(1,6):

                try:
                    infoPerKeywordDay = []

                    url = self.siteURL + 'search/' + urllib.quote(keyword) + '/' + str(pagePerKeyword)

                    page = self.getPage(url)
                    appinfoList = self.getAppInfoList(page)
                    for appInfo in appinfoList:

                         infoPerKeywordDay.append(self.getAppInfo(appInfo, keyword))

                    # cur.execute("SELECT id FROM huawei WHERE keyword = '%s'  and app_id = '%d' " % (keyword, int(appID)))
                    # results = cur.fetchone()
                    # if results is not None:
                    #     print "已存在"
                    #         continue
                    #     else:

                    cur.executemany("INSERT INTO huawei(app_id,app_name,app_rating,app_download,app_release_time,query_date,keyword) \
                                              VALUES(%s,         %s     ,%s      ,%s            ,%s            ,%s        ,%s)" , \
                                     infoPerKeywordDay)
                    conn.commit()
                    a+=1
                    print "page(24app/page): " + str(a)
                    time.sleep(1)
                except:
                    continue



        cur.close()
        conn.close()
        print "抓取完成"

con = MySQLdb.connect(user=CONNECT_USERNAME, passwd=CONNECT_SECRET)
cur = con.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS %s"%(DB_NAME))
aso = HWASO()
aso.start()


