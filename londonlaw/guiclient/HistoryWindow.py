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


# HistoryWindow.py
#
# This class handles Mr. X's history.  It displays ticket graphics
# and location numbers (when appropriate) in a vertical stack, and
# has a scroll bar to control the view.


import os, sys, string, gettext, wx
from TextPanel import *
from londonlaw.common.config import *

class HistoryWindow(wx.ScrolledWindow):
   def __init__(self, parent):
      wx.ScrolledWindow.__init__(self, parent)

      # load in the ticket images
      self.ticketImages = []
      for i in range(5):
         filename = os.path.normpath(os.path.join(MEDIAROOT, "images/ticket" + str(i) + ".png"))
         self.ticketImages.append(wx.Image(filename, wx.BITMAP_TYPE_ANY))

      # the toplevel sizer is this two-column FlexGridSizer;
      # the left column is filled with vertical wx.BoxSizers,
      # each of which places the turn number above Mr. X's
      # known locations.
      self.ticketSizer = wx.FlexGridSizer(24, 2, 0, 0)

      self.vbSizers     = []
      self.turns        = []
      self.locations    = []
      self.tickets      = []
      # left column
      self.panels       = []
      self.panelSizers  = []
      # right column
      self.panels2      = []
      self.panelSizers2 = []
      for i in range(24):
         self.panels.append(wx.Panel(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER))
         # TRANSLATORS: this is for the turn number labels in the history window
         self.turns.append(TextPanel(self.panels[i], _(" Turn %(num)d ") % {"num" : i+1},
            12, 0))
         self.locations.append(TextPanel(self.panels[i], " ", 16, 0))

         self.vbSizers.append(wx.BoxSizer(wx.VERTICAL))
         self.vbSizers[i].Add(self.turns[i], 1, wx.EXPAND|wx.CENTRE|wx.ADJUST_MINSIZE)
         self.vbSizers[i].Add(self.locations[i], 1, wx.EXPAND|wx.CENTRE|wx.ADJUST_MINSIZE)

         self.panelSizers.append(wx.BoxSizer(wx.HORIZONTAL))
         self.panelSizers[i].Add(self.vbSizers[i], 1, wx.EXPAND)
         self.panels[i].SetSizerAndFit(self.panelSizers[i])

         self.panels2.append(wx.Panel(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER))
         self.tickets.append(wx.StaticBitmap(self.panels2[i], -1, wx.BitmapFromImage(self.ticketImages[4])))

         self.panelSizers2.append(wx.BoxSizer(wx.HORIZONTAL))
         self.panelSizers2[i].Add(self.tickets[i], 1, wx.EXPAND)
         self.panels2[i].SetSizerAndFit(self.panelSizers2[i])

         self.ticketSizer.Add(self.panels[i], 0, wx.EXPAND|wx.CENTRE|wx.LEFT|wx.TOP, 5)
         self.ticketSizer.Add(self.panels2[i], 0, wx.EXPAND|wx.CENTRE|wx.LEFT|wx.TOP|wx.RIGHT, 5)

      self.showSurfacingTurns()

      self.SetSizer(self.ticketSizer)

# FIXME: the scrollbar-related sizing glitch has been corrected in wxGTK 2.6... 
#        need to test on other platforms
#      # workaround for incorrect scrolledwindow sizing
#      pform = string.lower(sys.platform)
#      if pform.startswith("win") or pform.startswith("darwin"):
#      (w, h) = self.ticketSizer.GetMinSize()
#      self.ticketSizer.SetMinSize(wx.Size(w+15, h))

      self.ticketSizer.Fit(self)
      self.SetScrollRate(0, 10)

      # The following doesn't seem to work in wx.GTK...
      # self.SetSizerAndFit(self.ticketSizer)


   # update one of the location numbers
   def setLocation(self, turnNum, locStr):
      self.vbSizers[turnNum].Remove(self.locations[turnNum])
      self.locations[turnNum].Destroy()
      if turnNum in (2, 7, 12, 17, 23):
         fontWeight = wx.BOLD
      else:
         fontWeight = wx.NORMAL
      self.locations[turnNum] = TextPanel(self.panels[turnNum], " " + locStr + " ",
         16, 0, fontWeight)
      self.vbSizers[turnNum].Add(self.locations[turnNum], 1, wx.EXPAND|wx.CENTRE)

      self.panelSizers[turnNum].Layout()


   # update one of the ticket graphics 
   def setTicket(self, turnNum, tickNum):
      self.tickets[turnNum].SetBitmap(wx.BitmapFromImage(self.ticketImages[tickNum]))
      self.tickets[turnNum].Refresh(False)


   # draw question marks for the location entries where Mr. X will
   # be surfacing
   def showSurfacingTurns(self):
      for i in (2, 7, 12, 17, 23):
         # TRANSLATORS: this is the symbol shown in the history bar to indicate turns where X will surface
         self.setLocation(i, _(" ? "))




