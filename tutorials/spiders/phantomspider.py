__author__ = 'zhangxa'


from selenium import webdriver
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup

from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http.response.html import HtmlResponse

from ..items import NewsItem

class PhantomjsSpider(CrawlSpider):
    def __init__(self,*a,**kw):
        super(PhantomjsSpider,self).__init__(*a,**kw)
        self.driver = webdriver.PhantomJS(executable_path="/usr/bin/phantomjs")


    name = "sina_oly_phantomjs"
    #allowed_domains = ["www.51job.com"]
    start_urls = (
        'http://2016.sina.com.cn/',
    )

    rules = (
        Rule(LinkExtractor(allow=('2016.sina.com.cn/china/[0-9\-]*/doc-if[a-z0-9]*.shtml',)),process_request='phantomjs_process',callback='parse_one_news',follow=True),
        Rule(LinkExtractor(allow=('2016.sina.com.cn/brazil/[0-9\-]*/doc-if[a-z0-9]*.shtml',
                                  '2016.sina.com.cn/side/[0-9\-]*/doc-if[a-z0-9]*.shtml')),
                                    process_request='phantomjs_process',callback='parse_one_news',follow=True),
        Rule(LinkExtractor(allow=('2016.sina.com.cn',),deny=('php$','php?','video.sina.com.cn',
                                                  )),follow=True),
    )


    def parse_one_news(self,response):
        def do_item(item):
            if item and isinstance(item,list):
                return item[0]
            return item

        item = NewsItem()
        try:
            cn = response.css("div[class='cn']")
            item['url'] = response.url
            item['title'] = do_item(response.css("div[class='blkContainerSblk'] h1::text").extract())

            art_info = response.css("div[class='artInfo']")
            item['publish'] = do_item(art_info.css("span[id='pub_date']::text").extract())
            item['pic_title'] = do_item(response.css("span[class='img_descr'] ::text").extract())
            item['keywords'] = do_item(response.css("p[class='art_keywords'] a::text").extract())
            '''
            filename = response.url.split("/")[-2] + '.html'
            with open(filename,'wb') as f:
                f.write(response.body)
            '''
        except Exception as e:
            self.logger.error("parse url:%s err:%s",response.url,e)
            return []
        return item

    def phantomjs_process(self,request):
        url = request.url
        driver = self.driver
        driver.get(request.url)
        body = driver.page_source
        response = HtmlResponse(url,body=body.encode('UTF-8'),request=request)
        return self.parse_one_news(response)