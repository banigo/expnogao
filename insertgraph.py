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
    edges_query = Edge.all()
    edges = edges_query.fetch(10)
    template_values = {
      'edges': edges
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/insertgraph.html')
    self.response.out.write(template.render(path, template_values))

def insertEdge(name1, name2):
  node1 = Subject.gql("WHERE name = :name", name=name1).get()
  if node1 == None:
    node1 = Subject(name=name1)
  node1.put()
  node2 = Subject.gql("WHERE name = :name", name=name2).get()
  if node2 == None:
    node2 = Subject(name=name2)
  node2.put()
  edge = Edge.gql("WHERE from_node = :from_node AND to_node = :to_node", from_node=node1, to_node=node2).get()
  if edge == None:
    edge = Edge(from_node=node1, to_node=node2)
  edge.put()

class InsertGraph(webapp.RequestHandler):
  def get(self):
    self.redirect('/insertgraph/')
  def post(self):
    insertEdge(self.request.get('from'), self.request.get('to'))
    self.redirect('/insertgraph/')

class InsertFile(webapp.RequestHandler):
  def post(self):
    # TODO:
    for name1, name2 in readfile(self.request.get()):# whatever from file
      insertEdge(name1, name2)
  def readfile(f):
    # TODO:
    # input a file from user's local computer
    # output a list of edge pair (from, to)
    return result
    
def main():
    application = webapp.WSGIApplication([('/insertgraph/', MainHandler),
                                          ('/insertgraph/insert', InsertGraph),
                                          ('/insertgraph/insert_file', InsertFile)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

