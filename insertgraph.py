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
from graph import *

class MainHandler(webapp.RequestHandler):
  def get(self):
    edges_query = Edge.all()
    edges = edges_query.fetch(10)
    template_values = {
      'edges': edges
    }
    path = os.path.join(os.path.dirname(__file__), 'insertgraph.html')
    self.response.out.write(template.render(path, template_values))
    #user = users.get_current_user()
    #if user:
    #else:
    #    self.redirect(users.create_login_url(self.request.uri))

class InsertGraph(webapp.RequestHandler):
  def get(self):
    self.redirect('/insertgraph/')
  def post(self):
    node1 = Node.gql("WHERE name = :name", name=self.request.get('from')).get()
    if node1 == None:
      node1 = Node(name=self.request.get('from'))
    node1.put()
    node2 = Node.gql("WHERE name = :name", name=self.request.get('to'), money=self.request.get('tmoney')).get()
    if node2 == None:
      node2 = Node(name=self.request.get('to'))
    node2.put()
    edge = Edge.gql("WHERE from_node = :from_node AND to_node = :to_node", from_node=node1, to_node=node2).get()
    if edge == None:
      edge = Edge(from_node=node1, to_node=node2)
    edge.put()
    self.redirect('/insertgraph/')
    
def main():
    application = webapp.WSGIApplication([('/insertgraph/', MainHandler),
                                          ('/insertgraph/insert', InsertGraph)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

