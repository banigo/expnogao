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
from graph import *

class Subject(Node):
  money = db.IntegerProperty(default=0)
  #last_action_turn = db.IntegerProperty()
  status = db.StringProperty(choices=set(["view", "send", "done"]))

class Action(db.Model):
  sender = db.ReferenceProperty(reference_class=Subject, required=True, collection_name='sender')
  receiver = db.ReferenceProperty(reference_class=Subject, required=True, collection_name='receiver')
  transferring = db.IntegerProperty()
  turn = db.IntegerProperty()

class UserMapping(db.Model):
  user = db.UserProperty(required=True)
  subject = db.ReferenceProperty(reference_class=Subject, required=True, collection_name='subject_mapping')

class GameSingleton(db.Model):
  # TODO: record many experiment
  turn = db.IntegerProperty()
    
def getGame():
  game = GameSingleton.all().get()
  if game == None:
    game = GameSingleton(turn=1)
  return game
