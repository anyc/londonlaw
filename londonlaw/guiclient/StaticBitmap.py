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




# StaticBitmap.py
#
# This class is an attempt at a more robust cross-platform version of a
# wx.StaticBitmap.

import wx

class StaticBitmap(wx.Window):
   def __init__(self, parent, id, bitmap, position = wx.DefaultPosition, size = wx.DefaultSize):
      wx.Window.__init__(self, parent, id, position, size)
      self.bitmap = bitmap
      self.SetSize(wx.Size(self.bitmap.GetWidth(), self.bitmap.GetHeight()))

      wx.EVT_PAINT(self, self.OnPaint)
      wx.EVT_LEFT_DCLICK(self, self.propagateDClick)


   def propagateDClick(self, ev):
      # propagate double-click as if it were a wx.CommandEvent
      ev.ResumePropagation(wx.EVENT_PROPAGATE_MAX)
      ev.Skip()


   def OnPaint(self, event):
      self.srcDC  = wx.MemoryDC()
      self.srcDC.SelectObject(self.bitmap)
      destDC = wx.PaintDC(self)
      destDC.BeginDrawing()
      destDC.Blit(0, 0, self.bitmap.GetWidth(), self.bitmap.GetHeight(), self.srcDC, 0, 0)
      destDC.EndDrawing()
      self.srcDC.SelectObject(wx.NullBitmap)


   def GetBitmap(self):
      return self.bitmap


   def SetBitmap(self, bitmap):
      self.bitmap = bitmap


   def DoGetBestSize(self):
      print "called DoGetBestSize()"
      return wx.Size(self.bitmap.GetWidth(), self.bitmap.GetHeight())
   
#   def GetBestSize(self):
#      print "called GetBestSize()"
#      return wx.Size(self.bitmap.GetWidth(), self.bitmap.GetHeight())


# arch-tag: DO_NOT_CHANGE_a21ebe5e-e749-45fb-81fb-fa430d46cf0e 
