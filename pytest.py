import os
import random
import unittest
from datetime import timedelta
from ScrapeCallback import ScrapeCallback
from DiskCache import DiskCache
from mongocache import MongoCache

from cinemacrawler import write_csv

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.seq = range(10)
        self.url = 'http://example.webscraping.com/places/view/United-Kingdom-239'
        self.code = 200
        self.html = '''<!--[if HTML5]><![endif]-->
<!DOCTYPE html>
<!-- paulirish.com/2008/conditional-stylesheets-vs-css-hacks-answer-neither/ -->
<!--[if lt IE 7]><html class="ie ie6 ie-lte9 ie-lte8 ie-lte7 no-js" lang="zh-cn"> <![endif]-->
<!--[if IE 7]><html class="ie ie7 ie-lte9 ie-lte8 ie-lte7 no-js" lang="zh-cn"> <![endif]-->
<!--[if IE 8]><html class="ie ie8 ie-lte9 ie-lte8 no-js" lang="zh-cn"> <![endif]-->
<!--[if IE 9]><html class="ie9 ie-lte9 no-js" lang="zh-cn"> <![endif]-->
<!--[if (gt IE 9)|!(IE)]><!--> <html class="no-js" lang="zh-cn"> <!--<![endif]-->
<body>
  <!-- Navbar ================================================== -->
  <div class="navbar navbar-inverse">
    <div class="flash"></div>
    <div class="navbar-inner">
      <div class="container">
        
        <!-- the next tag is necessary for bootstrap menus, do not remove -->
        <button type="button" class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse" style="display:none;">
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </button>
        
        <ul id="navbar" class="nav pull-right"><li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#" rel="nofollow">Log In</a><ul class="dropdown-menu"><li><a href="/user/register?_next=/view/United-Kingdom-239" rel="nofollow"><i class="icon icon-user glyphicon glyphicon-user"></i> Sign Up</a></li><li class="divider"></li><li><a href="/user/login?_next=/view/United-Kingdom-239" rel="nofollow"><i class="icon icon-off glyphicon glyphicon-off"></i> Log In</a></li></ul></li></ul>
        <div class="nav">
          
          <ul class="nav"><li class="web2py-menu-first"><a href="/">Home</a></li><li class="web2py-menu-last"><a href="/search">Search</a></li></ul>
          
        </div><!--/.nav-collapse -->
      </div>
    </div>
  </div><!--/top navbar -->

  <div class="container">
    <!-- Masthead ================================================== -->
      
    <header class="mastheader row" id="header">
        <div class="span12">
            <div class="page-header">
                <h1>
                    Example web scraping website
                    <small></small>
                </h1>
            </div>
        </div>
    </header>
	

    <section id="main" class="main row">
        

        <div class="span12">
            
            

<form action="#" enctype="multipart/form-data" method="post"><table><tr id="places_national_flag__row"><td class="w2p_fl"><label for="places_national_flag" id="places_national_flag__label">National Flag: </label></td><td class="w2p_fw"><img src="/places/static/images/flags/gb.png" /></td><td class="w2p_fc"></td></tr><tr id="places_area__row"><td class="w2p_fl"><label for="places_area" id="places_area__label">Area: </label></td><td class="w2p_fw">244,820 square kilometres</td><td class="w2p_fc"></td></tr><tr id="places_population__row"><td class="w2p_fl"><label for="places_population" id="places_population__label">Population: </label></td><td class="w2p_fw">62,348,447</td><td class="w2p_fc"></td></tr><tr id="places_iso__row"><td class="w2p_fl"><label for="places_iso" id="places_iso__label">Iso: </label></td><td class="w2p_fw">GB</td><td class="w2p_fc"></td></tr><tr id="places_country__row"><td class="w2p_fl"><label for="places_country" id="places_country__label">Country: </label></td><td class="w2p_fw">United Kingdom</td><td class="w2p_fc"></td></tr><tr id="places_capital__row"><td class="w2p_fl"><label for="places_capital" id="places_capital__label">Capital: </label></td><td class="w2p_fw">London</td><td class="w2p_fc"></td></tr><tr id="places_continent__row"><td class="w2p_fl"><label for="places_continent" id="places_continent__label">Continent: </label></td><td class="w2p_fw"><a href="/continent/EU">EU</a></td><td class="w2p_fc"></td></tr><tr id="places_tld__row"><td class="w2p_fl"><label for="places_tld" id="places_tld__label">Tld: </label></td><td class="w2p_fw">.uk</td><td class="w2p_fc"></td></tr><tr id="places_currency_code__row"><td class="w2p_fl"><label for="places_currency_code" id="places_currency_code__label">Currency Code: </label></td><td class="w2p_fw">GBP</td><td class="w2p_fc"></td></tr><tr id="places_currency_name__row"><td class="w2p_fl"><label for="places_currency_name" id="places_currency_name__label">Currency Name: </label></td><td class="w2p_fw">Pound</td><td class="w2p_fc"></td></tr><tr id="places_phone__row"><td class="w2p_fl"><label for="places_phone" id="places_phone__label">Phone: </label></td><td class="w2p_fw">44</td><td class="w2p_fc"></td></tr><tr id="places_postal_code_format__row"><td class="w2p_fl"><label for="places_postal_code_format" id="places_postal_code_format__label">Postal Code Format: </label></td><td class="w2p_fw">@# #@@|@## #@@|@@# #@@|@@## #@@|@#@ #@@|@@#@ #@@|GIR0AA</td><td class="w2p_fc"></td></tr><tr id="places_postal_code_regex__row"><td class="w2p_fl"><label for="places_postal_code_regex" id="places_postal_code_regex__label">Postal Code Regex: </label></td><td class="w2p_fw">^(([A-Z]\d{2}[A-Z]{2})|([A-Z]\d{3}[A-Z]{2})|([A-Z]{2}\d{2}[A-Z]{2})|([A-Z]{2}\d{3}[A-Z]{2})|([A-Z]\d[A-Z]\d[A-Z]{2})|([A-Z]{2}\d[A-Z]\d[A-Z]{2})|(GIR0AA))$</td><td class="w2p_fc"></td></tr><tr id="places_languages__row"><td class="w2p_fl"><label for="places_languages" id="places_languages__label">Languages: </label></td><td class="w2p_fw">en-GB,cy-GB,gd</td><td class="w2p_fc"></td></tr><tr id="places_neighbours__row"><td class="w2p_fl"><label for="places_neighbours" id="places_neighbours__label">Neighbours: </label></td><td class="w2p_fw"><div><a href="/iso/IE">IE </a></div></td><td class="w2p_fc"></td></tr></table><div style="display:none;"><input name="id" type="hidden" value="2141735" /></div></form>

<a href="/edit/United-Kingdom-239">Edit</a>

            
        </div>

        
    </section><!--/main-->

    <!-- Footer ================================================== -->
    <div class="row">
        <footer class="footer span12" id="footer">
        </footer>
    </div>

  </div> <!-- /container -->

  <!-- The javascript =============================================
       (Placed at the end of the document so the pages load faster) -->
  <script src="/places/static/js/bootstrap.min.js"></script>
  <script src="/places/static/js/web2py_bootstrap.js"></script>
  <!--[if lt IE 7 ]>
      <script src="/places/static/js/dd_belatedpng.js"></script>
      <script> DD_belatedPNG.fix('img, .png_bg'); //fix any <img> or .png_bg background-images </script>
      <![endif]-->
</body>
</html>

'''

    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1, 2, 3))

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)

    def test_scrapCallback(self):
        ScrapeCallback().__call__(self.url, self.html)
        with open('countries.csv','r') as f:
            print(f.read())

    def test_setitem(self):
        cache = DiskCache()
        cache[self.url]={'html':self.html,'code':self.code}
        self.assertTrue(os.path.exists(cache.url_to_path(self.url)))

    def test_getitem(self):
        cache = DiskCache()
        try:
            result = cache[self.url]
            self.assertEqual(result['code'],self.code)
        except KeyError as e:
            self.assertEqual(e.message,self.url+' has expired!')
        # self.assertRaises(KeyError,cache.__getitem__,self.url)

    def test_timeExpire(self):
        cache = DiskCache(expires=timedelta(seconds=5))
        try:
            result = cache[self.url]
        except KeyError as e:
            self.assertEqual(e.message,self.url+' has expired!')
        # self.assertRaises(KeyError,cache.__getitem__,self.url)

    def test_mongoSet(self):
        cache = MongoCache()
        cache[self.url] = {'code':self.code,'html':self.html}

    def test_mongoGet(self):
        cache = MongoCache()
        result = cache[self.url]
        self.assertEqual(self.html,result['html'])

    def test_write_film(self):
        if os.path.exists('films.csv'):
            os.remove('films.csv')
        write_csv(1,2,3,4,5)
        with open('films.csv','r') as f:
            f.readline()
            self.assertIn('1,2,3,4,5',f.readline(),'Failed !')

if __name__ == '__main__':
    unittest.main()
