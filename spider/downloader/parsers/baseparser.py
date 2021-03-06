#/bin/python
# -*- coding: utf-8 -*-

#from scrapy.http.response.text import TextResponse
import copy
from urlparse import urlparse
from scrapy.conf import settings
from scrapy.project import crawler
from scrapy.http import Request
from scrapy.utils.signal import send_catch_log
from urlparse import urljoin
from scrapy.stats import stats

from downloader.logobj import LogableObject
from downloader.utils.url import get_domain, get_uid
from downloader.utils.unicode import stringPartQ2B
from downloader import signals

class ReturnStatus(object):
    stop_it = 0
    move_on = 1

class BasicLinkInfo(object):
    
    def __init__(self, cur_idepth, max_idepth, \
            cur_xdepth, max_xdepth, content_group, \
            pl_group, source, url):
        self.cur_idepth = cur_idepth
        self.max_idepth = max_idepth
        self.cur_xdepth = cur_xdepth
        self.max_xdepth = max_xdepth
        self.content_group = content_group
        self.pl_group = pl_group
        self.source = source
        self.url = url
        self.uid = get_uid(url)
        self.domain = get_domain(url) 
        self.host = urlparse(self.url).hostname

    def __str__(self):
        return 'URL[%s], Host[%s], Domain[%s], Int_Dep[%d/%d], Ext_Dep[%d/%d],' \
            ' Content_Group[%s], Pl_Group[%s], Source[%s]'\
            % (self.url, self.host, self.domain, self.cur_idepth,
            self.max_idepth, self.cur_xdepth, self.max_xdepth, 
            self.content_group, self.pl_group, self.source)
    
    @staticmethod
    def from_response(response):
        max_idepth = response.request.meta.get('max_idepth', 0)
        max_xdepth = response.request.meta.get('max_xdepth', 0)
        cur_idepth = response.request.meta.get('cur_idepth', 0) + 1
        cur_xdepth = response.request.meta.get('cur_xdepth', 0) + 1
        content_group = response.request.meta.get('content_group')
        pl_group = response.request.meta.get('pl_group', None)
        source = response.request.meta.get('source', None)
        url = response.url
        return BasicLinkInfo(cur_idepth, max_idepth,\
            cur_xdepth, max_xdepth, content_group, pl_group, source, url)

class BaseParser(LogableObject):
    IGNORE_LINK_NUM = -1
    ALLOW_CGS = [] 

    def __init__(self):
        self.spider = None 
        self.response = None
        self.basic_link_info = None
        self.plg_mapping = settings.get("PLG_MAPPING") 
        self.tmpfile_dir = settings.get("TMP_FILE_DIR")
    
    def init_context(self, response, basic_link_info, spider):
        self.response = response
        self.basic_link_info = basic_link_info
        self.spider = spider

    '''@Interface: 
    '''
    def conditon_permit(self, response, basic_link_info, spider):
        #if not isinstance(response, TextResponse):
        #    return False
        
        if self.ALLOW_CGS and \
            basic_link_info.content_group not in self.ALLOW_CGS:
            return False
        
        return True

    def parse(self, response, basic_link_info, spider):
        if not self.conditon_permit(response, basic_link_info, spider):
            return  ReturnStatus.move_on
        
        self.log("use parser: %s" % type(self))
        self.init_context(response, basic_link_info, spider)
        link_num = self.process()
        send_catch_log(signal=signals.link_extracted,
            url=self.response.url, link_num=link_num)

        return ReturnStatus.stop_it

    '''@Interface: 
        default process flow:
        1. process_entrypage  cur_idepth=1
        2. process_listpage   cur_idepth=2
        3. process_contentpage cur_idepth=3
    '''
    def process(self):
        return 0
    
    def get_collection_name(self):
        return self.plg_mapping.get(self.basic_link_info.pl_group)

    def save(self, url, name, cat, price):
        self.spider.dbclient.put(url, name, cat, price,
            self.get_collection_name())

    def encode(self, text, tencoding='utf-8'):
        if not isinstance(text, unicode):
            raise Exception('text must be unicode, get %s' % type(text))
        utext = stringPartQ2B(text)
        return utext.encode(tencoding)

    def decode(self, text, encoding=None):
        if not isinstance(text, str):
            raise Exception('text must be str, get %s' % type(text))
        if encoding is None:
            encoding = self.response.encoding
        return text.decode(encoding)

    def crawl(self, request):
        crawler.engine.crawl(request, self.spider)
        self.log("craw request:%s, refer:%s" % (request.url, self.response.url))

    def make_request_from_response(self, url, **metakws):
        meta = copy.deepcopy(self.response.meta)
        for key in metakws:
            meta[key] = metakws[key]
        meta['source'] = self.response.url
        return Request(url, meta=meta)

    def stats_report(self):
        #stats.inc_value('docsaved_count', spider=self.spider)
        pass

    def urljoin(self, url, base_url=None):
        return urljoin(base_url if base_url else self.response.url, url)
