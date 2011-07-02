#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from experiment import *

class OutputAction(webapp.RequestHandler):
  def get(self):
    print 'Content-type:text/plain'
    print ''
    actions = Action.all().fetch(10000)
    for action in actions:
      print "%s,%s,%s,%s" % (action.turn, action.sender.name, action.receiver.name, action.transferring)
    exit()

class OutputUser(webapp.RequestHandler):
  def get(self):
    print 'Content-type:text/plain'
    print ''
    usermappings = UserMapping.all().fetch(10000)
    for usermapping in usermappings:
      print "%s,%s,%s" % (usermapping.subject.name, usermapping.user, usermapping.subject.money)
    exit()

def main():
    application = webapp.WSGIApplication([('/output/action.csv', OutputAction),
                                          ('/output/user.csv', OutputUser)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

