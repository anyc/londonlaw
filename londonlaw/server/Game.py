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


import re, random
import sets

from twisted.python import components
from twisted.python import log

from londonlaw.common.protocol import *
from londonlaw.common.map import *
from Pawn import *
from Team import *
import Protocol, GameRegistry


class GameError(Exception):
   pass


class IGameListener(components.Interface):
   def announceHistory(self, history):
      pass

   def announceTurnNum(self, num):
      pass

   def announceTurn(self, pawn):
      pass

   def announcePawnInfo(self):
      pass

   def gameOver(self, game, winningTeam, reason):
      pass

   def gameStart(self, game):
      pass
   
   def pawnMove(self, game, pawn, *moves):
      pass

   def pawnStuck(self, pawn):
      pass
   
   def pawnSetTicketAmount(self, game, pawn, ticket, amount):
      pass

   def playerJoin(self, game, player):
      """Called when a player has joined the game."""

   def playerJoinTeam(self, game, player, team):
      """Called when a player joins a team."""
   
   def playerLeave(self, game, player):
      """Called when a player has left the game."""
   
   def playerLeaveTeam(self, game, player, team):
      """Called when a player leaves a team."""

   def playerModified(self, player):
      """Called when a player's status changes for an unspecified reason"""

   def playerRejoin(self, player):
      """Called when a player rejoins an in-progress game."""
   
   def playerVoteStart(self, game, player, vote):
      """Called when a player votes to start the game."""


registry = GameRegistry.getHandle()

# Vocabulary: a 'player' is a username.  registry.getClient(player) is the
#             Protocol instance associated with that username, if one exists.
class Game:

   # start a new game with specified name, of desired type
   def __init__(self, name, gameType):
      self._gameStatus  = GAMESTATUS_NEW
      self._maxPlayers  = 0
      self._pawns       = []
      self._pawn2team   = {}
      self._players     = []
      self._player2team = {}
      self._teams       = []
      self._authList    = []
      self._listeners   = {}
      self._nextPawn    = {}
      self._turnNum     = 1
      
      x_team = Team("Mr. X")
      det_team = Team("Detectives")
      self._addTeam(x_team)
      self._addTeam(det_team)
      
      x_pawn      = Pawn("X")
      red_pawn    = Pawn("Red")
      yellow_pawn = Pawn("Yellow")
      green_pawn  = Pawn("Green")
      blue_pawn   = Pawn("Blue")
      black_pawn  = Pawn("Black")

      self._addPawn(x_pawn, x_team)
      self._addPawn(red_pawn, det_team)
      self._addPawn(yellow_pawn, det_team)
      self._addPawn(green_pawn, det_team)
      self._addPawn(blue_pawn, det_team)
      self._addPawn(black_pawn, det_team)

      # Starting positions for the players (they can't overlap)
      initial_location_pop = [13, 26, 29, 34, 50, 53, 91, 103, 112, 
                              117, 132, 138, 141, 155, 174, 197, 198]
      initial_locations = random.sample(initial_location_pop, 6)

      x_pawn.setTicketAmount("taxi", -1)
      x_pawn.setTicketAmount("bus", -1)
      x_pawn.setTicketAmount("underground", -1)
      x_pawn.setTicketAmount("black", 5)
      x_pawn.setTicketAmount("double", 2)
      x_pawn.setLocation(initial_locations[0])
      self._history = [[("X", repr(x_pawn.getLocation()))]]

      curr_pawn = 1
      for pawn in det_team.getPawns():
         pawn.setTicketAmount("taxi", 10)
         pawn.setTicketAmount("bus", 8)
         pawn.setTicketAmount("underground", 4)
         pawn.setLocation(initial_locations[curr_pawn])
         self._history[0].append((pawn.getName(), repr(pawn.getLocation())))
         curr_pawn += 1

      self._history.append([])

      self._nextPawn[x_pawn]      = red_pawn
      self._nextPawn[red_pawn]    = yellow_pawn
      self._nextPawn[yellow_pawn] = green_pawn
      self._nextPawn[green_pawn]  = blue_pawn
      self._nextPawn[blue_pawn]   = black_pawn
      self._nextPawn[black_pawn]  = x_pawn
      self._currentPawn           = x_pawn

      for team in self._teams:
         self._maxPlayers += team.getMaxPlayers()
      
      gameNameRegex = re.compile(r"^[^\n\t\"]+$")
      if len(name) > 40:
         raise GameError("game name too long")

      # test the game name to make sure it is legal
      if not gameNameRegex.match(name.strip()):
         raise GameError("illegal format for game name")

      self._gameName = name.strip()

      if gameType in [GAMETYPE_STANDARD]:
         self._gameType = gameType
      else:
         raise GameError("unrecognized game type")

   def addListenerForPlayer(self, player):
      self._listeners[Protocol.ProtocolGameListener(player)] = player
   
   # add a new player to this game
   def addPlayer(self, player):
      if self._gameStatus == GAMESTATUS_INPROGRESS:
         if player in self._players:
            registry.getClient(player).setGame(self)
            registry.getClient(player).setVote(True)
            for listener in self._listeners:
               listener.playerRejoin(player)
            self.addListenerForPlayer(player)
         else:
            raise GameError("Username not permitted for this in-progress game.")
      elif self._gameStatus == GAMESTATUS_COMPLETE:
         raise GameError("That game has already been completed.")
      # this must GAMESTATUS_NEW
      elif self._gameType == GAMETYPE_STANDARD:
         team = self._findAvailableTeam()
         if team is None:
            raise GameError("That game is full.")
         self._players.append(player)
         registry.getClient(player).setGame(self)
         self._setTeamForPlayer(player, team)
         self.addListenerForPlayer(player)
   
   def gameOver(self, winningTeam, reason):
      self._gameStatus = GAMESTATUS_COMPLETE
      for listener in self._listeners:
         listener.gameOver(winningTeam, reason)

   def getCurrentPawn(self):
      return self._currentPawn

   def getHistory(self):
      return self._history

   def getListeners(self):
      return self._listeners

   def getMaxPlayers(self):
      return self._maxPlayers
   
   def getName(self):
      return self._gameName

   def getNumPlayers(self):
      return len(self._players)

   def getPawns(self):
      return self._pawns

   def getPawnsForPlayer(self, player):
      team = self._getTeamForPlayer(player)
      return team.getPawnsForPlayer(player)
   
   def getPlayerForPawn(self, pawn):
      team = self._getTeamForPawn(pawn)
      return team.getPlayerForPawn(pawn)
   
   def getPlayers(self):
      return self._players

   def getStatus(self):
      return self._gameStatus

   def getTeam(self, player):
      return self._getTeamForPlayer(player)

   def getTurnNum(self):
      return self._turnNum
   
   def getType(self):
      return self._gameType

   def isDetectiveStuck(self, pawn):
      for route in locToRoutes[pawn.getLocation()]:
         for ticket in route[1]:
            if pawn.hasTicket(ticket):
               # ok, this route is available, but does it cause collisions?
               team = self._getTeamForPawn(pawn)
               teammateLocations = [p.getLocation() for p in team.getPawns() if p != pawn]
               if route[0] not in teammateLocations:
                  return False
      return True

   def isEveryDetectiveStuck(self):
      for pawn in self._getTeamByName("Detectives").getPawns():
         if not self.isDetectiveStuck(pawn):
            return False
      return True

   def isFull(self):
      return self.getNumPlayers() == self.getMaxPlayers()
   
   def isLegalMove(self, pawn, newLoc1, ticket1, newLoc2=None, ticket2=None):
      # test for detective collision
      team = self._getTeamForPawn(pawn)
      if team.getName() == "Detectives":
         teammateLocations = [p.getLocation() for p in team.getPawns() if p != pawn]
         if newLoc1 in teammateLocations or newLoc2 in teammateLocations:
            return False
      # test for map connectivity and ticket inventory
      return self.isLegalMoveAux(pawn, newLoc1, ticket1, newLoc2, ticket2)

   def isLegalMoveAux(self, pawn, newLoc1, ticket1, newLoc2=None, ticket2=None):
      routes = locToRoutes[pawn.getLocation()]
      for route in routes:
         if route[0] == newLoc1:
            if ((ticket1 in route[1] and pawn.hasTicket(ticket1)) or
                (ticket1 == BLACK and pawn.hasTicket(BLACK))):
               if newLoc2 is not None:
                  # temporarily change pawn's state to match the first move,
                  # so the second move can be tested
                  previousLocation = pawn.getLocation()
                  pawn.setLocation(newLoc1)
                  previousTicketNum = pawn.getTicketAmount(ticket1)
                  pawn.removeTicket(ticket1)
                  retVal = self.isLegalMoveAux(pawn, newLoc2, ticket2)
                  # restore pawn's original state
                  pawn.setLocation(previousLocation)
                  pawn.setTicketAmount(ticket1, previousTicketNum)
               else:
                  retVal = True
               return retVal
      return False

   def isSurfacingTurn(self):
      return (self._turnNum in (3, 8, 13, 18, 24))

   # not checked; validate with isLegalMove()
   def makeMove(self, pawn, newLoc1, ticket1, newLoc2=None, ticket2=None):
      pawn.setLocation(newLoc1)
      pawn.removeTicket(ticket1)
      self._history[self._turnNum].append((pawn.getName(), repr(newLoc1), ticket1))
      for listener in self._listeners:
         if pawn == self.getPawnByName("X") and not self.isSurfacingTurn() \
         and self._listeners[listener] != self.getPawnByName("X").getPlayer():
            reportedLoc1 = -1
         else:
            reportedLoc1 = newLoc1
         listener.pawnMove(self, pawn, (reportedLoc1, ticket1))
      if not self.testMrXCaught():
         if newLoc2 is not None:
            self._turnNum += 1
            self._history.append([])
            pawn.setLocation(newLoc2)
            pawn.removeTicket(ticket2)
            pawn.removeTicket("double")
            self._history[self._turnNum].append((pawn.getName(), repr(newLoc2), ticket2))
            for listener in self._listeners:
               listener.announceTurnNum(self._turnNum)
               if pawn == self.getPawnByName("X") and not self.isSurfacingTurn() \
               and self._listeners[listener] != self.getPawnByName("X").getPlayer():
                  reportedLoc2 = -1
               else:
                  reportedLoc2 = newLoc2
               listener.pawnMove(self, pawn, (reportedLoc2, ticket2))
            if not self.testMrXCaught():
               self._updateTurnInfo()
         else:
            self._updateTurnInfo()

   def removeListenerForPlayer(self, player):
      for listener in self._listeners:
         if self._listeners[listener] == player:
            del self._listeners[listener]
            break
   
   # remove a player from the game
   def removePlayer(self, player):
      if self._gameStatus == GAMESTATUS_NEW:
         team = self._player2team[player]
         team.removePlayer(player)
         del self._player2team[player]
         self._players.remove(player)
         self.removeListenerForPlayer(player)
         for listener in self._listeners:
            listener.playerLeave(self, player)
         # all players on this team will have some information changed, so push
         # a playerinfo update on each one
         self._sendTeamUpdate(team)
      elif self._gameStatus == GAMESTATUS_COMPLETE:
         self._players.remove(player)
         self.removeListenerForPlayer(player)
         for listener in self._listeners:
            listener.playerLeave(self, player)
      else:
         # for an in-progress game or a completed game, remove the listener only
         self.removeListenerForPlayer(player)
         for listener in self._listeners:
            listener.playerLeave(self, player)
      
   def setStatus(self, status):
      if status in (GAMESTATUS_NEW, GAMESTATUS_INPROGRESS, GAMESTATUS_COMPLETE):
         self._gameStatus = status
      else:
         raise GameError("unknown game status")

   def setTeam(self, player, teamName):
      team = self._getTeamByName(teamName)
      self._setTeamForPlayer(player, team)
      
   def syncPlayer(self, username):
      for listener in self._listeners:
         if self._listeners[listener] == username:
            listener.announcePawnInfo()
            listener.announceTurnNum(self._turnNum)
            listener.announceTurn(self._currentPawn)
            listener.announceHistory(self._history)
            break

   def testMrXCaught(self):
      X = self.getPawnByName("X")
      for detective in self._getTeamByName("Detectives").getPawns():
         if X.getLocation() == detective.getLocation():
            reason = "Mr. X was caught by the " + detective.getName() + \
                  " Detective at location " + repr(X.getLocation()) + \
                  ".  The detectives win!"
            self.gameOver(self._getTeamByName("Detectives"), reason)
            return True
      return False

   def testGameStart(self):
      if not (False in [t.getNumPlayers() > 0 for t in self._teams]) \
      and not (False in [registry.getClient(p).getVote() for p in self._players]):
         for listener in self._listeners:
            self._gameStatus = GAMESTATUS_INPROGRESS
            listener.gameStart(self)
            listener.announcePawnInfo()
            listener.announceTurnNum(self._turnNum)
            listener.announceTurn(self._currentPawn)

   def _addPawn(self, pawn, team):
      self._pawns.append(pawn)
      team.addPawn(pawn)
      self._pawn2team[pawn] = team
   
   def _addTeam(self, team):
      self._teams.append(team)

   def _findAvailableTeam(self):
      teams = [team for team in self._teams if not team.isFull()]
      if len(teams) == 0:
         return None
      def comparer(team1, team2):
         return cmp(team1.getNumPlayers(), team2.getNumPlayers())
      # all we really need to do is get the minimum element, but I don't
      # see a way to do that in the python 2.3 standard library
      teams.sort(comparer)
      return teams[0]
            
   def getPawnByName(self, name):
      for pawn in self._pawns:
         if pawn.getName() == name:
            return pawn
      raise GameError("no such pawn")
   
   def _getTeamByName(self, name):
      for team in self._teams:
         if team.getName() == name:
            return team
      raise GameError("no such team")
   
   def _getTeamForPawn(self, pawn):
      return self._pawn2team.get(pawn, None)
   
   def _getTeamForPlayer(self, player):
      return self._player2team.get(player, None)
   
   def _sendTeamUpdate(self, team):
      for p in team.getPlayers():
         for listener in self._listeners:
            listener.playerModified(p)
   
   def _setTeamForPlayer(self, player, team):
      oldTeam = self._player2team.get(player, None)
      if team == oldTeam:
         return
      if team is not None:
         team.addPlayer(player)
      # do this second, so an exception in addPlayer() won't break things
      if oldTeam is not None:
         oldTeam.removePlayer(player)
      self._player2team[player] = team
      if oldTeam is not None:
         self._sendTeamUpdate(oldTeam)
      if team is not None:
         self._sendTeamUpdate(team)

   def _updateTurnInfo(self):
      self._currentPawn = self._nextPawn[self._currentPawn]
      if self._currentPawn == self.getPawnByName("X"):
         self._turnNum += 1
         if self._turnNum >= 25:
            self.gameOver(self._getTeamByName("Mr. X"), 
               "Mr. X successfully evaded the detectives for 24 turns.  Mr. X wins!")
            return
         else:
            self._history.append([])
            for listener in self._listeners:
               listener.announceTurnNum(self._turnNum)
      else:
         if self._currentPawn == self.getPawnByName("Red"):
            if self.isEveryDetectiveStuck():
               self.gameOver(self._getTeamByName("Mr. X"),
                     "None of the detectives are able to move.  Mr. X wins!")
               return
         if self.isDetectiveStuck(self._currentPawn):
            for listener in self._listeners:
               listener.pawnStuck(self._currentPawn)
            self._updateTurnInfo()
            return
      for listener in self._listeners:
         listener.announceTurn(self._currentPawn)




# arch-tag: DO_NOT_CHANGE_956f65da-ac5e-4295-a9a1-629e25e4baa4 
