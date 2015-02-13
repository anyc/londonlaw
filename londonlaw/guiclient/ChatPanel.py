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




# ChatPanel.py
#
# This class creates a combined chat entry and chat message display area.

import gettext, wx
from ScrolledLabel import *


# Wrapped in a StaticBox.
class ChatPanel(wx.Panel):
   def __init__(self, parent, text, enableSendTo):
      wx.Panel.__init__(self, parent, -1)


      # create a scrollable display for the chat messages 
      self.chatDisplay = ScrolledLabel(self, text)

      # create the "send to" radio button
      # TRANSLATORS: this is for a set of radio buttons for chat messages--"send to" all players or "send to" team only
      self.chatRadio = wx.RadioBox(self, -1, _("send to:"), wx.DefaultPosition, wx.DefaultSize,
      # TRANSLATORS: this is for a set of radio buttons for chat messages--send to "all" players or send to "team" only
         [_("all"), 
      # TRANSLATORS: this is for a set of radio buttons for chat messages--send to "all" players or send to "team" only
         _("team")], 1, wx.RA_SPECIFY_COLS)
      self.chatRadio.Enable(enableSendTo)

      # create a chat entry box
      self.chatEntry = wx.TextCtrl(self, -1, "", wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER)
      self.chatEntry.SetMaxLength(254)  # messages longer than this would get truncated by ESocket.write_string()


      # set up the geometry.
      # line the chat display and the radio button horizontally...
      sizer2 = wx.BoxSizer(wx.HORIZONTAL)
      sizer2.Add(self.chatDisplay, 1, wx.EXPAND|wx.ALL, 5)
      sizer2.Add(self.chatRadio, 0, wx.ALIGN_BOTTOM|wx.ALL, 5) 

      # ... and line up the rest vertically
      self.topSizer = wx.BoxSizer(wx.VERTICAL)
      self.topSizer.Add(sizer2, 1, wx.EXPAND)
      self.topSizer.Add(self.chatEntry, 0, wx.EXPAND|wx.ALL, 5)
      self.SetSizer(self.topSizer)
      self.topSizer.SetSizeHints(self)


   def GetEntry(self):
      return (self.chatEntry.GetValue(), self.chatRadio.GetStringSelection())

   def ClearEntry(self):
      self.chatEntry.Clear()

   def SetText(self, txt):
      self.chatDisplay.SetText(txt)

   def AppendText(self, txt):
      self.chatDisplay.AppendText(txt)


