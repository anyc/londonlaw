#  London Law -- a networked manhunting board game
#  Copyright (C) 2003-2004, 2005 Paul Pelzl
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License, Version 2, as 
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


from twisted.python import log
import sets, shelve, os
from londonlaw.common.protocol import *


class PasswordError(Exception):
   pass

class UserError(Exception):
   pass


# Don't instantiate directly, unless you want to also handle
# the exception.  Use getHandle().
#
# The game registry tracks four items:
#   * self._games is a dict of open games, keyed by game room name
#   * self._users is a dict that maps username to password
#   * self._clients is a dict that maps username to protocol instance
#   * self._unjoinedUsers is a Set of player usernames that are not
#     currently joined to a game
#
# self._games and self._users are persistent structures stored via the
# 'shelve' module.

class GameRegistrySingleton:
   __instance = None

   def __init__(self):
      if GameRegistrySingleton.__instance:
         raise GameRegistrySingleton.__instance
      GameRegistrySingleton.__instance = self

      dummyDir = "~/.londonlaw/server"
      dbDir = os.path.expanduser(dummyDir)
      # catch for OS's that do not have a $HOME
      if dbDir == dummyDir:
         dbDir = "serverdata"
      dbDir = os.path.normpath(dbDir)
      if not os.path.isdir(dbDir):
         os.makedirs(dbDir)

      self._games = shelve.open(os.path.join(dbDir, "games_db." + LLAW_VERSION), 
            "c", writeback = True)
      self._users = shelve.open(os.path.join(dbDir, "users_db." + LLAW_VERSION), 
            "c", writeback = True)
      self._clients       = {}
      self._unjoinedUsers = sets.Set()


   def addClient(self, client):
      self._clients[client.getUsername()] = client

   def addGame(self, game):
      if not self._games.has_key(game.getName()):
         self._games[game.getName()] = game
      else:
         raise Exception("Game name in use.")

   def addUnjoinedUser(self, username):
      self._unjoinedUsers.add(username)

   def close(self):
      log.msg("Closing game registry.")
      self._games.close()
      self._users.close()

   def getClient(self, username):
      return self._clients[username]

   def getGame(self, gameName):
      return self._games[gameName]

   def getGameList(self):
      return [self._games[key] for key in self._games.keys()]

   def getPassword(self, username):
      return self._users[username]

   def getUnjoinedUsers(self):
      return self._unjoinedUsers

   def hasGame(self, gameName):
      return self._games.has_key(gameName)

   def registerUser(self, username, password):
      if not self._users.has_key(username):
         self._users[username] = password
      else:
         if self._clients.has_key(username):
            raise UserError("That username is in use.")
         elif password != self._users[username]:
            raise PasswordError("Incorrect password.")
         else:
            self._users[username] = password

   def removeClient(self, client):
      if self._clients.has_key(client.getUsername()):
         del self._clients[client.getUsername()]

   def removeGame(self, game):
      if self._games.has_key(game.getName()):
         del self._games[game.getName()]

   def removeUnjoinedUser(self, username):
      try:
         self._unjoinedUsers.remove(username)
      except KeyError:
         pass

   def unRegisterUser(self, username):
      if self._users.has_key(username):
         del self._users[username]



def getHandle():
   try:
      g = GameRegistrySingleton()
   except GameRegistrySingleton, instance:
      g = instance
   return g




# arch-tag: DO_NOT_CHANGE_80c29472-b8b4-4207-8c45-2a007410b22c 
