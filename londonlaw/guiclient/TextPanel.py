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




# TextPanel.py
#
# This class handles a wx.StaticText drawn on a wx.Panel.  The combination
# allows one to set both foreground and background colors, as well as
# borders around the window.

import wx

# Generate a text label drawn on a wx.Panel.
class TextPanel(wx.Panel):
   def __init__(self, parent, text, points = 10, style = 0, fontWeight = wx.NORMAL):
      wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, style)

      font = wx.Font(points, wx.DEFAULT, wx.NORMAL, fontWeight)
      self.text = wx.StaticText(self, -1, text, wx.Point(0,0))
      self.text.SetFont(font)

      self.sizer = wx.BoxSizer(wx.VERTICAL)
      self.sizer.Add((0, 0), 1, wx.EXPAND)
      self.sizer.Add(self.text, 0, wx.ALIGN_CENTRE|wx.ADJUST_MINSIZE)
      self.sizer.Add((0, 0), 1, wx.EXPAND)
      self.SetSizer(self.sizer)
      self.sizer.SetSizeHints(self)

   def SetText(self, text):
      self.text.SetLabel(text)
      txtsize = self.text.GetSize()
      self.sizer.SetMinSize(txtsize)

   def SetForegroundColour(self, color):
      self.text.SetForegroundColour(color)
      wx.Panel.SetForegroundColour(self, color)

   # def SetBackgroundColour(self, color)
   # (this function falls through to call SetBackgroundColour on the wx.Panel)
   def SetBackgroundColour(self, color):
      self.text.SetBackgroundColour(color)
      wx.Panel.SetBackgroundColour(self, color)
   


