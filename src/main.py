# -*- coding: utf8 -*-

import os
import logging
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from models import *

from get_config import get_config

from twitter_oauth_handler import OAuthHandler, OAuthAccessToken

class MainHandler(webapp.RequestHandler):
    def get(self):
        config = get_config()
        options = {'title': config['title']}
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        page = template.render(path,options)
        self.response.out.write(page)


logging.getLogger().setLevel(logging.DEBUG)
application = webapp.WSGIApplication([
                                    ('/', MainHandler),
                                    ('/oauth/(.*)/(.*)', OAuthHandler),
                                    ],
                                   debug=True)
                                   # debug=False)

def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
