#/bin/python
import sys
sys.path.append('../../gen-py.twisted')

import time
from twisted.python import log

from scheduler.ttypes import JobReport
from utils.url import get_domain
from core.info import GlobalInfo

class MemoryBasedSeedsService:
    SEED_PKG_SIZE = 1
    
    def __init__(self, pkg_size):
        self.SEED_PKG_SIZE = pkg_size
        self.pending_seeds = []
        self.global_info = GlobalInfo() 
        log.msg("init MemoryBasedSeedsService, SEED_PKG_SIZE:%s" % pkg_size)

    @property
    def seeds_num(self):
        return len(self.pending_seeds)

    @property
    def hosts(self):
        return self.global_info.hosts

    def get_seeds(self, spiderid, jobreport):
        total = len(self.pending_seeds)
        if total > self.SEED_PKG_SIZE:
            num = self.SEED_PKG_SIZE
        else:
            num = total
        
        results = self.pending_seeds[:num]
        self.pending_seeds = self.pending_seeds[num:]
        self.global_info.update_spider_report(jobreport, 
            True if num > 0 else False)

        log.msg("return %s seeds" % num)
        return results 

    def add_seeds(self, clientid, pkg):
        for seed in pkg.seeds:
            self.pending_seeds.append(seed)
            self.global_info.add_seed(seed)
            log.msg("add %s" % seed)

        log.msg("add %s seeds from %s" % (len(pkg.seeds), clientid))
        return

    def get_latency_time(self, url):
        domain = get_domain(url) 
        hostinfo = self.hosts[domain]
        print hostinfo

        if hostinfo.last_crawl_time is None:
            hostinfo.last_crawl_time = time.time()
            return 0
        else:
            left_time = time.time() - hostinfo.last_crawl_time - \
                hostinfo.crawl_interval

            print "left: ", left_time
            if left_time > 0:
                hostinfo.last_crawl_time = time.time()
                return 0 
            else:
                return -left_time

    def status(self):
        return "unsupported yet"

if __name__ == '__main__':
    service = MemoryBasedSeedsService()
    report = JobReport()
    report.spiderid = 'test001'

    service.get_seeds(report.spiderid, report)
