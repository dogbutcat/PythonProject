import zlib
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.binary import Binary
try:
    import cPickle as pickle
except ImportError:
    import pickle


class MongoCache:
    def __init__(self,
                 expires=timedelta(days=30),
                 host='127.0.0.1',
                 port=27017):
        self.client = MongoClient(host, port)
        self.db = self.client.cache
        self.db.webpage.create_index(
            'timestamp', expireAfterSeconds=expires.total_seconds())

    def __getitem__(self, url):
        """Load Value at target url"""
        record = self.db.webpage.find_one({"_id": url})
        if record:
            return pickle.loads(zlib.decompress(record['result']))
        else:
            raise KeyError(url + ' does not exist!')

    def __setitem__(self, url, result):
        """Save value for target url"""
        record = {
            "result": Binary(zlib.compress(pickle.dumps(result))),
            'timestamp': datetime.utcnow()
        }
        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)
