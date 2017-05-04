from datetime import datetime,timedelta
from pymongo import MongoClient, errors

class MongoQueue:
    OUTSTANGDING,PROGRESSING,COMPLETE=range(3)

    def __init__(self, host='127.0.0.1', port='27017', timeout=300):
        self.client = MongoClient(host=host,port=port)
        self.db = self.client.cache
        self.timeout = timeout

    def __nonzero__(self):
        record = self.db.crawl_queue.find_one(
            {'status':{'$ne':self.OUTSTANGDING}}
        )
        return True if record else False

    def push(self, url):
        try:
            self.db.crawl_queue.insert(
                {'_id':url,'status':self.OUTSTANGDING}
            )
        except errors.DuplicateKeyError as identifier:
            pass

    def pop(self):
        record = self.db.crawl_queue.find_and_modify(
            query={'status':self.OUTSTANGDING},
            update={'$set':{'status':self.PROGRESSING,'timestamp':datetime.now()}}
        )
        if record:
            return record['_id']
        else:
            self.repair()
            raise KeyError

    def repair(self):
        record = self.db.crawl_queue.find_and_modify(
            query={
                'timestamp':{'$lt':datetime.now()-timedelta(seconds=self.timeout)},
                'status':{'$ne':self.COMPLETE}
            },
            update={'$set':{'status':self.OUTSTANGDING}}
        )
        if record:
            print 'Released: ',record['_id']

    def complete(self, url):
        self.db.crawl_queue.update(
            {'_id':url},
            {'$set':{'status':self.COMPLETE}}
        )