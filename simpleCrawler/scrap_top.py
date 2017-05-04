import re
import csv
from lxml import html as HTML

class scrapeTopCallback:
    def __init__(self):
        self.writer = csv.writer(open('topWebsite.csv','w'))
        self.fields = ('count','site')
        self.writer.writerow(self.fields)
        self.pattern = re.compile('^"?(.*)"?$')

    def __call__(self, url,html):
        if re.search('topsites',url):
            tree = HTML.fromstring(html)
            lists = tree.cssselect('.site-listing')
            for list in lists:
                row = []
                for field in self.fields:
                    field='desc-paragraph'if field=='site'else field
                    row.append(self.pattern.match(list.cssselect('.{}'.format(field))[0].text_content()).group(1))
                self.writer.writerow(row)