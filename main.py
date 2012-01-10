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
import operator
import os
import random
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from experiment import *

class MainHandler(webapp.RequestHandler):
  def random_map(self, key, user):
    map = db.get(key)
    if map.user == None:
      map.user = user
      map.put()
      return map
    else:
      return None
  def checkAllDone(self, key):
    game = db.get(key)
    if game.allDone == False:
       game.allDone = True
       game.put()
       return True
    else:
       return False
   
  def get(self):
    # check whether all players done
    # summarize the turn if all player done
    
    # if game is over, output gameover message
    game = getGame()
    if game.gameOver == True:
      if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
      template_values = {
        'url' : url,
        'url_linktext': url_linktext,
      }
      path = os.path.join(os.path.dirname(__file__), 'templates/gameover.html')
      self.response.out.write(template.render(path, template_values))
      return
    
    user = users.get_current_user()
    # mapping user to game node
    map = UserMapping.gql("WHERE user=:user", user=user).get()
    global_maps = UserMapping.all().fetch(1000)
    global_subjects = set()
    for m in global_maps:
      global_subjects.add(m.subject)
    if map == None:
      maps = db.GqlQuery("SELECT * FROM UserMapping WHERE user=:user", user=None).fetch(1000)
      while len(maps) != 0 and map == None:
      	map = maps.pop(random.randint(0, len(maps) - 1))
        map = db.run_in_transaction(self.random_map, map.key(), user)
    if map != None:
      subject = map.subject
    else:
      print 'Content-type:text/plain'
      print ''
      print 'The game is expired.'
      return
    if subject.status != 'send' and subject.status != 'done':
      subject.status = 'send'
      subject.put()
    if subject.status == 'send' and game.allDone == True:
       game.allDone = False
       game.put()
    if subject.status == 'done':
      if Subject.gql("WHERE status!='done'").count() == 0:
       if db.run_in_transaction(self.checkAllDone, game.key()):
         summaryGame()
    # display
    actions = Action.all().fetch(1000)
    sends = Action.gql("WHERE sender = :subject AND turn = :turn", subject=subject, turn=(game.turn - 1)).fetch(1000)
    receives = Action.gql("WHERE receiver = :subject AND turn = :turn", subject=subject, turn=(game.turn - 1)).fetch(1000)
    sendM = 0
    for s in sends:
      sendM += s.transferring
    receiveM = 0
    for r in receives:
      receiveM += r.transferring
    # Change the money rank order
    friends = []
    for edge in subject.from_node:
      neighbor = Subject.gql("WHERE name=:to_node", to_node=edge.to_node.name).get()
      # No need to process an empty node
      if neighbor == None: continue
      friends.append((edge.to_node, neighbor.money))
    if game.rankOrder == "ascend": friends = sorted(friends, key=operator.itemgetter(1))
    elif game.rankOrder == "descend": friends = sorted(friends, key=operator.itemgetter(1), reverse=True)
    elif game.rankOrder == "random": random.shuffle(friends)
    friends = [i[0] for i in friends]
    # Log in or log out
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
      'game': game, 
      'send': sendM,
      'receive': receiveM,
      'globals': global_subjects,
      'turn' : game.turn,
      'countdownTime' : game.countdownTime,
      'error_msg' : self.request.get('err'),
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, template_values))
    
class Donate(webapp.RequestHandler):
  def post(self):
    user = users.get_current_user()
    subject = UserMapping.gql("WHERE user=:user", user=user).get().subject
    if subject.status == 'send':
      # check total donation
      error_msg = []
      total = 0
      for edge in subject.from_node:
        if len(self.request.get(edge.to_node.name)) == 0:
          continue
        try:
          transferring = int(self.request.get(edge.to_node.name))
        except ValueError:
          error_msg.append('You cannot donate non-integer money to %s.' % edge.to_node.name)
          continue
        if transferring < 0:
          error_msg.append('You cannot donate minus money to %s.' % edge.to_node.name)
          continue
        total += transferring
      if total > subject.money:
        error_msg.append('You cannot donate more money than you own.')        
      if error_msg:
        self.redirect('/?err=%s' % reduce(lambda x, y: x + y + "<br/>", error_msg, ''))
        return
      else:
        for edge in subject.from_node:
          if len(self.request.get(edge.to_node.name)) == 0:
            continue
          transferring = int(self.request.get(edge.to_node.name))
          if transferring != 0:
            game = getGame()
            Action(sender=subject, receiver=edge.to_node, transferring=transferring, turn=game.turn).put()
      subject.status = 'done'
      subject.put()
    elif subject.status == 'done':
      pass
    self.redirect('/')
 

def summaryGame():
  game = getGame()
  subjects = Subject.all().fetch(1000)
  actions = Action.gql('WHERE turn=:turn', turn=game.turn).fetch(1000)
  if len(actions) > 0:
    game.silent = 0
  else:
    game.silent = game.silent + 1
    if game.silent >= game.stopTurns:
      game.silent = 0
      game.gameOver = True
  for subject in subjects:
    actions = Action.gql('WHERE receiver=:subject AND turn=:turn', subject=subject, turn=game.turn).fetch(1000)
    for action in actions:
      subject.money += action.transferring
    actions = Action.gql('WHERE sender=:subject AND turn=:turn', subject=subject, turn=game.turn).fetch(1000)
    for action in actions:
      subject.money -= action.transferring
    subject.status = 'send'
    subject.put()
  game.turn = game.turn + 1
  game.put()

class Logout(webapp.RequestHandler):
  def get(self):
    self.redirect(users.create_logout_url('/'))

def main():
  application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/donate', Donate),
                                          ('/logout', Logout)],
                                         debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

