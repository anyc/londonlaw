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



from twisted.internet import reactor, threads
from twisted.protocols import basic
from twisted.python import log
import shlex, sys
from londonlaw.common import util
from londonlaw.common.protocol import *


# turn a UTF-8 encoded string into something printable
def makePrint(s):
   return s.decode('utf-8').encode(sys.stdout.encoding, 'replace')


class ProtocolError(Exception):
   pass
   


class AdminClientProtocol(basic.LineOnlyReceiver):

   def __init__(self):
      self._tagIndex   = 0
      self._waitTag    = ""
      self._state      = "init"


   def connectionLost(self, reason):
      reactor.stop()


   def connectionMade(self):
      self.factory.registerProtocol(self)
      self.sendTokens(self.genTag(), "protocol", PROTOCOL_VERSION)
      self._state = "protocol"


   def disconnect(self):
      self.transport.loseConnection()


   def lineReceived(self, line):
      try:
         tokens    = shlex.split(line)
         if len(tokens) > 1:
            tag       = tokens[0]
            response  = tokens[1].lower()
            data      = tokens[2:]

            f = getattr(self, "".join(("response_", response, "_", self._state)), None)
            if f is None:
               # Try a catch-all method for the command
               f = getattr(self, "".join(("response_", response, "_default")), None)
            if f is None:
               log.msg("Received unhandled server message (tried default): \"" + line + "\" state = \"" + self._state + "\"")
               return
            
            f(tag, data)
         else:
            log.msg("Received unhandled server message (too few args): \"" + line + "\" state = \"" + self._state + "\"")

      except AttributeError, e:
         log.msg(str(e))
         print "tokens = " + str(tokens)
         log.msg("Received unhandled server message: \"" + line + "\" state = \"" + self._state + "\"")


   def genTag(self):
      if self._tagIndex > 99999:
         self._tagIndex = 0
      st = repr(self._tagIndex)
      self._tagIndex += 1
      self._waitTag = "#" + "0"*(5 - len(st)) + st
      return self._waitTag
      

   def getCommand(self):
      return raw_input("> ")


   def handleCommand(self, command_str):
      commands = shlex.split(command_str)
      if commands[0] == 'commands':
         print "Command list: allplayers ban commands deletegame deleteplayer disconnect eject help"
         print "              listgames listplayers password profile quit"
         print "Enter \"help <command>\" to see usage information."
         d = threads.deferToThread(self.getCommand)
         d.addCallback(self.handleCommand)
      elif commands[0] == 'help':
         if len(commands) == 1:
            print "Usage: help <command>" 
            print "Provides usage syntax for the specified command, along with brief explanation of purpose."
            print "Enter 'commands' to see a list of available commands."
         elif commands[1] == 'allplayers':
            print "Usage: allplayers"
            print "Lists all user accounts on the server."
         elif commands[1] == 'ban':
            print "Usage: ban \"player name\""
            print "Sets the specified user's password to a null value, effectively banning that player from the server."
         elif commands[1] == 'commands':
            print "Usage: commands"
            print "Provides a list of admin client commands."
         elif commands[1] == 'deletegame':
            print "Usage: deletegame \"game name\""
            print "Deletes the specified game, and ejects any connected players into the game registration area."
         elif commands[1] == 'deleteplayer':
            print "Usage: deleteplayer \"player name\""
            print "Deletes the user account for this player, and disconnects him from the server if necessary."
         elif commands[1] == 'disconnect':
            print "Usage: disconnect \"player name\""
            print "Causes the server to drop its connection to the specified player."
         elif commands[1] == 'eject':
            print "Usage: eject \"player name\" \"game name\""
            print "Ejects the specified player from this game and into the game registration area."
         elif commands[1] == 'help':
            print "Usage: help <command>" 
            print "Provides usage syntax for the specified command, along with brief explanation of purpose."
         elif commands[1] == 'listgames':
            print "Usage: listgames"
            print "Lists all games running on the server."
         elif commands[1] == 'listplayers':
            print "Usage: listplayers \"game name\""
            print "Lists all players joined to the specified game."
         elif commands[1] == 'password':
            print "Usage: password \"player name\" \"new password\""
            print "Changes the password of the specified player."
         elif commands[1] == 'profile':
            print "Usage: profile \"player name\""
            print "Provides password and IP address information for the specified player."
         elif commands[1] == 'quit':
            print "Usage: quit"
            print "Disconnect from the server and exit the admin client."
         else:
            print "Unable to provide help for unrecognized command \"" + commands[1] + "\"."
         d = threads.deferToThread(self.getCommand)
         d.addCallback(self.handleCommand)
      elif commands[0] == 'allplayers':
         self._state = "tryallplayers"
         self.sendTokens("allplayers")
      elif commands[0] == 'ban':
         if len(commands) > 1:
            self._state = "tryban"
            self.sendTokens("ban", commands[1])
         else:
            print "Usage: ban \"player name\""
            d = threads.deferToThread(self.getCommand)
            d.addCallback(self.handleCommand)
      elif commands[0] == 'deletegame':
         if len(commands) > 1:
            self._state = "trydeletegame"
            self.sendTokens("deletegame", commands[1])
         else:
            print "Usage: deletegame \"game name\""
            d = threads.deferToThread(self.getCommand)
            d.addCallback(self.handleCommand)
      elif commands[0] == 'deleteplayer':
         if len(commands) > 1:
            self._state = "trydeleteplayer"
            self.sendTokens("deleteplayer", commands[1])
         else:
            print "Usage: deleteplayer \"player name\""
            d = threads.deferToThread(self.getCommand)
            d.addCallback(self.handleCommand)
      elif commands[0] == 'disconnect':
         if len(commands) > 1:
            self._state = "trydisconnect"
            self.sendTokens("disconnect", commands[1])
         else:
            print "Usage: disconnect \"player name\""
            d = threads.deferToThread(self.getCommand)
            d.addCallback(self.handleCommand)
      elif commands[0] == 'eject':
         if len(commands) > 2:
            self._state = "tryeject"
            self.sendTokens("eject", commands[1], commands[2])
         else:
            print "Usage: eject \"player name\" \"game name\""
            d = threads.deferToThread(self.getCommand)
            d.addCallback(self.handleCommand)
      elif commands[0] == 'listgames':
         self._state = "trylistgames"
         self.sendTokens("listgames")
      elif commands[0] == 'listplayers': 
         if len(commands) > 1:
            self._state = "trylistplayers"
            self.sendTokens('listplayers', commands[1])
         else:
            print "Usage: listplayers \"game name\""
            d = threads.deferToThread(self.getCommand)
            d.addCallback(self.handleCommand)
      elif commands[0] == 'password':
         if len(commands) > 2:
            self._state = "trypassword"
            self.sendTokens("setpassword", commands[1], commands[2])
         else:
            print "Usage: password \"player name\" \"new password\""
            d = threads.deferToThread(self.getCommand)
            d.addCallback(self.handleCommand)
      elif commands[0] == 'profile':
         if len(commands) > 1:
            self._state = "tryprofile"
            self.sendTokens(self.genTag(), "profile", commands[1])
         else:
            print "Usage: profile \"player name\""
            d = threads.deferToThread(self.getCommand)
            d.addCallback(self.handleCommand)
      elif commands[0] == 'quit':
         self.transport.loseConnection()
      else:
         print "Unrecognized command."
         d = threads.deferToThread(self.getCommand)
         d.addCallback(self.handleCommand)


   def sendTokens(self, *tokens):
      s = util.join_tokens(*tokens)
      # convert from unicode to 8-bit ascii
      self.sendLine(str(s))


   def logUnmatched(self, tag, response, data):
      log.msg("Received unmatched \"" + response + "\" message tagged \"" + 
            tag + "\" with data " + str(data))


   def response_gameinfo_trylistgames(self, tag, data):
      print "* \"" + makePrint(data[0]) + "\""
      print "     status: " + makePrint(data[1]) + "   type: " + makePrint(data[2]) + \
            "   players: " + data[3]


   def response_bad_default(self, tag, data):
      print "Bad command. (\"" + makePrint(data[0]) + "\")"
      self._state = "loggedin"
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_gameinfo_default(self, tag, data):
      pass


   def response_gameremoved_default(self, tag, data):
      pass


   def response_no_default(self, tag, data):
      pass


   def response_no_default(self, tag, data):
      print "Command rejected. (\"" + makePrint(data[0]) + "\")"
      self._state = "loggedin"
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_no_login(self, tag, data):
      print "The server refused your login attempt. (\"" + makePrint(data[0]) + "\")"
      self.transport.loseConnection()


   def response_ok_tryban(self, tag, data):
      self._state = "loggedin"
      print "User banned.  (Use 'disconnect' to force user off the server immediately.)"
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_ok_trydeletegame(self, tag, data):
      self._state = "loggedin"
      print "Game deleted."
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_ok_trydeleteplayer(self, tag, data):
      self._state = "loggedin"
      print "Player deleted."
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_ok_trydisconnect(self, tag, data):
      self._state = "loggedin"
      print "Player disconnected."
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_ok_tryeject(self, tag, data):
      self._state = "loggedin"
      print "Player ejected from game."
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_ok_login(self, tag, data):
      if tag == self._waitTag:
         self._state = "loggedin"
         print "Logged in to server with administrator access.  Enter 'commands' for a command list."
         d = threads.deferToThread(self.getCommand)
         d.addCallback(self.handleCommand)
      else:
         self.logUnmatched(tag, "ok", data)


   def response_ok_loggedin(self, tag, data):
      pass


   def response_ok_protocol(self, tag, data):
      if tag == self._waitTag:
         self._state = "login"
         self.sendTokens(self.genTag(), "login", "admin", self._password)
      else:
         logUnmatched(tag, "ok", data)


   def response_ok_tryallplayers(self, tag, data):
      self._state = "loggedin"
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_ok_trylistgames(self, tag, data):
      self._state = "loggedin"
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_ok_trylistplayers(self, tag, data):
      self._state = "loggedin"
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_ok_trypassword(self, tag, data):
      self._state = "loggedin"
      print "User's password has been set."
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def response_playerinfo_default(self, tag, data):
      pass


   def response_playerinfo_trylistplayers(self, tag, data):
      print "* \"" + makePrint(data[0]) + "\""
      print "     team: " + data[1] + "   vote_start: " + data[2] + "   pawns: " + data[3]


   def response_playername_tryallplayers(self, tag, data):
      print "* \"" + makePrint(data[0]) + "\""


   def response_profile_tryprofile(self, tag, data):
      if tag == self._waitTag:
         print "password: \"" + makePrint(data[0]) + "\"   last_ip: " + data[1]
      else:
         self.logUnmatched(tag, "profile", data)
      self._state = "loggedin"
      d = threads.deferToThread(self.getCommand)
      d.addCallback(self.handleCommand)


   def shutdown(self):
      self._state = "shutdown"
      self.disconnect()




