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



from twisted.internet import protocol, reactor
from twisted.protocols import basic
from twisted.python import log
import re, shlex, sys, sets
from londonlaw.common.protocol import *
from londonlaw.common.Pawn import *
from londonlaw.common import util, path, map


class BaseAIProtocolError(Exception):
   pass


# Base class for AI players.  Knows how to communicate with the server,
# keeps track of pawn information and game history, has some basic
# pathfinding/distance algorithms.
class BaseAIProtocol(basic.LineOnlyReceiver):

   def __init__(self):
      self._state              = "init"
      self._tagIndex           = 1
      self._pawns              = {}
      self._myPawns            = {}
      self._history            = [{} for i in range(25)]
      self._turnNum            = 0
      self._lastMover          = None
      self._lastXSurfacingTurn = None
      self._players            = sets.Set()
      self._gameStatus         = None


   def connectionLost(self, reason):
      #reactor.stop()
      print "AI: connection lost"


   def connectionMade(self):
      self._username = self.factory.username
      self._password = self.factory.password
      self._gameroom = self.factory.gameroom
      self._team     = self.factory.team
      self._state    = "protocol"
      self.sendTokens(self.genTag(), "protocol", PROTOCOL_VERSION)


   # called when this AI needs to make a move
   def doTurn(self, pawnName):
      raise NotImplementedError("doTurn must be implemented in derived classes.")


   # Find sets of locations where Mr. X safely move on the next turn.
   # Returns a list of Sets: the first Set is locations at least distance
   # 1 from all detectives, the second Set is locations at least distance
   # 2, etc. (up to the maximum map distance).  Note that moves at distance
   # 1 are UNsafe.
   def safeMoves(self, loc=None):
      if loc == None:
         loc = self._pawns['X'].getLocation()
      if loc == -1:
         raise BaseAIProtocolError("Cannot determine safe X moves when X location is unknown")
       
      dets      = ['Red', 'Yellow', 'Green', 'Blue', 'Black']
      detLocs   = [self._pawns[d].getLocation() for d in dets]
      allMoves  = path.possible_destinations(loc, 1, eliminate=[sets.Set(detLocs)])
      distances = [path.distance(self._pawns[d].getLocation(),
            tickets=self._pawns[d]._tickets) for d in dets]

      def findSafe(threshold):
         safe = allMoves.copy()
         for dest in allMoves:
            for dist in distances:
               if dist[dest] < threshold:
                  safe.remove(dest)
                  break
         return safe

      return [findSafe(threshold) for threshold in range(1, map.MAX_DISTANCE + 1)]


   def genTag(self):
      if self._tagIndex > 99999:
         self._tagIndex = 0
      st = repr(self._tagIndex)
      self._tagIndex += 1
      self._waitTag = "#" + "0"*(5 - len(st)) + st
      return self._waitTag

   
   def lineReceived(self, line):
      try:
         tokens = shlex.split(line)
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
         log.msg("tokens = " + str(tokens))
         log.msg("Received unhandled server message: \"" + line + "\" state = \"" + self._state + "\"")


   def makeMove(self, data):
      self._state = "trymove"
      log.msg("move data = " + str(data))
      if len(data) == 3:
         self.sendTokens(self.genTag(), "move", data[0], data[1], data[2])
      elif len(data) == 5:
         self.sendTokens(self.genTag(), "doublemove", 
               data[0], data[1], data[2], data[3], data[4])
      else:
         raise BaseAIProtocolError("makeMove() received illegal data length; data = " + str(data))


   def response_bad_default(self, tag, args):
      log.msg("received 'bad' response, state = " + self._state + ", reason = " + str(args))
      self.transport.loseConnection()


   def response_chatall_default(self, tag, args):
      pass


   def response_chatteam_default(self, tag, args):
      pass


   def response_ejected_default(self, tag, data):
      log.msg("received 'ejected' response")
      self.transport.loseConnection()


   def response_gameover_default(self, tag, args):
      self.transport.loseConnection()


   def response_gameinfo_default(self, tag, args):
      if len(args) >= 2:
         try:
            name   = args[0].decode("utf-8")
            status = args[1]
            if name == self._gameroom:
               self._gameStatus = status
         except:
            pass


   def response_gamestart_default(self, tag, args):
      self._state = "playing"


   def response_history_playing(self, tag, args):
      moves = [moveStr.split() for moveStr in args[1:]]
      for move in moves:
         if args[0] == '0':
            self._history[0][move[0]] = int(move[1])
         else:
            self._history[int(args[0])][move[0]] = (int(move[1]), move[2])
            if move[0] == 'X' and int(move[1]) != -1:
               self._lastXSurfacingTurn = int(args[0])


   def response_move_playing(self, tag, args):
      self._pawns[args[0]].setLocation(int(args[1]))
      self._pawns[args[0]].removeTicket(args[2])
      self._history[self._turnNum][args[0]] = (int(args[1]), args[2])
      if args[0] == "X" and int(args[1]) != -1:
         self._lastXSurfacingTurn = self._turnNum
      if args[0] == self._lastMover:
         self._pawns[args[0]].removeTicket("double")
      self._lastMover = args[0]


   def response_no_default(self, tag, args):
      log.msg("received 'no' response, state = " + self._state + ", reason = " + str(args))
      self.transport.loseConnection()


   def response_no_protocol(self, tag, args):
      self.transport.loseConnection()


   def response_no_trysetteam(self, tag, args):
      self.sendChat("I was unable to select team \"" + self._team + 
            "\".  You need to make room for me on that team!", "all")
      self.sendChat("Logging out.", "all")
      self.transport.loseConnection()


   def response_ok_trylistgames(self, tag, args):
      if self._gameStatus == GAMESTATUS_NEW:
         self._state = "tryjoin"
         self.sendTokens(self.genTag(), "join", self._gameroom.encode("utf-8"))
      elif self._gameStatus == GAMESTATUS_INPROGRESS:
         self._state = "tryrejoin"
         self.sendTokens(self.genTag(), "join", self._gameroom.encode("utf-8"))
      elif self._gameStatus == None:
         log.msg("Specified game not found; exiting.")
         self.transport.loseConnection()
      else:
         log.msg("Cannot join completed game; exiting.")
         self.transport.loseConnection()


   def response_ok_login(self, tag, args):
      self._state = "trylistgames"
      self.sendTokens(self.genTag(), "listgames")


   def response_ok_playing(self, tag, args):
      pass


   def response_ok_protocol(self, tag, args):
      self._state = "login"
      self.sendTokens(self.genTag(), "login", self._username, self._password)


   def response_ok_tryjoin(self, tag, args):
      self._state = "trylistplayers"
      self.sendTokens(self.genTag(), "listplayers")


   def response_ok_trylistplayers(self, tag, args):
      self._state = "trysetteam"
      self.sendTokens(self.genTag(), "setteam", self._team)


   def response_ok_trymove(self, tag, data):
      self._state = "playing"


   def response_ok_tryrejoin(self, tag, args):
      log.msg("rejoined an in-progress game")
      self._state = "playing"


   def response_ok_trysetteam(self, tag, args):
      self._state = "tryvote"
      self.sendTokens(self.genTag(), "votestart", "True")


   def response_ok_tryvote(self, tag, args):
      self._state = "ready"


   def response_pawninfo_playing(self, tag, args):
      p = Pawn(args[0])
      p.setPlayer(args[1].decode("utf-8"))
      p.setLocation(int(args[2]))
      p.setTicketAmount("taxi", int(args[3]))
      p.setTicketAmount("bus", int(args[4]))
      p.setTicketAmount("underground", int(args[5]))
      p.setTicketAmount("black", int(args[6]))
      p.setTicketAmount("double", int(args[7]))

      self._pawns[p.getName()] = p
      if p.getPlayer() == self._username:
         self._myPawns[p.getName()] = p
      
      if p.getName() == "X":
         self._history[0]['X'] = p.getLocation()
   

   def response_stuck_playing(self, tag, args):
      pass


   def response_turn_playing(self, tag, args):
      if args[0] in self._myPawns.keys():
         self.doTurn(args[0])


   def response_turnnum_playing(self, tag, args):
      self._turnNum = int(args[0])


   def response_playerinfo_default(self, tag, args):
      self._players.add(args[0].decode("utf-8"))


   def response_playerleave_default(self, tag, args):
      pass


   def response_playerleave_ready(self, tag, args):
      username = args[0].decode("utf-8")
      if username in self._players:
         self._players.remove(username)
      if len(self._players) == 1:
         # if this bot is the last player, leave the gameroom
         self.transport.loseConnection()


   def response_playerleave_trysetteam(self, tag, args):
      self.response_playerleave_ready(tag, args)


   def response_playerleave_votestart(self, tag, args):
      self.response_playerleave_ready(tag, args)


   def response_rejoin_default(self, tag, args):
      pass


   def sendChat(self, text, sendTo):
      if sendTo == "all":
         self.sendTokens(self.genTag(), "chatall", text.encode("utf-8"))
      elif sendTo == "team":
         self.sendTokens(self.genTag(), "chatteam", text.encode("utf-8"))


   def sendTokens(self, *tokens):
      s = util.join_tokens(*tokens)
      self.sendLine(str(s))



class BaseAIFactory(protocol.ClientFactory):
   protocol = BaseAIProtocol

   def __init__(self, username, password, gameroom, team):
      self.username = username
      self.password = password
      self.gameroom = gameroom
      self.team     = team

   def clientConnectionFailed(self, connector, reason):
      log.msg("Failed to connect to specified server.")
      reactor.stop()



