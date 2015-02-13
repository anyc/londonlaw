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



import random, sets
from twisted.internet import protocol
from twisted.python import log
from londonlaw.aiclients import base
from londonlaw.common import path


class DetectiveSimpleAIProtocolError(Exception):
   pass



# A very simple but complete AI client for the detectives.
class DetectiveSimpleAIProtocol(base.BaseAIProtocol):

   def doTurn(self, pawnName):

      pawn = self._pawns[pawnName]

      def cost(ticket_amounts, ticket):
         if ticket == 'taxi':
            if ticket_amounts['taxi'] > 2:
               return 1
            else:
               return 2
         elif ticket == 'bus':
            if ticket_amounts['bus'] > 2:
               return 1.2
            else:
               return 2
         elif ticket == 'underground':
            if ticket_amounts['underground'] > 1:
               return 3
            else:
               return 5
         elif ticket == 'black':
            return 1000000

      all_paths = path.cheapest_path(pawn.getLocation(), tickets=pawn._tickets,
                                      cost=cost)
      detective_locs = [self._pawns[p].getLocation() for p in self._pawns if p != 'X']

      if self._turnNum < 3:
         # Before X has surfaced, just try to get to high-mobility locations.
         # Compute locations we can get to by the end of turn 2, with the constraint
         # that we don't spend any undergrounds
         t = pawn._tickets.copy()
         t['underground'] = 0
         e = [sets.Set()] * (3 - self._turnNum)
         e[0].union_update(detective_locs)
         locs = list(path.possible_destinations(pawn.getLocation(), 3 - self._turnNum, 
               tickets=t, eliminate=e))
         random.shuffle(locs)
         # evaluate the mobility of each location
         bestLoc      = None
         bestMobility = 0
         for loc in locs:
            # how well-connected is this location?
            mobility = len(path.possible_destinations(loc, 1, pawn._tickets))
            if mobility > bestMobility:
               bestLoc      = loc
               bestMobility = mobility
         if bestLoc != None and all_paths[bestLoc] != None:
            self.makeMove([pawnName.lower(), str(all_paths[bestLoc][0][0]), all_paths[bestLoc][0][1]])
         else:
            # shouldn't happen
            raise DetectiveSimpleAIProtocolError("failed to find a move for turnNum < 3")
      else:
         # after X has surfaced, just try to go somewhere where he *might* be (use game
         # history to eliminate detective positions as possible locations)
         lastXLoc = self._history[self._lastXSurfacingTurn]['X'][0]
         xTransports = []
         e           = []
         for i in range(self._lastXSurfacingTurn + 1, self._turnNum + 1):
            xTransports.append(self._history[i]['X'][1])
            detPos = []
            for p in self._pawns:
               if p != 'X' and p in self._history[i-1].keys():
                  detPos.append(self._history[i-1][p][0])
            e.append(sets.Set(detPos))
         log.msg('x transports = ' + str(xTransports))
         xLocs = path.possible_locations(lastXLoc, xTransports, eliminate=e)
         log.msg('x possible locations = ' + str(xLocs))

         # determine which of these locations is closest with a path that is
         # attainable
         minDist = 1000000
         bestLoc = None
         for loc in xLocs:
            if (all_paths[loc] != None and len(all_paths[loc]) < minDist and
                  len(all_paths[loc]) > 0 and all_paths[loc][0][0] not in detective_locs):
               bestLoc = loc

         if bestLoc != None and all_paths[bestLoc] != None:
            self.makeMove([pawnName.lower(), str(all_paths[bestLoc][0][0]), all_paths[bestLoc][0][1]])
         else:
            # if we can't find anything good, make a random move
            log.msg("moving randomly")
            availableMoves = list(path.possible_destinations(pawn.getLocation(), 1,
               tickets=pawn._tickets, eliminate = [sets.Set(detective_locs)]))
            move = random.choice(availableMoves)
            self.makeMove([pawnName.lower(), str(all_paths[move][0][0]), all_paths[move][0][1]])



   def response_ok_tryjoin(self, tag, args):
      self._state = "trychat"
      self.sendChat("Loaded \"Simple Detective AI\", Copyright 2005 Paul Pelzl.", "all")


   def response_ok_trychat(self, tag, args):
      base.BaseAIProtocol.response_ok_tryjoin(self, tag, args)

      


class DetectiveSimpleAIFactory(base.BaseAIFactory):
   protocol = DetectiveSimpleAIProtocol

   def __init__(self, username, gameroom):
      base.BaseAIFactory.__init__(self, username, username, gameroom, "Detectives")




