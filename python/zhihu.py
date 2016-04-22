#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os,re,urllib2
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request, FormRequest

class ZhihuSipder(CrawlSpider) :
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = [
        "http://www.zhihu.com"
    ]
    maxpage = 2
    page = 1
    LastVote = 0 #低于此赞同的不收录
    '''
    rules = (
        Rule(SgmlLinkExtractor(allow = ('/question/\d+', )), callback = 'parse_item', follow = True),
    )
    '''
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36" \
                        "(KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "http://www.zhihu.com/"
    }
 
    def start_requests(self):
        print "START"
        return [Request("http://www.zhihu.com/collection/30822111", 
                    meta = {'cookiejar' : 1},
                    headers=self.headers,
                    callback=self.view_collection)
                ]

    def view_collection(self,response):
        sites = response.xpath('//h2[@class="zm-item-title"]')
        for i in sites:
            title = i.xpath('a/text()').extract()[0]
            self.cratedir('botdir/'+title)
            urls = 'https://www.zhihu.com'+i.xpath('a/@href').extract()[0]
            yield Request(urls, meta = {'cookiejar' : 1},headers=self.headers,body=title,callback=self.parse_item)
        '''
        if self.page < self.maxpage:
            self.page +=1
            url = "http://www.zhihu.com/collection/30822111?page=%d" %self.page
            print url
            return [Request(url, meta = {'cookiejar' : 1},headers=self.headers,callback=self.view_collection)]
            
        '''
    def parse_item(self, response):
        title = response.request.body.decode('utf-8')
        self.log('Hi, this is an item page! %s' % title)
        
        
        Answerlist = response.xpath(
            '//div[@id="zh-question-answer-wrap"]/div[@class="zm-item-answer  zm-item-expanded"]'
            )
        for i in Answerlist:
            self.handleAnswer(i,title)

    def cratedir(self,dirname):
        BASE_PATH = os.getcwd()
        dir_name = os.path.join(BASE_PATH,dirname)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            return True
        else:
            return False
    
    def handleAnswer(self,i,Title):
        
        data_aid = i.xpath('@data-aid').extract()[0]
        author = i.xpath('div[2]/div[1]/a[2]/text()').extract()
        vote = i.xpath('div[1]//span[@class="count"]/text()').extract()[0]
        if author == []:
            author = u"知乎用户"
        else:
            author = author[0]
        BASE_PATH = os.getcwd()
        img_dir = BASE_PATH+'/botdir/'+Title+"/"+author
        
        #filename = img_dir+"/test.txt"
        vote = int(str(vote).replace('K','000'))
        imglist = i.xpath('div[3]/div[2]/img[@data-original]/@data-original').extract()
        if len(imglist) == 0:
            print "NO IMG,PASS!"
            pass
        else:
            self.cratedir(img_dir)
            for imgUrl in imglist:
                imgName = imgUrl.split("/")[-1]
                filename = img_dir+"/"+imgName
                if os.path.exists(filename):
                    print "Image already exists:",filename

                else:
                    data = urllib2.urlopen(imgUrl).read()
                    print Title+" FOR "+author
                    print "Image_Save:",imgUrl
                    try:
                        with open(filename,'wb') as f:
                            f.write(data)
                    except Exception, e:
                        print str(e)
                        pass
