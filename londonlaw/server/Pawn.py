#  London Law -- a networked manhunting board game
#  Copyright (C) 2005 Conor Davis
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


class PawnError(Exception):
   pass


class Pawn(object):
   def __init__(self, name):
      self._loc = None
      self._name = name
      self._player = None
      self._tickets = {}
   
   def getLocation(self):
      return self._loc
   
   def getName(self):
      return self._name
   
   def getPlayer(self):
      return self._player
   
   def getTicketAmount(self, ticket):
      return self._tickets.get(ticket, 0)
      
   def hasTicket(self, ticket):
      return self._tickets.get(ticket, 0) != 0
   
   def removeTicket(self, ticket):
      amount = self._tickets.get(ticket, 0)
      if amount == 0:
         raise PawnError("tried to remove non-existant ticket " + str(ticket))
      if amount != -1:
         # amount -1 implies infinite tickets
         self._tickets[ticket] = amount - 1
   
   def setLocation(self, loc):
      self._loc = loc
   
   def setPlayer(self, player):
      self._player = player
   
   def setTicketAmount(self, ticket, amount):
      self._tickets[ticket] = amount

# arch-tag: 90f1d631-c439-4e68-8d8d-d7bd62f6f7d5
