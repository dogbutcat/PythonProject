import os
import re
import urlparse
import zlib
from datetime import datetime, timedelta
try:
    import cPickle as pickle
except ImportError:
    import pickle


class DiskCache:
    def __init__(self,
                 cache_dir='cache',
                 isCompress=True,
                 expires=timedelta(days=30)):
        self.cache_dir = cache_dir
        self.compress = isCompress
        self.expires = expires

    def url_to_path(self, url):
        components = urlparse.urlsplit(url)
        path = components.path
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        filename = components.netloc + path + components.query
        filename = re.sub('[^/\d\w\-.,;_]', '_', url)
        filename = '/'.join(segment[:255] for segment in filename.split('/'))
        return os.path.join(self.cache_dir, filename)

    def __getitem__(self, url):
        """Load data from disk from target url"""
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fp:
                data = fp.read()
                if self.compress:
                    data = zlib.decompress(data)
                result, timestamp = pickle.loads(data)
                if self.has_expired(timestamp):
                    raise KeyError(url + " has expired!")
                return result
        else:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        """Save data to disk for target url"""
        path = self.url_to_path(url)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        timestamp = datetime.utcnow()
        result = pickle.dumps((result, timestamp))
        if self.compress:
            result = zlib.compress(result)
        with open(path, 'wb') as fp:
            fp.write(result)

    def has_expired(self, timestamp):
        """ Return the time whether has expired """
        return datetime.utcnow() > timestamp + self.expires
