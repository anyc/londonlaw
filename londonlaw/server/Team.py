import sets

class TeamError(Exception):
   pass


class Team(object):
   def __init__(self, name):
      self._name        = name
      self._players     = []
      self._pawns       = []
      self._pawn2player = {}
   
   def addPawn(self, pawn):
      self._pawns.append(pawn)
   
   def addPlayer(self, player):
      if self.getNumPlayers() >= self.getNumPawns():
         raise TeamError("That team is full.")
      self._players.append(player)
      self._reassignPawns()

   def getMaxPlayers(self):
      return self.getNumPawns()
   
   def getName(self):
      return self._name
   
   def getNumPawns(self):
      return len(self._pawns)
   
   def getNumPlayers(self):
      return len(self._players)

   def getPawns(self):
      return self._pawns
   
   def getPawnsForPlayer(self, player):
      return [pawn for pawn in self._pawns if self._pawn2player[pawn] == player]
   
   def getPlayerForPawn(self, pawn):
      return self._pawn2player.get(pawn, None)
   
   def getPlayers(self):
      return self._players
   
   def isFull(self):
      return self.getNumPlayers() == self.getMaxPlayers()
   
   def removePlayer(self, player):
      try:
         self._players.remove(player)
      except KeyError:
         raise TeamError("player not in team")
      self._reassignPawns()

   def _assignPawnToPlayer(self, pawn, player):
      self._pawn2player[pawn] = player
      pawn.setPlayer(player)
   
   def _reassignPawns(self):
      self._unassignPawns()
      if self.getNumPlayers() == 0:
         return
      (minPawns, extra) = divmod(self.getNumPawns(), self.getNumPlayers())
      pawnIterator = iter(self._pawns)
      for player in self._players:
         if extra > 0:
            pawnsForPlayer = minPawns + 1
            extra -= 1
         else:
            pawnsForPlayer = minPawns
         for _ in xrange(pawnsForPlayer):
            self._assignPawnToPlayer(pawnIterator.next(), player)
         
   def _unassignPawns(self):
      self._pawn2player.clear()

# arch-tag: 04c72878-6f44-4cb4-b64f-8ba5779aad58
