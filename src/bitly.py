# -*- coding: utf-8 -*-
import sys
import urllib
sys.path = ['/usr/local/google_appengine'] + sys.path
import unittest
from django.utils import simplejson
from google.appengine.api import urlfetch

# http://snipplr.com/view.php?codeview&id=15247
class BitLy():
    def __init__(self, login, apikey):
        self.login = login
        self.apikey = apikey

    def expand(self,param):
        request = "http://api.bit.ly/expand?version=2.0.1&shortUrl=http://bit.ly/"
        request += param
        request += "&login=" + self.login + "&apiKey=" +self.apikey

        result = urlfetch.fetch(request)
        json = simplejson.loads(result.content)
        return json

    def shorten(self,param):
        url = urllib.quote(param)
        request = "http://api.bit.ly/shorten?version=2.0.1&longUrl="
        request += url
        request += "&login=" + self.login + "&apiKey=" +self.apikey

        result = urlfetch.fetch(request)
        json = simplejson.loads(result.content)
        return json

    def info(self,param):
        request = "http://api.bit.ly/info?version=2.0.1&hash="
        request += param
        request += "&login=" + self.login + "&apiKey=" +self.apikey

        result = urlfetch.fetch(request)
        json = simplejson.loads(result.content)
        return json

    def stats(self,param):
        request = "http://api.bit.ly/stats?version=2.0.1&shortUrl="
        request += param
        request += "&login=" + self.login + "&apiKey=" +self.apikey

        result = urlfetch.fetch(request)
        json = simplejson.loads(result.content)
        return json

    def errors(self):
        request += "http://api.bit.ly/errors?version=2.0.1&login=" + self.login + "&apiKey=" +self.apikey

        result = urlfetch.fetch(request)
        json = simplejson.loads(result.content)
        return json

    def short_url(self,long_url):
        return self.shorten(long_url)['results'].values()[0]['shortUrl']

    def long_url(self,short_url):
        return self.expand(short_url)['results'].values()[0]['longUrl']


class TestDateFormat(unittest.TestCase):

    def testFormat(self):
        print 'testing'
	bitly = BitLy('toptuby','R_c6faf6450cb2c211e39bd3f6d079a58a')
        long_url = 'http://toptuby.appspot.com/20100106#Z86V_ICUCD4'
        short_url = 'http://bit.ly/8DKpO6'
        self.assertEqual(bitly.long_url(short_url),long_url)
        self.assertEqual(bitly.short_url(long_url),short_url)
        

if __name__ == '__main__':
    from google.appengine.api import urlfetch_stub
    from google.appengine.api import apiproxy_stub_map 
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap() 
    apiproxy_stub_map.apiproxy.RegisterStub('urlfetch',urlfetch_stub.URLFetchServiceStub()) 
    unittest.main()
