#/bin/python
#coding: utf-8

from scrapy import log
from scrapy.utils.misc import load_object
from downloader.logobj import LogableObject
from downloader.parsers.baseparser import BasicLinkInfo, ReturnStatus

class ParserMiddlewareManager(LogableObject):
    component_name = 'parser plugin'

    def __init__(self, parsers):
        super(ParserMiddlewareManager, self).__init__()
        self.parsers = parsers

    @classmethod
    def from_settings(cls, settings, spider=None):
        parser_classes = settings.get("SPIDER_PARSERS", ()) 
        parsers = []
        for clspath in parser_classes:
            parser_cls = load_object(clspath)
            if hasattr(parser_cls, 'from_settings'):
                parser_obj = parser_cls.from_settings(settings)
            else:
                parser_obj = parser_cls()
    
            parsers.append(parser_obj)

        enabled = [x.__class__.__name__ for x in parsers]
        log.msg("Enabled %ss: %s" % (cls.component_name, ", ".join(enabled)), \
           level=log.DEBUG)
        return cls(parsers)

    def process_response(self, response, spider):
        basic_link_info = BasicLinkInfo.from_response(response)
        self.log("%s" % basic_link_info, level=log.DEBUG)

        ret_status = None
        for parser in self.parsers:
            ret_status = parser.parse(response, basic_link_info, spider)
            if ret_status == ReturnStatus.stop_it:
                break

        if ret_status != ReturnStatus.stop_it:
            self.log('ignore unknow response, url:%s, type:%s' \
                % (response.url, type(response)), level=log.ERROR)
