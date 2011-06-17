# -*- coding: utf8 -*-

import os
import logging
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from twitter_oauth_handler import OAuthHandler, OAuthAccessToken

from models import Changeset

from get_config import get_config


class MainHandler(webapp.RequestHandler):
    def get(self):
        changesets = Changeset.all().order('-created_at').fetch(20)
        config = get_config()
        options = {'config': config, 'changesets': changesets}
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        page = template.render(path,options)
        self.response.out.write(page)


class RSSHandler(webapp.RequestHandler):
    def get(self):
        changesets = Changeset.all().order('-created_at').fetch(20)
        config = get_config()
        options = {'config': config, 'changesets': changesets}
        path = os.path.join(os.path.dirname(__file__), 'templates/rss.html')
        page = template.render(path,options)
        self.response.out.write(page)


logging.getLogger().setLevel(logging.DEBUG)
application = webapp.WSGIApplication([
                                    ('/', MainHandler),
                                    ('/rss', RSSHandler),
                                    ('/oauth/(.*)/(.*)', OAuthHandler),
                                    ],
                                   debug=True)
                                   # debug=False)

def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
