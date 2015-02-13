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


import gettext


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
      
   # The pawn name strings are used for server communication, etc., so
   # they need to be well-defined constants.  But we need translations
   # when popping up messages for the user.
   def getTranslatedName(self, trans):
      if self._name == "Red":
         return trans.ugettext("Red")
      elif self._name == "Yellow":
         return trans.ugettext("Yellow")
      elif self._name == "Green":
         return trans.ugettext("Green")
      elif self._name == "Blue":
         return trans.ugettext("Blue")
      elif self._name == "Black":
         return trans.ugettext("Black")
      else:
         return u"X"

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

