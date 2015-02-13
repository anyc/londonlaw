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



import shlex, sys, gettext, locale
from twisted.protocols import basic
from twisted.python import log
from londonlaw.common import util
from londonlaw.common.protocol import *
import wx


class ProtocolError(Exception):
   pass
   


class LLawClientProtocol(basic.LineOnlyReceiver):

   def __init__(self):
      self._tagIndex   = 0
      self._waitTag    = ""
      self._pawnInfo   = [None, None, None, None, None, None]
      self._pawn2Index = {"X" : 0, "Red" : 1, "Yellow" : 2,
            "Green" : 3, "Blue" : 4, "Black" : 5}
      self._game2Status = {}
      self._gameJoined = None
      self._history    = []


   def _setPreviousState(self):
      if self._state == "joined":
         self._state = "loggedin"
      elif self._state == "tryjoin":
         self._state = "loggedin"
      elif self._state == "tryleave":
         self._state = "joined"
      elif self._state == "trynewgame":
         self._state = "loggedin"
      elif self._state == "trysetteam":
         self._state = "joined"
      elif self._state == "tryvote":
         self._state = "joined"
      else:
         raise ProtocolError("called _setPreviousState() with unknown state \"" 
               + self._state + "\"")


   def connectionLost(self, reason):
      if self._state != "shutdown":
         self._messenger.guiAlert(_("You have been disconnected from the server."))
         self._messenger.guiLaunchConnectionWindow()


   def connectionMade(self):
      self.factory.registerProtocol(self)
      self.sendTokens(self.genTag(), "protocol", PROTOCOL_VERSION)
      self._state = "protocol"


   def disconnect(self):
      self.transport.loseConnection()


   def join(self, name):
      log.msg("called Protocol.join()")
      self.sendTokens(self.genTag(), "join", name.encode("utf-8"))
      self._state      = "tryjoin"
      self._gameJoined = name


   def leave(self):
      log.msg("called Protocol.leave()")
      self._state = "tryleave"
      self.sendTokens(self.genTag(), "leave")


   def lineReceived(self, line):
      #print "received line \"%s\"" % line.encode("string_escape")
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


   def makeMove(self, data):
      self._state = "trymove"
      if len(data) == 3:
         self.sendTokens(self.genTag(), "move", data[0], data[1], data[2])
      elif len(data) == 5:
         self.sendTokens(self.genTag(), "doublemove", 
               data[0], data[1], data[2], data[3], data[4])
      else:
         print "Protocol.makeMove() received illegal data length"


   def newgame(self, data):
      self._state = "trynewgame"
      self.sendTokens(self.genTag(), "newgame", data[0].encode("utf-8"), data[1])


   def genTag(self):
      if self._tagIndex > 99999:
         self._tagIndex = 0
      st = repr(self._tagIndex)
      self._tagIndex += 1
      self._waitTag = "#" + "0"*(5 - len(st)) + st
      return self._waitTag
      

   def sendTokens(self, *tokens):
      s = util.join_tokens(*tokens)
      # convert from unicode to 8-bit ascii
      self.sendLine(str(s))


   def logUnmatched(self, tag, response, data):
      log.msg("Received unmatched \"" + response + "\" message tagged \"" + 
            tag + "\" with data " + str(data))


   def requestAI(self, algorithm):
      self._state = "tryrequestai"
      self.sendTokens(self.genTag(), "requestai", algorithm.encode("utf-8"))


   def requestAIList(self, team):
      self._state = "trylistai"
      self._aiAlgorithms = []
      self.sendTokens(self.genTag(), "listai", team)


   def response_aiinfo_trylistai(self, tag, data):
      self._aiAlgorithms.append(data[0].decode("utf-8"))

      
   def response_chatall_endgame(self, tag, data):
      decoded = [el.decode("utf-8") for el in data]
      self._messenger.guiUpdateChat("all", decoded)


   def response_chatall_joined(self, tag, data):
      decoded = [el.decode("utf-8") for el in data]
      self._messenger.guiUpdateChat("all", decoded)


   def response_chatall_playing(self, tag, data):
      decoded = [el.decode("utf-8") for el in data]
      self._messenger.guiUpdateChat("all", decoded)


   def response_chatteam_endgame(self, tag, data):
      decoded = [el.decode("utf-8") for el in data]
      self._messenger.guiUpdateChat("team", decoded)


   def response_chatteam_playing(self, tag, data):
      decoded = [el.decode("utf-8") for el in data]
      self._messenger.guiUpdateChat("team", decoded)


   def response_ejected_default(self, tag, data):
      self._messenger.guiAlert(data[0])
      self._state = "loggedin"
      self.sendTokens(self.genTag(), "listgames")
      self._messenger.guiLaunchGameListWindow()
   

   def response_no_login(self, tag, data):
      self._messenger.guiAlert(data[0])
      self.transport.loseConnection()


   def response_no_language(self, tag, data):
      self.response_ok_language(tag, data)


   def response_ok_endgame(self, tag, data):
      pass


   def response_ok_joined(self, tag, data):
      pass


   def response_ok_language(self, tag, data):
      if tag == self._waitTag:
         self._state = "login"
         self.sendTokens(self.genTag(), "login", 
               self._messenger.getUsername().encode("utf-8"), 
               self._messenger.getPassword().encode("utf-8"))
      else:
         logUnmatched(tag, "ok", data)


   def response_ok_login(self, tag, data):
      if tag == self._waitTag:
         self._state = "loggedin"
         self.sendTokens(self.genTag(), "listgames")
         self._messenger.guiLaunchGameListWindow()
      else:
         self.logUnmatched(tag, "ok", data)


   def response_ok_loggedin(self, tag, data):
      pass


   def response_ok_playing(self, tag, data):
      pass


   def response_ok_protocol(self, tag, data):
      if tag == self._waitTag:
         lang = locale.getdefaultlocale()[0]
         if lang != None:
            self._state = "language"
            self.sendTokens(self.genTag(), "language", lang)
         else:
            self._state = "login"
            self.sendTokens(self.genTag(), "login", 
                  self._messenger.getUsername().encode("utf-8"), 
                  self._messenger.getPassword().encode("utf-8"))
      else:
         logUnmatched(tag, "ok", data)


   def response_ok_tryjoin(self, tag, data):
      log.msg("called Protocol.response_ok_tryjoin()")
      if tag == self._waitTag:
         if self._game2Status[self._gameJoined] == GAMESTATUS_NEW:
            self._state = "joined"
            self._messenger.guiLaunchRegistrationWindow()
            self.sendTokens(self.genTag(), "listplayers")
         else:
            self._state = "playing"
            # wait for pawninfo
      else:
         self.logUnmatched(tag, "ok", data)


   def response_ok_tryleave(self, tag, data):
      log.msg("called Protocol.response_ok_tryleave()")
      if tag == self._waitTag:
         self._state = "loggedin"
         self._messenger.guiLaunchGameListWindow()
         self.sendTokens(self.genTag(), "listgames")
      else:
         self.logUnmatched(tag, "ok", data)


   def response_ok_trylistai(self, tag, data):
      log.msg("called Protocol.response_ok_trylistai()")
      if tag == self._waitTag:
         self._state = "loggedin"
         self._messenger.guiSelectAI(self._aiAlgorithms)
      else:
         self.logUnmatched(tag, "ok", data)


   def response_ok_trymove(self, tag, data):
      log.msg("called Protocol.response_ok_trymove()")
      if tag == self._waitTag:
         self._state = "playing"
         self._messenger.guiDisableMove()
      else:
         self.logUnmatched(tag, "ok", data)


   def response_ok_trynewgame(self, tag, data):
      log.msg("called Protocol.response_ok_trynewgame()")
      if tag == self._waitTag:
         self._state = "joined"
         self._messenger.guiLaunchRegistrationWindow()
         self.sendTokens(self.genTag(), "listplayers")
      else:
         self.logUnmatched(tag, "ok", data)


   def response_ok_tryrequestai(self, tag, data):
      self._state = "joined"


   def response_no_trylistai(self, tag, data):
      log.msg("failed to list ai clients")
      self._state = "joined"


   def response_no_tryjoin(self, tag, data):
      log.msg("denied entry to a game")
      self._messenger.guiAlert(data[0])
      self._state = "loggedin"


   def response_no_tryrequestai(self, tag, data):
      log.msg("AI client request denied")
      self._messenger.guiAlert(data[0])
      self._state = "joined"
      

   def response_gameinfo_loggedin(self, tag, data):
      log.msg("received gameinfo " + str(data))
      decoded = [data[0].decode("utf-8")] + data[1:]
      self._game2Status[decoded[0]] = decoded[1]
      self._messenger.guiAddGame(decoded)


   def response_gameinfo_tryjoin(self, tag, data):
      self.response_gameinfo_tryjoin(self, tag, data)


   def response_gameover_playing(self, tag, data):
      log.msg("received gameover " + str(data))
      self._state = "endgame"
      self._messenger.guiAlert(data[1])
      self._history = []
      self.sendTokens(self.genTag(), "history")


   def response_gameremoved_loggedin(self, tag, data):
      log.msg("received gameremoved info " + str(data))
      decoded = [el.decode("utf-8") for el in data]
      self._messenger.guiRemoveGame(decoded)


   def response_gamestart_default(self, tag, data):
      log.msg("received gamestart " + str(data))
      self._state = "playing"
      self._messenger.guiUpdateStatusBar(_("Preparing to start the game..."))


   def response_history_endgame(self, tag, data):
      log.msg("received history + " + str(data))
      if data[0] == "end":
         self._messenger.guiUpdateHistory(self._history)
      else:
         turnData = []
         for moveStr in data[1:]:
            turnData.append(moveStr.split())
         self._history.append(turnData)
         

   def response_history_playing(self, tag, data):
      self.response_history_endgame(tag, data)


   def response_move_playing(self, tag, data):
      log.msg("received move " + str(data))
      self._messenger.guiDisplayMove(data)


   def response_no_default(self, tag, data):
      self._setPreviousState()
      self._messenger.guiAlert(data[0])


   def response_no_trysetteam(self, tag, data):
      self._state = "joined"
      self._messenger.guiAlert(data[0])


   def response_ok_trysetteam(self, tag, data):
      self._state = "playing"


   def response_ok_tryvote(self, tag, data):
      self._state = "joined"
      self._messenger.guiDisableVoteButton()


   def response_pawninfo_playing(self, tag, data):
      log.msg("received pawninfo " + str(data))
      self._pawnInfo[self._pawn2Index[data[0]]] = \
            [data[1].decode("utf-8"), int(data[2]), 
            [int(data[3]), int(data[4]), int(data[5]), int(data[6]), int(data[7])]]
      if None not in self._pawnInfo:
         self._messenger.guiLaunchMainWindow(self._pawnInfo)
      

   def response_playerinfo_joined(self, tag, data):
      log.msg("received playerinfo " + str(data))
      decoded = [data[0].decode("utf-8")] + data[1:]
      self._messenger.guiAddPlayer(decoded)


   def response_playerinfo_default(self, tag, data):
      log.msg("received playerinfo " + str(data))
      decoded = [data[0].decode("utf-8")] + data[1:]
      self._messenger.guiAddPlayer(decoded)


   def response_playerleave_joined(self, tag, data):
      log.msg("received playerleave " + str(data))
      decoded = [el.decode("utf-8") for el in data]
      self._messenger.guiRemovePlayer(decoded)


   def response_playerleave_playing(self, tag, data):
      log.msg("received playerleave " + str(data))
      self._messenger.guiAlert(_("Player \"%(playername)s\" disconnected from the server.") %
            {"playername" : data[0].decode("utf-8")})


   def response_playerleave_endgame(self, tag, data):
      self.response_playerleave_playing(tag, data)


   def response_rejoin_playing(self, tag, data):
      log.msg("received rejoin " + str(data))
      self._messenger.guiAlert(_("Player \"%(playername)s\" has rejoined the game.") %
            {"playername" : data[0].decode("utf-8")})


   def response_stuck_playing(self, tag, data):
      log.msg("received stuck " + str(data))
      self._messenger.guiPawnStuck(data[0])


   def response_turnnum_playing(self, tag, data):
      log.msg("received turnnum " + str(data))
      self._messenger.guiSetTurnNum(data[0])


   def response_turn_playing(self, tag, data):
      log.msg("received turn " + str(data))
      self._messenger.guiSetPawnTurn(data[0])


   def setMessenger(self, m):
      self._messenger = m


   def setTeam(self, team):
      self._state = "trysetteam"
      self.sendTokens(self.genTag(), "setteam", team)


   def sendChat(self, text, sendTo):
      if sendTo == _("all"):
         self.sendTokens(self.genTag(), "chatall", text.encode("utf-8"))
      elif sendTo == _("team"):
         self.sendTokens(self.genTag(), "chatteam", text.encode("utf-8"))


   def shutdown(self):
      self._state = "shutdown"
      self.disconnect()


   def vote(self):
      self._state = "tryvote"
      self.sendTokens(self.genTag(), "votestart", "True")



