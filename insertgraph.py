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
import string
import random
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
    node1 = Subject(name=name1, map=False)
    node1.put()
    map = UserMapping(subject=node1)
    map.put()
  node2 = Subject.gql("WHERE name = :name", name=name2).get()
  if node2 == None:
    node2 = Subject(name=name2, map=False)
    node2.put()
    map = UserMapping(subject=node2)
    map.put()
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
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'templates/insertfile.html')
    self.response.out.write(template.render(path, template_values))
  def post(self):
    names = set()
    for name1, name2 in self.readFile(self.request.POST.get('graphfile').file.read()):# whatever from file
      insertEdge(name1, name2)
      names.add(name1)
      names.add(name2)
    self.giveTokens(list(names))
    self.redirect('/insertgraph/')
  def giveTokens(self, names):
    tokens = 10
    while(len(names) != 0):
      name1 = names.pop(random.randint(0, len(names) - 1))
      subject1 = Subject.gql("WHERE name = :name", name=name1).get()
      subject1.money = tokens
      subject1.put()
      tokens += 10
    
  def readFile(self, file_content):
    edges = []
    file_content = string.replace(file_content, '\r', '')
    file_content = string.replace(file_content, '\n', '')
    file_content = file_content.split(')')
    for e in file_content:
        if e == '':
          continue
        e = e[e.index('(') + 1:]
        e = e.split('->')
        edge = []
        edge.append(e[0].strip())
        edge.append(e[1].strip())
        edges.append(edge)
    return edges

class InsertDefault(webapp.RequestHandler):
  # add default test case (line graph)
  def get(self):
    insertEdge('A', 'B')
    insertEdge('B', 'A')
    insertEdge('B', 'C')
    insertEdge('C', 'B')
    self.redirect('/insertgraph/')

def main():
    application = webapp.WSGIApplication([('/insertgraph/', MainHandler),
                                          ('/insertgraph/insert', InsertGraph),
                                          ('/insertgraph/insert_file', InsertFile),
                                          ('/insertgraph/insert_default', InsertDefault)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

