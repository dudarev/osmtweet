# -*- coding: utf8 -*-

from django.utils import simplejson as json
import logging
import datetime, time

import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import db

from google.appengine.api import urlfetch

import urllib2

import tweepy
from bitly import BitLy
from trim_to_tweet import trim_to_tweet

import users
from twitter_oauth_handler import OAuthHandler, OAuthAccessToken

from models import *

from get_config import get_config

DEBUG_DO_NOT_SAVE_CHANGESETS = False
DEBUG_LOAD_FROM_FILE = False

class AdminHandler(webapp.RequestHandler):
    def LoadHandler(self):
        self.response.out.write('<br/><br/>Loading changesets<br/>')
        from xml.etree  import cElementTree as etree
        config = get_config()
        # o,a for lat,lon
        # 1,2 for min,max
        o1,a1,o2,a2 = map(float,config['bbox'].split(','))
        delta_o = o2 - o1
        delta_a = a2 - a1
        # load local data from localhost
        if DEBUG_LOAD_FROM_FILE:
            file_name = "data.osm"
            data = open(file_name,'r')
        else:
            url = "http://api.openstreetmap.org/api/0.6/changesets?bbox=%s" % config['bbox']
            try:
                data = urllib2.urlopen(url)
            except urllib2.URLError, e:
                self.response.out.write( "error fetching url" )
                return
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        count = 0
        changesets = []
        # find latest changeset in the datastore
        last_changeset = Changeset.all().order('-created_at').fetch(1)
        last_id_in_datastore = 0
        if last_changeset:
            last_id_in_datastore = last_changeset[0].id
            self.response.out.write("last changeset:<br/>")
            self.response.out.write("id: %d<br/>" % last_changeset[0].id)
            self.response.out.write("created_at: %s<br/><br/>" % last_changeset[0].created_at)
        last_id = None
        last_created_at = None
        all_ids_are_in_order = True
        all_created_at_are_in_order = True
        for event, elem in etree.iterparse(data):
            if elem.tag == 'changeset':
                count += 1
                id = elem.attrib.get('id',None)
                if id:
                    id = int(id)
                    if last_id_in_datastore >= id:
                        self.response.out.write("changeset with id smaller than latest id in datastore<br/>")
                        break
                    self.response.out.write("<br/>id: %d" % id)
                    if last_id and not id < last_id:
                        all_ids_are_in_order = False
                        self.response.out.write("<br/>not in order!")
                    if last_created_at and not created_at < last_created_at:
                        all_created_at_are_in_order = False
                        self.response.out.write("<br/>created_at not in order!")
                    last_id = id
                value_str = elem.attrib['created_at']
                created_at = datetime.datetime.fromtimestamp(time.mktime(time.strptime(value_str, time_format)))
                self.response.out.write("<br/>created_at: %s" % created_at)
                user = elem.attrib.get('user',None)
                if user:
                    self.response.out.write("<br/>user: %s" % user)
                min_lon = float(elem.attrib.get('min_lon',-180))
                min_lat = float(elem.attrib.get('min_lat',-90))
                max_lon = float(elem.attrib.get('max_lon',180))
                max_lat = float(elem.attrib.get('max_lat',90))
                # 3 is an arbitrary number, we just ignore changesets that 3 times larger than bbox in config
                self.response.out.write("<br/>delta_lon: %f" % (max_lon - min_lon))
                self.response.out.write("<br/>delta_lat: %f" % (max_lat - min_lat))
                if ( (max_lon - min_lon) > 3 * delta_o ) or ( (max_lat - min_lat) > 3 * delta_a ):
                    self.response.out.write("<br/>changeset BBOX is too large<br/>")
                    # go to next element
                    continue
                comment = None
                created_by = None
                tags = elem.findall('tag')
                for t in tags:
                    if t.attrib['k'] == 'comment':
                        comment = t.attrib['v']
                    if t.attrib['k'] == 'created_by':
                        created_by = t.attrib['v']
                if comment:
                    self.response.out.write("<br/>comment: %s" % comment)
                if created_by:
                    self.response.out.write("<br/>created_by: %s" % created_by)
                self.response.out.write("<br/>")
                changesets.append(Changeset(key_name=str(id), id=id, created_at=created_at, user=user, comment=comment, created_by=created_by))
        if not DEBUG_DO_NOT_SAVE_CHANGESETS:
            db.put(changesets)
        self.response.out.write("<br/>%d" % count)
        self.response.out.write("<br/>All ids are in order: %s" % str(all_ids_are_in_order))
        self.response.out.write("<br/>All created_at in order: %s" % str(all_created_at_are_in_order))

    def PrepareHandler(self):
        """prepare means: 
        - find the oldest non-prepared
        - create bit.ly link if does not exist
        - create trimmed tweet text if the link exists"""
        config = get_config()
        self.response.out.write('<br/><br/>Preparing to tweet')
        # get oldest non-prepared changeset in the datastore
        oldest_changeset = Changeset.all().order('created_at').filter('is_prepared =', False).fetch(1)
        if oldest_changeset:
            c = oldest_changeset[0]
            self.response.out.write('<br/>There is non-prepared<br/>')
            self.response.out.write("id: %d<br/>" % c.id)
            self.response.out.write("created_at: %s<br/>" % c.created_at)
            self.response.out.write("comment: %s<br/>" % c.comment)
            self.response.out.write("user: %s<br/>" % c.user)
            # if no shortened link - create it
            if not c.link_url:
                long_url = "http://www.openstreetmap.org/browse/changeset/%d" % c.id
                bitly = BitLy(config["bitly_username"], config["bitly_key"])
                short_url = bitly.short_url(long_url)
                if not short_url:
                    self.response.out.write('could not shorten')
                    return
                self.response.out.write(short_url)
                c.link_url = short_url
            if not c.tweet:
                if c.comment:
                    tweet = "%s: %s %s" % (c.user, c.comment, c.link_url)
                else:
                    tweet = "%s: %s" % (c.user, c.link_url)
            c.tweet = trim_to_tweet(tweet)
            if c.link_url and c.tweet:
                c.is_prepared = True
            self.response.out.write('tweet: %s' % c.tweet)
            c.put()

    def TweetHandler(self):
        """tweeting
        does not tweet from localhost"""
        self.response.out.write('<br/><br/>Tweeting<br/>')
        self.response.out.write('this info will be tweeted:<br/>')
        # oldest non-tweeted and prepared
        oldest_changeset = Changeset.all().order('created_at').filter('is_tweeted =', False).filter('is_prepared =', True).fetch(1)
        if not oldest_changeset:
            self.response.out.write('nothing to tweet')
            return
        else:
            c = oldest_changeset[0]
        
        config = get_config()

        # do not tweet from localhost
        if not 'localhost' in self.request.url:
            auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
            auth_data = OAuthAccessToken.all().filter('specifier =', config["twitter_username"]).fetch(1)[0]
            auth.set_access_token(auth_data.oauth_token, auth_data.oauth_token_secret)
            self.response.out.write('<br/>tweeting with oauth:<br/>')
            api = tweepy.API(auth)
            self.response.out.write("id: %d" % c.id)
            self.response.out.write("user: %s" % c.user)
            self.response.out.write("comment: %s" % c.comment)
            self.response.out.write("tweet: %s" % c.tweet)
            try:
                api.update_status(c.tweet)
            except tweepy.error.TweepError, e: 
                self.response.out.write( 'failed: %s' % e.reason )
                if "Status is a duplicate" in e.reason:
                    c.is_tweeted = True
                    c.put()
                return
        else:
            self.response.out.write('<br/>localhost - nothing actually tweeted:')

        self.response.out.write('<br/>%s' % c.tweet)

        c.is_tweeted = True
        c.put()

    def get(self,action=None):
        self.response.out.write('Admin page<br/><br/>')
        self.response.out.write('<a href="/admin/load">Load and parse changesets</a> (takes time)<br/>')
        self.response.out.write('<a href="/admin/prepare">Prepare to tweet</a><br/>')
        self.response.out.write('<a href="/admin/tweet">Tweet</a><br/><br/>')
        self.response.out.write('<a href="http://localhost:8080/_ah/admin/datastore">Localhost datastore</a><br/><br/>')
        self.response.out.write('<a href="/">Home</a><br/><br/>')

        user = users.get_current_user(self)
        if user:
            login_logout_link = "%s<br/><a href=\"%s\">Logout</a>" % (user, users.create_logout_url(self, "/"))
        else:
            login_logout_link = "<a href=\"%s\">Login with Twitter</a>" % users.create_login_url(self, "/")
        self.response.out.write(login_logout_link)

        if action:
            if action == 'load':
                self.LoadHandler()
            if action == 'prepare':
                self.PrepareHandler()
            if action == 'tweet':
                self.TweetHandler()


def main():
    # logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
                                        ('/admin', AdminHandler),
                                        ('/admin/(.*)', AdminHandler),
                                        ],
                                       debug=True)
                                       # debug=False)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()

