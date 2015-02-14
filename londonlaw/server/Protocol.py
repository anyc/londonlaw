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
import re, shlex, sys
from londonlaw.common import util
from londonlaw.common.protocol import *
from Game import *
import GameRegistry


class ServerError(Exception):
   pass

class IllegalCommand(Exception):
   pass

class DeniedCommand(Exception):
   pass
   


"""
Client states:
   "init"    : client has connected but has not passed a protocol check
   "compat"  : client has passed a protocol check
   "player"  : client has provided a username, but has not joined a game
   "joined"  : client has been joined to a game
   "playing" : client is currently playing a game
"""

registry = GameRegistry.getHandle()

class LLawServerProtocol(basic.LineOnlyReceiver):
   def __init__(self):
      self._game            = None
      self._state           = "init"
      self._username        = None
      self._password        = None
      self._voteStart       = False


   def cmd_chatall_endgame(self, tag, args):
      self.cmd_chatall_joined(tag, args)


   def cmd_chatall_joined(self, tag, args):
      if args == []:
         raise IllegalCommand("insufficient arguments")
      else:
         self.sendOk(tag)
         for player in self._game.getPlayers():
            try:
               registry.getClient(player).sendUntagged("chatall", self._username, args[0])
            except KeyError:
               pass


   def cmd_chatall_playing(self, tag, args):
      self.cmd_chatall_joined(tag, args)


   def cmd_chatteam_endgame(self, tag, args):
      self.cmd_chatteam_playing(tag, args)


   def cmd_chatteam_playing(self, tag, args):
      if args == []:
         raise IllegalCommand("insufficient arguments")
      else:
         self.sendOk(tag)
         for player in self._game.getTeam(self._username).getPlayers():
            try:
               registry.getClient(player).sendUntagged("chatteam", self._username, args[0])
            except KeyError:
               pass


   def cmd_doublemove_playing(self, tag, args):
      if len(args) < 5:
         raise IllegalCommand("insufficient arguments")
      pawn = self._game.getCurrentPawn()
      if args[0] == pawn.getName().lower():
         if self._username == pawn.getPlayer() and self._game.isLegalMove(
               pawn, int(args[1]), args[2], int(args[3]), args[4]):
            self.sendOk(tag)
            self._game.makeMove(pawn, int(args[1]), args[2], int(args[3]), args[4])
         else:
            self.sendNo(tag, "That move is illegal.")
      else:
         self.sendNo(tag, "It is not that pawn's turn.")


   def cmd_history_endgame(self, tag, args):
      self.sendOk(tag)
      self.sendHistory()
      

   def cmd_history_playing(self, tag, args):
      self.sendOk(tag)
      self.sendHistory()


   def cmd_join_player(self, tag, args):
      if args == []:
         raise IllegalCommand("insufficient arguments")
      else:
         name = args[0]
         try:
            g = registry.getGame(name)
            g.addPlayer(self._username)
            registry.removeUnjoinedUser(self._username)
            self.sendOk(tag)
            if g.getStatus() == GAMESTATUS_NEW:
               self._state = "joined"
               # number of players in this game needs to be updated
               for p in registry.getUnjoinedUsers():
                  registry.getClient(p).sendUntagged("gameinfo", g.getName(), g.getStatus(),
                        g.getType(), str(g.getNumPlayers()))
            else:
               self._state = "playing"
               self._game.syncPlayer(self._username)
         except KeyError:
            raise DeniedCommand("unrecognized game name")
         except TeamError, e:
            raise DeniedCommand(str(e))
         except GameError, e:
            raise DeniedCommand(str(e))


   def cmd_leave_joined(self, tag, args):
      self._game.removePlayer(self._username)
      self._state     = "player"
      self._voteStart = False
      # number of players in this game needs to be updated
      for p in registry.getUnjoinedUsers():
         registry.getClient(p).sendUntagged("gameinfo", self._game.getName(), 
               self._game.getStatus(), self._game.getType(), str(self._game.getNumPlayers()))
      registry.addUnjoinedUser(self._username)
      self.sendOk(tag)
      # kill the game if this was the last player
      self.testRemoveGame()
      self._game = None


   def cmd_listgames_player(self, tag, args):
      for g in registry.getGameList():
         self.sendUntagged("gameinfo", g.getName(), g.getStatus(), 
               g.getType(), str(g.getNumPlayers()))
      self.sendOk(tag)


   def cmd_listplayers_joined(self, tag, args):
      for player in self._game.getPlayers():
         self.sendPlayerInfo(player)
      self.sendOk(tag)


   def cmd_move_playing(self, tag, args):
      if len(args) < 3:
         raise IllegalCommand("insufficient arguments")
      pawn = self._game.getCurrentPawn()
      if args[0] == pawn.getName().lower():
         if self._username == pawn.getPlayer() and \
         self._game.isLegalMove(pawn, int(args[1]), args[2]):
            self.sendOk(tag)
            self._game.makeMove(pawn, int(args[1]), args[2])
         else:
            self.sendNo(tag, "That move is illegal.")
      else:
         self.sendNo(tag, "It is not that pawn's turn.")


   def cmd_newgame_player(self, tag, args):
      if len(args) < 2:
         raise IllegalCommand("insufficient arguments")
      else:
         name = args[0]
         if registry.hasGame(name):
            raise DeniedCommand("That game name is already in use.")
         else:
            try:
               g = Game(name, args[1])
               self.sendOk(tag)
               g.addPlayer(self._username)
               registry.addGame(g)
               self._state = "joined"
               registry.removeUnjoinedUser(self._username)
               log.msg("New game \"" + name + "\" created by player \"" + self._username + "\"")
               for p in registry.getUnjoinedUsers():
                  registry.getClient(p).sendUntagged("gameinfo", g.getName(), g.getStatus(),
                        g.getType(), str(g.getNumPlayers()))
            except GameError, e:
               raise DeniedCommand(str(e))


   def cmd_login_default(self, tag, args):
      raise DeniedCommand("already logged in")


   def cmd_login_compat(self, tag, args):
      if len(args) < 2:
         raise IllegalCommand("insufficient arguments")
      else:
         try:
            registry.registerUser(args[0], args[1])
            self._username = args[0]
            self._state    = "player"
            registry.addClient(self)
            registry.addUnjoinedUser(self._username)
            log.msg("Player \"" + args[0] + "\" has signed on")
            self.sendOk(tag)
         except GameRegistry.PasswordError, e:
            raise DeniedCommand(str(e))
         except GameRegistry.UserError, e:
            raise DeniedCommand(str(e))


   def cmd_login_init(self, tag, args):
      raise DeniedCommand("protocol version not verified")


   def cmd_noop_default(self, tag, args):
      self.sendOk(tag)
   
   
   def cmd_pawninfo_playing(self, tag, args):
      self.sendOk(tag)
      self.sendPawnInfo()

   
   def cmd_protocol_default(self, tag, args):
      raise DeniedCommand("protocol already verified")

   def cmd_protocol_init(self, tag, args):
      if len(args) > 0:
         if args[0] == PROTOCOL_VERSION:
            self._state = "compat"
            self.sendOk(tag)
         elif args[0].isdigit():
            raise IllegalCommand("Incompatible protocol version.")
         else:
            raise IllegalCommand("Unrecognized protocol string.")
      else:
         raise IllegalCommand("insufficient arguments.")


   def cmd_setteam_joined(self, tag, args):
      if len(args) == 0:
         raise IllegalCommand("insufficient arguments")
      try:
         self._game.setTeam(self._username, args[0])
      except TeamError, e:
         raise DeniedCommand(str(e))
      self.sendOk(tag)            


   def cmd_votestart_joined(self, tag, args):
      if len(args) == 0:
         raise IllegalCommand("insufficient arguments")
      vote = args[0].lower()
      try:
         self._voteStart = util.parse_bool(vote)
      except ValueError, e:
         raise IllegalCommand(str(e))
      self.sendOk(tag)
      for listener in self._game.getListeners():
         listener.playerModified(self.getUsername())
      self._game.testGameStart()


   def cmd_whatturnnum_playing(self, tag, args):
      self.sendTokens(tag, "turnnum", `self._game.getTurnNum()`)


   def cmd_whoseturn_playing(self, tag, args):
      self.sendTokens(tag, "turn", self._game.getCurrentPawn().getName())


   def connectionLost(self, reason):
      if self._game is not None:
         self._game.removePlayer(self._username)
         # number of players in this game needs to be updated
         for p in registry.getUnjoinedUsers():
            registry.getClient(p).sendUntagged("gameinfo", self._game.getName(), 
                  self._game.getStatus(), self._game.getType(), 
                  str(self._game.getNumPlayers()))
         # kill the game if this was the last player
         self.testRemoveGame()
      if self._username is not None:
         registry.removeClient(self)
         registry.removeUnjoinedUser(self._username)
         log.msg("Connection lost to player \"" + self._username + "\"")


   def getUsername(self):
      return self._username
   
   def getPassword(self):
      return self._password
   
   def getVote(self):
      return self._voteStart


   def lineReceived(self, line):
      try:
         tokens = shlex.split(line)
         if len(tokens) == 0:
            raise ServerError("insufficient arguments")
         if len(tokens[0]) > 0 and tokens[0][0] == "#":
            if len(tokens) < 2:
               raise ServerError("insufficient arguments")
            tag       = tokens[0]
            command   = tokens[1]
            arguments = tokens[2:]
         else:
            tag       = "-"
            command   = tokens[0]
            arguments = tokens[1:]
         
         if not (re.match(r"^#\d+$", tag) or tag == "-"):
            raise ServerError("illegal tag")

         f = getattr(self, "".join(("cmd_", command, "_", self._state)), None)
         if f is None:
            # Try a catch-all method for the command
            f = getattr(self, "".join(("cmd_", command, "_default")), None)
         if f is None:
            self.sendBad(tag, "unrecognized command")
            return
         
         try:
            f(tag, arguments)
         except IllegalCommand, e:
            self.sendBad(tag, str(e))
         except DeniedCommand, e:
            self.sendNo(tag, str(e))
#         except Exception, e:
#            self.sendBad(tag, "Server error: " + str(e))
      
      except ServerError, e:
         self.sendTokens("*", "bad", str(e))
      except ValueError, e:
         self.sendTokens("-", "bad", str(e))


   def sendBad(self, tag, message=None):
      if message:
         self.sendTokens(tag, "bad", message)
      else:
         self.sendTokens(tag, "bad")

   def sendHistory(self):
      hist = self._game.getHistory()
      for turn in range(len(hist)):
         moves = []
         for move in hist[turn]:
            # hide Mr. X's location as appropriate
            if move[0] == "X" and self._state == "playing" \
            and self._username != self._game.getPawnByName("X").getPlayer() \
            and not turn in (3, 8, 13, 18, 24):
               adjustedMove = move[:1] + ("-1",) + move[2:]
            else:
               adjustedMove = move
            moves.append(" ".join(adjustedMove))
         if moves != []:
            self.sendUntagged("history", repr(turn), *moves)
      self.sendUntagged("history", "end")

   def sendNo(self, tag, message=None):
      if message:
         self.sendTokens(tag, "no", message)
      else:
         self.sendTokens(tag, "no")

   def sendOk(self, tag, *tokens):
      self.sendTokens(tag, "ok", *tokens)

   def sendTokens(self, *tokens):
      s = util.join_tokens(*tokens)
      self.sendLine(s)
   
   def sendUntagged(self, *tokens):
      self.sendTokens("*", *tokens)
   
   def sendPawnInfo(self):
      for pawn in self._game.getPawns():
         if pawn == self._game.getPawnByName("X") \
         and self._username != pawn.getPlayer() and not self._game.isSurfacingTurn():
            loc = -1
         else:
            loc = pawn.getLocation()
         self.sendUntagged("pawninfo", pawn.getName(), 
               pawn.getPlayer(), `loc`,
               `pawn.getTicketAmount("taxi")`,
               `pawn.getTicketAmount("bus")`,
               `pawn.getTicketAmount("underground")`,
               `pawn.getTicketAmount("black")`,
               `pawn.getTicketAmount("double")`)


   def sendPlayerInfo(self, username):
      pawns = [p.getName() for p in self._game.getPawnsForPlayer(username)]
      pawnToken = " ".join(pawns)
      self.sendUntagged(
         "playerinfo",
         username,
         self._game.getTeam(username).getName(),
         str(registry.getClient(username).getVote()),
         pawnToken)

   def sendPlayerLeave(self, username):
      self.sendUntagged("playerleave", username)

   def setGame(self, game):
      self._game = game

   def setVote(self, vote):
      self._voteStart = vote

   def testRemoveGame(self):
      if self._game.getNumPlayers() == 0 and \
      (self._game.getStatus() == GAMESTATUS_NEW or 
      self._game.getStatus() == GAMESTATUS_COMPLETE):
         registry.removeGame(self._game)
         for p in registry.getUnjoinedUsers():
            registry.getClient(p).sendUntagged("gameremoved", self._game.getName())



class ProtocolGameListener:
   __implements__ = (IGameListener,)
   
   def __init__(self, username):
      self._username = username
   
   def announceHistory(self, history):
      registry.getClient(self._username).sendHistory()

   def announcePawnInfo(self):
      registry.getClient(self._username).sendPawnInfo()

   def announceTurnNum(self, num):
      registry.getClient(self._username).sendUntagged("turnnum", repr(num))

   def announceTurn(self, pawn):
      registry.getClient(self._username).sendUntagged("turn", pawn.getName())

   def gameOver(self, winningTeam, reason):
      registry.getClient(self._username)._state = "endgame"
      registry.getClient(self._username).sendUntagged(
         "gameover",
         winningTeam.getName(),
         reason)

   def gameStart(self, game):
      registry.getClient(self._username)._state = "playing"
      registry.getClient(self._username).sendUntagged("gamestart")
   
   def pawnMove(self, game, pawn, *moves):
      if len(moves) == 1:
         (dest, transport) = moves[0]
         registry.getClient(self._username).sendUntagged("move", 
               pawn.getName(), repr(dest), transport)
      elif len(moves) == 2:
         (dest1, transport1) = moves[0]
         (dest2, transport2) = moves[1]
         registry.getClient(self._username).sendUntagged(
            "doublemove",
            pawn.getName(),
            repr(dest1), 
            transport1,
            repr(dest2),
            transport2)
      else:
         raise ServerError("invalid number of moves")
   
   def pawnStuck(self, pawn):
      registry.getClient(self._username).sendUntagged("stuck", pawn.getName())

   def pawnSetTicketAmount(self, game, pawn, ticket, amount):
      raise NotImplementedError()
   
   def playerJoin(self, game, player):
      registry.getClient(self._username).sendPlayerInfo(player)
   
   def playerJoinTeam(self, game, player, team):
      registry.getClient(self._username).sendPlayerInfo(player)
   
   def playerLeave(self, game, player):
      registry.getClient(self._username).sendPlayerLeave(player)
   
   def playerLeaveTeam(self, game, player, team):
      registry.getClient(self._username).sendPlayerInfo(player)
   
   def playerModified(self, player):
      registry.getClient(self._username).sendPlayerInfo(player)

   def playerRejoin(self, player):
      registry.getClient(self._username).sendUntagged("rejoin", player)

   def playerVoteStart(self, game, player, vote):
      registry.getClient(self._username).sendPlayerInfo(player)





# arch-tag: DO_NOT_CHANGE_c2f8aaed-8c42-4541-9c5d-309842a4fd49 
