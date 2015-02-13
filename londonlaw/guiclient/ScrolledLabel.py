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




# ScrolledLabel.py
#
# This class handles a wx.StaticText that is managed by a scrolled window.


import wx

class ScrolledLabel(wx.ScrolledWindow):
   def __init__(self, parent, label):
      wx.ScrolledWindow.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, 
         wx.VSCROLL | wx.SIMPLE_BORDER)
      self.SetBackgroundColour(wx.Colour(200, 200, 200))
      self.SetScrollRate(0, 5)

      # create the text that will be scrolled
      self.text = wx.StaticText(self, -1, label, wx.Point(0,0))

      # use a Sizer to handle geometry
      self.topSizer = wx.BoxSizer(wx.VERTICAL)
      self.topSizer.Add(self.text, 1, wx.EXPAND)
      self.SetSizer(self.topSizer)
      self.topSizer.FitInside(self)

      self.ScrollToEnd()

   def SetText(self, text):
      self.text.SetLabel(text)

      # force the sizer to readjust to the new text, so the scroll bars
      # will properly cover the entire region
      txtsize = self.text.GetSize()
      self.topSizer.SetMinSize(txtsize)
      self.ScrollToEnd()

   def AppendText(self, txt):
      self.text.SetLabel(self.text.GetLabel() + '\n' + txt)

      txtsize = self.text.GetSize()
      self.topSizer.SetMinSize(txtsize)
      self.ScrollToEnd()



   # scroll to the bottom of the text
   def ScrollToEnd(self):
      self.topSizer.FitInside(self)
      self.Scroll(0, self.GetVirtualSize()[1]/5)


