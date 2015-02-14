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




# StaticBitmap.py
#
# This class is an attempt at a more robust cross-platform version of a
# wxStaticBitmap.

from wxPython.wx import *

class StaticBitmap(wxWindow):
   def __init__(self, parent, id, bitmap, position = wxDefaultPosition, size = wxDefaultSize):
      wxWindow.__init__(self, parent, id, position, size)
      self.bitmap = bitmap
      self.SetSize(wxSize(self.bitmap.GetWidth(), self.bitmap.GetHeight()))

      EVT_PAINT(self, self.OnPaint)


   def OnPaint(self, event):
      self.srcDC  = wxMemoryDC()
      self.srcDC.SelectObject(self.bitmap)
      destDC = wxPaintDC(self)
      destDC.BeginDrawing()
      destDC.Blit(0, 0, self.bitmap.GetWidth(), self.bitmap.GetHeight(), self.srcDC, 0, 0)
      destDC.EndDrawing()
      self.srcDC.SelectObject(wxNullBitmap)


   def GetBitmap(self):
      return self.bitmap


   def SetBitmap(self, bitmap):
      self.bitmap = bitmap


   def DoGetBestSize(self):
      print "called DoGetBestSize()"
      return wxSize(self.bitmap.GetWidth(), self.bitmap.GetHeight())
   
#   def GetBestSize(self):
#      print "called GetBestSize()"
#      return wxSize(self.bitmap.GetWidth(), self.bitmap.GetHeight())


# arch-tag: DO_NOT_CHANGE_a21ebe5e-e749-45fb-81fb-fa430d46cf0e 
