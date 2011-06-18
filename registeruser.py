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
import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from experiment import *

class MainHandler(webapp.RequestHandler):
  def get(self):
    usermapping_query = UserMapping.all()
    usermappings = usermapping_query.fetch(10)
    template_values = {
      'usermappings': usermappings
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/registeruser.html')
    self.response.out.write(template.render(path, template_values))

def insertUser(email, subjectName):
  subject = Subject.gql("WHERE name = :name", name=subjectName).get()
  if subject == None:
    subject = Subject(name=subjectName)
  subject.put()
  usermapping = UserMapping.gql("WHERE user = User(:email) AND subject_mapping = :subject", email=email, subject=subject).get()
  if usermapping == None:
    usermapping = UserMapping(user=users.User(email), subject=subject)
  usermapping.put()

class NewUser(webapp.RequestHandler):
  def post(self):
    insertUser(self.request.get('email'), self.request.get('name'))
    self.redirect('/register/')

    
def main():
    application = webapp.WSGIApplication([('/register/', MainHandler),
                                          ('/register/newuser', NewUser)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

