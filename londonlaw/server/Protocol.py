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
import re, shlex, sys, gettext, os
from londonlaw.common import util
from londonlaw.aiclients import ai_list
from londonlaw.common.protocol import *
from Game import *
import GameRegistry


class ServerError(Exception):
   def ustr(self):
      return self.args[0]

class IllegalCommand(Exception):
   def ustr(self):
      return self.args[0]

class DeniedCommand(Exception):
   def ustr(self):
      return self.args[0]
   


"""
Client states:
   "init"    : client has connected but has not passed a protocol check
   "compat"  : client has passed a protocol check
   "player"  : client has provided a username, but has not joined a game
   "joined"  : client has been joined to a game
   "playing" : client is currently playing a game
   "admin"   : client is an administrator
"""

class LLawServerProtocol(basic.LineOnlyReceiver):
   def __init__(self):
      self._game            = None
      self._state           = "init"
      self._username        = None
      self._password        = None
      self._voteStart       = False
      # server messages to remote clients are in english by default,
      # unless the client uses the 'language' command
      self.trans = gettext.NullTranslations()



   def cmd_allplayers_admin(self, tag, args):
      for player in GameRegistry.registry.getUserList():
         self.sendUntagged("playername", player.encode("utf-8"))
      self.sendOk(tag)
      

   def cmd_ban_admin(self, tag, args):
      if args == []:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         try:
            GameRegistry.registry.removePassword(args[0])
            self.sendOk(tag)
         except KeyError:
            raise DeniedCommand(self.trans.ugettext("Player name not found."))


   def cmd_chatall_endgame(self, tag, args):
      self.cmd_chatall_joined(tag, args)


   def cmd_chatall_joined(self, tag, args):
      if args == []:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         self.sendOk(tag)
         for player in self._game.getPlayers():
            try:
               GameRegistry.registry.getClient(player).sendUntagged("chatall", self._username.encode("utf-8"), args[0])
            except KeyError:
               pass


   def cmd_chatall_playing(self, tag, args):
      self.cmd_chatall_joined(tag, args)


   def cmd_chatteam_endgame(self, tag, args):
      self.cmd_chatteam_playing(tag, args)


   def cmd_chatteam_playing(self, tag, args):
      if args == []:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         self.sendOk(tag)
         for player in self._game.getTeam(self._username).getPlayers():
            try:
               GameRegistry.registry.getClient(player).sendUntagged("chatteam", self._username.encode("utf-8"), args[0])
            except KeyError:
               pass


   def cmd_deletegame_admin(self, tag, args):
      if args == []:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         try:
            g = GameRegistry.registry.getGame(args[0].decode("utf-8"))
         except KeyError:
            raise DeniedCommand(self.trans.ugettext("Unrecognized game name."))

         playerList = g.getPlayers()[:]
         for player in playerList:
            g.removePlayer(player, force_remove=True)
            try:
               client = GameRegistry.registry.getClient(player)
               if client._game == g:
                  client._state     = "player"
                  client._voteStart = False
                  client._game      = None
                  client.sendUntagged("ejected", 
                        self.trans.ugettext("The server admin ejected you from this game.").encode("utf-8"))
            except KeyError:
               pass
         self.testRemoveGame(g, True)
         self.sendOk(tag)
      

   def cmd_deleteplayer_admin(self, tag, args):
      if args == []:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         username = args[0].decode("utf-8")
         try:
            GameRegistry.registry.deleteUser(username)
         except KeyError:
            raise DeniedCommand(self.trans.ugettext("Player name not found."))
         # if this player was connected, boot him out
         try:
            client = GameRegistry.registry.getClient(username)
            client.transport.loseConnection()
         except KeyError:
            pass
         self.sendOk(tag)


   def cmd_disconnect_admin(self, tag, args):
      if args == []:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         try:
            client = GameRegistry.registry.getClient(args[0].decode("utf-8"))
         except KeyError:
            raise DeniedCommand(self.trans.ugettext("No such user is connected."))
         client.transport.loseConnection()
         self.sendOk(tag)


   def cmd_doublemove_playing(self, tag, args):
      if len(args) < 5:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      pawn = self._game.getCurrentPawn()
      if args[0] == pawn.getName().lower():
         if self._username == pawn.getPlayer() and self._game.isLegalMove(
               pawn, int(args[1]), args[2], int(args[3]), args[4]):
            self.sendOk(tag)
            self._game.makeMove(pawn, int(args[1]), args[2], int(args[3]), args[4])
         else:
            self.sendNo(tag, self.trans.ugettext("That move is illegal.").encode("utf-8"))
      else:
         self.sendNo(tag, self.trans.ugettext("It is not that pawn's turn.").encode("utf-8"))


   # kicks a player out of a game, but not off the server
   def cmd_eject_admin(self, tag, args):
      if len(args) < 2:
         raise IllegalCommand("Insufficient arguments.")
      else:
         player = args[0].decode("utf-8")
         game   = args[1].decode("utf-8")
         try:
            g = GameRegistry.registry.getGame(game)
         except KeyError:
            raise DeniedCommand(self.trans.ugettext("Unrecognized game name."))
         
         if g.getStatus() == GAMESTATUS_NEW or g.getStatus() == GAMESTATUS_COMPLETE:
            if player in g.getPlayers():
               g.removePlayer(player, force_remove=True)
               try:
                  client = GameRegistry.registry.getClient(player)
                  if client._game == g:
                     client._state     = "player"
                     client._voteStart = False
                     client._game      = None
                     client.sendUntagged("ejected", 
                        self.trans.ugettext("The server admin ejected you from this game.").encode("utf-8"))
               except KeyError:
                  pass
            self.testRemoveGame(g, True)
            self.sendOk(tag)
         else:
            raise DeniedCommand(self.trans.ugettext("Game is in progress."))


   def cmd_language_default(self, tag, args):
      if args == []:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         try:
            # first try searching the installed locale dir
            t = gettext.translation("londonlaw", languages=[args[0]])
            self.trans = t
            self.sendOk(tag)
         except:
            try:
               # if that fails, try the local locale dir
               t = gettext.translation("londonlaw", "locale", languages=[args[0]])
               self.trans = t
               self.sendOk(tag)
            except:
               raise DeniedCommand(self.trans.ugettext("Unsupported language code."))


   def cmd_profile_admin(self, tag, args):
      if args == []:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         player = args[0].decode("utf-8")
         try:
            pw = GameRegistry.registry.getPassword(player)
            ip = GameRegistry.registry.getLastAddress(player)
            if pw == None:
               pw = "None"
            self.sendTokens(tag, "profile", pw.encode("utf-8"), str(ip))
         except KeyError:
            raise DeniedCommand(self.trans.ugettext("Player name not found."))


   def cmd_history_endgame(self, tag, args):
      self.sendOk(tag)
      self.sendHistory()
      

   def cmd_history_playing(self, tag, args):
      self.sendOk(tag)
      self.sendHistory()


   def cmd_join_player(self, tag, args):
      if args == []:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         name = args[0].decode("utf-8")
         try:
            g = GameRegistry.registry.getGame(name)
            g.addPlayer(self._username)
            GameRegistry.registry.removeUnjoinedUser(self._username)
            self.sendOk(tag)
            if g.getStatus() == GAMESTATUS_NEW:
               self._state = "joined"
               # number of players in this game needs to be updated
               for p in GameRegistry.registry.getUnjoinedUsers():
                  GameRegistry.registry.getClient(p).sendUntagged("gameinfo", g.getName().encode("utf-8"), 
                        g.getStatus(), g.getType(), str(g.getNumPlayers()))
            else:
               self._state = "playing"
               self._game.syncPlayer(self._username)
         except KeyError:
            raise DeniedCommand(self.trans.ugettext("Unrecognized game name."))
         except TeamError, e:
            raise DeniedCommand(self.trans.ugettext(e.ustr()))
         except GameError, e:
            raise DeniedCommand(self.trans.ugettext(e.ustr()))


   def cmd_leave_joined(self, tag, args):
      self._game.removePlayer(self._username)
      self._state     = "player"
      self._voteStart = False
      # number of players in this game needs to be updated
      for p in GameRegistry.registry.getUnjoinedUsers():
         GameRegistry.registry.getClient(p).sendUntagged("gameinfo", self._game.getName().encode("utf-8"), 
               self._game.getStatus(), self._game.getType(), str(self._game.getNumPlayers()))
      GameRegistry.registry.addUnjoinedUser(self._username)
      self.sendOk(tag)
      # kill the game if this was the last player
      self.testRemoveGame(self._game)
      self._game = None


   def cmd_listai_joined(self, tag, args):
      if len(args) > 0:
         if args[0] == "Mr. X":
            for algorithm, launcher in ai_list.X_ALGORITHMS:
               self.sendTokens(tag, "aiinfo", algorithm.encode("utf-8"))
            self.sendOk(tag)
         elif args[0] == "Detectives":
            for algorithm, launcher in ai_list.DETECTIVE_ALGORITHMS:
               self.sendTokens(tag, "aiinfo", algorithm.encode("utf-8"))
            self.sendOk(tag)
         else:
            raise DeniedCommand(self.trans.ugettext("Unrecognized team name."))
      else:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))


   def cmd_listgames_admin(self, tag, args):
      self.cmd_listgames_player(tag, args)


   def cmd_listgames_player(self, tag, args):
      for g in GameRegistry.registry.getGameList():
         self.sendUntagged("gameinfo", g.getName().encode("utf-8"), 
               g.getStatus().encode("utf-8"), g.getType().encode("utf-8"), str(g.getNumPlayers()))
      self.sendOk(tag)


   def cmd_listplayers_default(self, tag, args):
      if len(args) > 0:
         try:
            g = GameRegistry.registry.getGame(args[0].decode("utf-8"))
         except KeyError:
            raise DeniedCommand(self.trans.ugettext("Unrecognized game name."))
      elif self._state == "joined":
         g = self._game
      else:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))

      for player in g.getPlayers():
         self.sendPlayerInfo(player, g)
      self.sendOk(tag)


   def cmd_move_playing(self, tag, args):
      if len(args) < 3:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      pawn = self._game.getCurrentPawn()
      if args[0] == pawn.getName().lower():
         if self._username == pawn.getPlayer() and \
         self._game.isLegalMove(pawn, int(args[1]), args[2]):
            self.sendOk(tag)
            self._game.makeMove(pawn, int(args[1]), args[2])
         else:
            self.sendNo(tag, self.trans.ugettext("That move is illegal.").encode("utf-8"))
      else:
         self.sendNo(tag, self.trans.ugettext("It is not that pawn's turn.").encode("utf-8"))


   def cmd_newgame_player(self, tag, args):
      if len(args) < 2:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         name = args[0].decode("utf-8")
         if GameRegistry.registry.hasGame(name):
            raise DeniedCommand(self.trans.ugettext("That game name is already in use."))
         else:
            try:
               g = Game(name, args[1])
               self.sendOk(tag)
               g.addPlayer(self._username)
               GameRegistry.registry.addGame(g)
               self._state = "joined"
               GameRegistry.registry.removeUnjoinedUser(self._username)
               log.msg(util.printable(_("New game \"%(gamename)s\" created by player \"%(playername)s\"") %
                     {"gamename": name, "playername": self._username}))
               for p in GameRegistry.registry.getUnjoinedUsers():
                  GameRegistry.registry.getClient(p).sendUntagged("gameinfo", g.getName().encode("utf-8"), 
                        g.getStatus(), g.getType(), str(g.getNumPlayers()))
            except GameError, e:
               raise DeniedCommand(self.trans.ugettext(e.ustr()))


   def cmd_login_default(self, tag, args):
      raise DeniedCommand(self.trans.ugettext("Already logged in."))


   def cmd_login_compat(self, tag, args):
      if len(args) < 2:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         try:
            GameRegistry.registry.registerUser(args[0].decode("utf-8"), args[1].decode("utf-8"), 
                  self.transport.getPeer().host)
            self._username = args[0].decode("utf-8")
            if self._username == "admin":
               self._state = "admin"
            else:
               self._state = "player"
            GameRegistry.registry.addClient(self)
            GameRegistry.registry.addUnjoinedUser(self._username)
            log.msg(util.printable(_("Player \"%(playername)s\" has signed on") % 
                  {"playername" : self._username}))
            self.sendOk(tag)
         except GameRegistry.PasswordError, e:
            raise DeniedCommand(self.trans.ugettext(e.ustr()))
         except GameRegistry.UserError, e:
            raise DeniedCommand(self.trans.ugettext(e.ustr()))


   def cmd_login_init(self, tag, args):
      raise DeniedCommand(self.trans.ugettext("Protocol version not verified."))


   def cmd_noop_default(self, tag, args):
      self.sendOk(tag)
   
   
   def cmd_pawninfo_playing(self, tag, args):
      self.sendOk(tag)
      self.sendPawnInfo()

   
   def cmd_protocol_default(self, tag, args):
      raise DeniedCommand(self.trans.ugettext("Protocol version already verified."))

   def cmd_protocol_init(self, tag, args):
      if len(args) > 0:
         if args[0] == PROTOCOL_VERSION:
            self._state = "compat"
            self.sendOk(tag)
         elif args[0].isdigit():
            raise IllegalCommand(self.trans.ugettext("Incompatible protocol version."))
         else:
            raise IllegalCommand(self.trans.ugettext("Unrecognized protocol string."))
      else:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))


   def cmd_requestai_joined(self, tag, args):
      if len(args) > 0:
         requestedAlgorithm = args[0].decode("utf-8")
         launchScript       = None
         for algorithm, launcher in ai_list.X_ALGORITHMS + ai_list.DETECTIVE_ALGORITHMS:
            if algorithm == requestedAlgorithm:
               aidir = os.path.dirname(ai_list.__file__)
               launchScript = os.path.normpath(os.path.join(aidir, launcher))
               break
         if launchScript != None:
            self.sendOk(tag)
         log.msg(util.printable(_("Launching AI algorithm \"%(algorithm)s\" using script \"%(script)s\"" % 
            {"algorithm" : requestedAlgorithm, "script" : launchScript})))
         os.spawnl(os.P_NOWAIT, sys.executable, sys.executable, launchScript,
               self.generateBotName().encode("utf-8"), self._game.getName().encode("utf-8"))
      else:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))


   def cmd_setpassword_admin(self, tag, args):
      if len(args) < 2:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      else:
         try:
            GameRegistry.registry.setPassword(args[0].decode("utf-8"), args[1].decode("utf-8"))
            self.sendOk(tag)
         except KeyError:
            raise DeniedCommand(self.trans.ugettext("Player name not found."))


   def cmd_setteam_joined(self, tag, args):
      if len(args) == 0:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
      try:
         self._game.setTeam(self._username, args[0])
      except GameError, e:
         raise DeniedCommand(self.trans.ugettext(e.ustr()))
      except TeamError, e:
         raise DeniedCommand(self.trans.ugettext(e.ustr()))
      self.sendOk(tag)            


   def cmd_votestart_joined(self, tag, args):
      if len(args) == 0:
         raise IllegalCommand(self.trans.ugettext("Insufficient arguments."))
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
         for p in GameRegistry.registry.getUnjoinedUsers():
            GameRegistry.registry.getClient(p).sendUntagged("gameinfo", self._game.getName().encode("utf-8"), 
                  self._game.getStatus(), self._game.getType(), str(self._game.getNumPlayers()))
         # kill the game if this was the last player
         self.testRemoveGame(self._game)
      if self._username is not None:
         GameRegistry.registry.removeClient(self)
         GameRegistry.registry.removeUnjoinedUser(self._username)
         log.msg(util.printable(_("Connection lost to player \"%(playername)s\"") % 
            {"playername": self._username}))


   # compute a unique AI client username
   def generateBotName(self):
      # http://en.wikipedia.org/wiki/List_of_fictional_robots_and_androids
      names = ["HAL", "Calculon", "Bender", "Marvin", "Adam Link", "Chip", "Max", "Number 5", 
            "Rosie", "Cyberman", "Kamelion", "Number Six", "KITT", "KARR", "Voltron", "Data", 
            "Lore", "Leader One", "Cy-Kill", "Megatron", "Optimus Prime", "Unicron", "Conky", 
            "Tom Servo", "Metal Man", "Guts Man", "Dorothy", "Terminator"]
      random.shuffle(names)

      # attempt 1: try each name in random order
      for name in names:
         botname = name + " [bot]"
         if botname not in GameRegistry.registry.getConnectedUserList():
            return botname
      
      # attempt 2: pick a random name, and append a random integer
      valid = False
      while not valid:
         i = randint(1, 999)
         botname = names[0] + " " + str(i) + " [bot]"
         if botname not in GameRegistry.registry.getConnectedUserList():
            valid = True
      return botname
         

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
            raise ServerError(self.trans.ugettext("Insufficient arguments."))
         if len(tokens[0]) > 0 and tokens[0][0] == "#":
            if len(tokens) < 2:
               raise ServerError(self.trans.ugettext("Insufficient arguments."))
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
            self.sendBad(tag, self.trans.ugettext("Unrecognized command.").encode("utf-8"))
            return
         
         try:
            f(tag, arguments)
         except IllegalCommand, e:
            self.sendBad(tag, e.ustr().encode("utf-8"))
         except DeniedCommand, e:
            self.sendNo(tag, e.ustr().encode("utf-8"))
      
      except ServerError, e:
         self.sendBad("*", e.ustr().encode("utf-8"))
      except ValueError, e:
         print "value error:" + str(e)
         self.sendBad("-", str(e))


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
      # convert to ASCII if necessary--all unicode should already be safely encoded as UTF-8
      self.sendLine(str(s)) 
   
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
               pawn.getPlayer().encode("utf-8"), `loc`,
               `pawn.getTicketAmount("taxi")`,
               `pawn.getTicketAmount("bus")`,
               `pawn.getTicketAmount("underground")`,
               `pawn.getTicketAmount("black")`,
               `pawn.getTicketAmount("double")`)


   def sendPlayerInfo(self, username, game=None):
      if game == None:
         game = self._game
      pawns = [p.getName() for p in game.getPawnsForPlayer(username)]
      pawnToken = " ".join(pawns)
      try:
         vote = str(GameRegistry.registry.getClient(username).getVote())
      except KeyError:
         vote = "None"
      self.sendUntagged( "playerinfo", username.encode("utf-8"),
         game.getTeam(username).getName(), vote, pawnToken)

   def sendPlayerLeave(self, username):
      self.sendUntagged("playerleave", username.encode("utf-8"))

   def setGame(self, game):
      self._game = game

   def setVote(self, vote):
      self._voteStart = vote

   def testRemoveGame(self, game, force_remove=False):
      if game.getNumPlayers() == 0 and (force_remove or 
      (game.getStatus() == GAMESTATUS_NEW or game.getStatus() == GAMESTATUS_COMPLETE)):
         GameRegistry.registry.removeGame(game)
         for p in GameRegistry.registry.getUnjoinedUsers():
            GameRegistry.registry.getClient(p).sendUntagged("gameremoved", game.getName())



class ProtocolGameListener:
   __implements__ = (IGameListener,)
   
   def __init__(self, username):
      self._username = username
   
   def announceHistory(self, history):
      GameRegistry.registry.getClient(self._username).sendHistory()

   def announcePawnInfo(self):
      GameRegistry.registry.getClient(self._username).sendPawnInfo()

   def announceTurnNum(self, num):
      GameRegistry.registry.getClient(self._username).sendUntagged("turnnum", repr(num))

   def announceTurn(self, pawn):
      GameRegistry.registry.getClient(self._username).sendUntagged("turn", pawn.getName())

   def gameOverEvade(self, winningTeam):
      client = GameRegistry.registry.getClient(self._username)
      client_state = "endgame"
      client.sendUntagged("gameover", winningTeam.getName(), 
            client.trans.ugettext("Mr. X successfully evaded the detectives for 24 turns.  Mr. X wins!").encode("utf-8"))

   def gameOverStuck(self, winningTeam):
      client = GameRegistry.registry.getClient(self._username)
      client_state = "endgame"
      client.sendUntagged("gameover", winningTeam.getName(), 
            client.trans.ugettext("None of the detectives are able to move.  Mr. X wins!").encode("utf-8"))

   def gameOverCaught(self, winningTeam, detective):
      client = GameRegistry.registry.getClient(self._username)
      client_state = "endgame"
      client.sendUntagged("gameover", winningTeam.getName(), 
         (client.trans.ugettext("Mr. X was caught by the %(color)s Detective at location %(number)d.  The detectives win!") % \
         {"color" : detective.getTranslatedName(client.trans), "number" : detective.getLocation()}).encode("utf-8"))

   def gameStart(self, game):
      GameRegistry.registry.getClient(self._username)._state = "playing"
      GameRegistry.registry.getClient(self._username).sendUntagged("gamestart")
   
   def pawnMove(self, game, pawn, *moves):
      if len(moves) == 1:
         (dest, transport) = moves[0]
         GameRegistry.registry.getClient(self._username).sendUntagged("move", 
               pawn.getName(), repr(dest), transport)
      elif len(moves) == 2:
         (dest1, transport1) = moves[0]
         (dest2, transport2) = moves[1]
         GameRegistry.registry.getClient(self._username).sendUntagged(
            "doublemove",
            pawn.getName(),
            repr(dest1), 
            transport1,
            repr(dest2),
            transport2)
      else:
         raise ServerError(self.trans.ugettext("Invalid number of moves."))
   
   def pawnStuck(self, pawn):
      GameRegistry.registry.getClient(self._username).sendUntagged("stuck", pawn.getName())

   def pawnSetTicketAmount(self, game, pawn, ticket, amount):
      raise NotImplementedError()
   
   def playerJoin(self, game, player):
      GameRegistry.registry.getClient(self._username).sendPlayerInfo(player)
   
   def playerJoinTeam(self, game, player, team):
      GameRegistry.registry.getClient(self._username).sendPlayerInfo(player)
   
   def playerLeave(self, game, player):
      GameRegistry.registry.getClient(self._username).sendPlayerLeave(player)
   
   def playerLeaveTeam(self, game, player, team):
      GameRegistry.registry.getClient(self._username).sendPlayerInfo(player)
   
   def playerModified(self, player):
      GameRegistry.registry.getClient(self._username).sendPlayerInfo(player)

   def playerRejoin(self, player):
      GameRegistry.registry.getClient(self._username).sendUntagged("rejoin", player.encode("utf-8"))

   def playerVoteStart(self, game, player, vote):
      GameRegistry.registry.getClient(self._username).sendPlayerInfo(player)





