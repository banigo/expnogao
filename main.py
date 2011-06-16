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

class MainHandler(webapp.RequestHandler):
  def get(self):
    #Subject(name='U8ER', money=0, last_action_turn=0, status='view').put()
    #Edge(from_node=Subject.gql("WHERE name=:name", name="n00b").get(), to_node=Subject.gql("WHERE name=:name", name="U8ER").get()).put()
    user = users.get_current_user()
    #print user
    #print dir(user)
    user = users.get_current_user()
    subject = UserMapping.gql("WHERE user=:user", user=user).get().subject    
    if subject.status != 'view' and subject.status != 'send' and subject.status != 'done':
      subject.status = 'view'
      subject.put()
    #print subject
    #print subject.name
    #print subject.from_node.fetch(100)
    #edge = Edge.all().get()
    #print edge
    actions = Action.all().fetch(1000)
    friends = []
    for edge in subject.from_node:
      friends.append(edge.to_node)
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      'actions': actions,
      'subject': subject,
      'friends': friends,
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, template_values))
    
    #user = users.get_current_user()
    #if user:
    #else:
    #    self.redirect(users.create_login_url(self.request.uri))

class Donate(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    subject = UserMapping.gql("WHERE user=:user", user=user).get().subject
    if subject.status == 'view':
      if self.request.get('status') == 'Donate':
        subject.status = 'send'
      elif self.request.get('status') == 'Pass':
        subject.status = 'done'
      subject.put()
    elif subject.status == 'send':
      for edge in subject.from_node:
        if len(self.request.get(edge.to_node.name)) == 0:
          continue
        transferring = int(self.request.get(edge.to_node.name))
        if transferring != 0:
          Action(sender=subject, receiver=edge.to_node, transferring=transferring).put()
      subject.status = 'done'
      subject.put()
    elif subject.status == 'done':
      pass
    self.redirect('/')

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/donate', Donate)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

