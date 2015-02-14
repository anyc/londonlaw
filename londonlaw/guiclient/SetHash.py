#  London Law -- a networked manhunting board game
#  Copyright (C) 2003-2004 Paul Pelzl
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


from sets import *


# create a hash table that does not overwrite values, but rather appends them
# to a set
class SetHash:
   def __init__(self):
      self.dict = {}

   def add(self, key, value):
      try:
         self.dict[key] |= Set([value])
      except KeyError:
         self.dict[key] = Set([value])

   def get(self, key):
      return self.dict[key]

   # delete(key) removes entire list of values
   # delete(key, value) removes the particular value from the list
   def delete(self, key, value=None):
      if value:
         self.dict[key] -= Set([value])
         if len(self.dict[key]) == 0:
            del self.dict[key]
      else:
         del self.dict[key]

   def clear(self):
      self.dict = {}

   def getDict(self):
      return self.dict




# arch-tag: DO_NOT_CHANGE_f7a6402c-f781-4e96-9b78-62804caef364  
