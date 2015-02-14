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



# utility.py
#
# various utility functions that don't fit well elsewhere


# determine whether two rectangles overlap
def collideRect((x1, y1, w1, h1), (x2, y2, w2, h2)):
   if ((x1+w1-1) < x2 or x1 > (x2+w2-1) or
         (y1+h1-1) < y2 or y1 > (y2+h2-1)):
      return 0
   else:
      return 1


def collidePoint((x1, y1), (x2, y2, w2, h2)):
   if (x1 < x2 or x1 > (x2+w2-1) or 
         y1 < y2 or y1 > (y2+h2-1)):
      return 0
   else:
      return 1


# arch-tag: DO_NOT_CHANGE_f97b07aa-f6c2-41bc-a3a7-8a6fbcb5c49d  
