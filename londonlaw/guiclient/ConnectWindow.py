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




# ConnectWindow.py
#
# This class handles the initial connection window, where players
# enter server information and provide usernames.

import sys, gettext, wx
from londonlaw.common.protocol import *


# Initial window.  Creates a form for the user to enter a host, port, and user information.
class ConnectWindow(wx.Frame):
   def __init__(self, parent, ID, title, exitCallback):
      wx.Frame.__init__(self, parent, ID, title)

      EXIT = 100

      self.exitCallback = exitCallback

      # Create a menu bar
      # TRANSLATORS: this is a menu bar entry
      fileMenu = wx.Menu(_("File"))
      # TRANSLATORS: this is a menu bar entry
      fileMenu.Append(EXIT, _("Exit%(hotkey)s") % {"hotkey" : "\tCTRL+Q"}, "Exit London Law")
      menuBar = wx.MenuBar()
      # TRANSLATORS: this is a menu bar entry
      menuBar.Append(fileMenu, _("File"))
      self.SetMenuBar(menuBar)

      # Create a status bar
      self.status = self.CreateStatusBar()

      # stick everything in a panel to enable tab traversal
      mainPanel = wx.Panel(self, -1)

      labelFont = wx.Font(self.GetFont().GetPointSize(), wx.DEFAULT, wx.NORMAL, wx.BOLD)
      labelFont.SetWeight(wx.BOLD)
      # TRANSLATORS: labels for server connection dialog
      connectLabel = wx.StaticText(mainPanel, -1, _("Connect to: "))
      connectLabel.SetFont(labelFont)
      # TRANSLATORS: labels for server connection dialog
      self.hostEntryLabel = wx.StaticText(mainPanel, -1, _("host:"), wx.Point(0,0))
      self.hostEntry      = wx.TextCtrl(mainPanel, -1, "localhost", wx.DefaultPosition, (170, wx.DefaultSize[1]))
      # TRANSLATORS: labels for server connection dialog
      self.portEntryLabel = wx.StaticText(mainPanel, -1, _("port:"), wx.Point(0,0))
      self.portEntry      = wx.TextCtrl(mainPanel, -1, str(LLAW_PORT), wx.DefaultPosition, (50, wx.DefaultSize[1]))
      self.portEntry.SetMaxLength(5)

      connectSizer = wx.BoxSizer(wx.HORIZONTAL)
      connectSizer.Add((30,1),0,0)
      connectSizer.Add(self.hostEntryLabel, 0, wx.ALIGN_CENTRE | wx.LEFT, 5)
      connectSizer.Add(self.hostEntry, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
      connectSizer.Add((10,1),0,0)
      connectSizer.Add(self.portEntryLabel, 0, wx.ALIGN_CENTRE)
      connectSizer.Add(self.portEntry, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

      # TRANSLATORS: labels for server connection dialog
      userLabel = wx.StaticText(mainPanel, -1, _("User information: "))
      userLabel.SetFont(labelFont)
      self.usernameEntryLabel = wx.StaticText(mainPanel, -1, _("username:"), wx.Point(0,0))
      self.usernameEntry = wx.TextCtrl(mainPanel, -1)
      self.usernameEntry.SetMaxLength(20)
      self.passEntryLabel = wx.StaticText(mainPanel, -1, _("password:"), wx.Point(0,0))
      self.passEntry = wx.TextCtrl(mainPanel, -1, style=wx.TE_PASSWORD)
      self.passEntry.SetMaxLength(20)

      userSizer = wx.BoxSizer(wx.HORIZONTAL)
      userSizer.Add((30,1),0,0)
      userSizer.Add(self.usernameEntryLabel, 0, wx.ALIGN_CENTRE)
      userSizer.Add(self.usernameEntry, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
      userSizer.Add((10,1),1,1)
      userSizer.Add(self.passEntryLabel, 0, wx.ALIGN_CENTRE)
      userSizer.Add(self.passEntry, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

      # Add some buttons
      # TRANSLATORS: labels for server connection dialog buttons
      self.connectButton = wx.Button(mainPanel, -1, _("Connect"))
      self.quitButton    = wx.Button(mainPanel, -1, _("Quit"))
      buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
      buttonSizer.Add(self.quitButton, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
      if sys.platform.lower()[:-3] == "win":
         # Win32 users like their buttons in the wrong order
         buttonSizer.Prepend(self.connectButton, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
      else:
         buttonSizer.Add(self.connectButton, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
      buttonSizer.Prepend((10,1),1,wx.EXPAND)

      self.topSizer = wx.BoxSizer(wx.VERTICAL)
      self.topSizer.Add(connectLabel, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP, 10)
      self.topSizer.Add(connectSizer, 0, wx.ALIGN_LEFT | wx.ALL, 5)
      self.topSizer.Add(userLabel, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP, 10)
      self.topSizer.Add(userSizer, 0, wx.ALIGN_LEFT | wx.ALL, 5)
      self.topSizer.Add((10,10),1,wx.EXPAND)
      self.topSizer.Add(buttonSizer, 0, wx.EXPAND | wx.ALL, 5)
      mainPanel.SetSizer(self.topSizer)
      self.topSizer.Fit(self)
      mainPanel.SetAutoLayout(1)

      self.hostEntry.SetFocus()

      wx.EVT_SET_FOCUS(self.hostEntry, self.selectFocused)
      wx.EVT_SET_FOCUS(self.portEntry, self.selectFocused)
      wx.EVT_SET_FOCUS(self.usernameEntry, self.selectFocused)
      wx.EVT_SET_FOCUS(self.passEntry, self.selectFocused)
      wx.EVT_BUTTON(self, self.quitButton.GetId(), self.menuExit)
      wx.EVT_MENU(self, EXIT, self.menuExit)


   # select contents of a focused wx.TextCtrl
   def selectFocused(self, ev):
      self.hostEntry.SetSelection(0,0)
      self.portEntry.SetSelection(0,0)
      self.usernameEntry.SetSelection(0,0)
      self.passEntry.SetSelection(0,0)
      if (ev.GetId() == self.hostEntry.GetId() and 
            len(self.hostEntry.GetValue()) > 0):
         self.hostEntry.SetSelection(-1, -1)
      if (ev.GetId() == self.portEntry.GetId() and 
            len(self.portEntry.GetValue()) > 0):
         self.portEntry.SetSelection(-1, -1)
      if (ev.GetId() == self.usernameEntry.GetId() and 
            len(self.usernameEntry.GetValue()) > 0):
         self.usernameEntry.SetSelection(-1, -1)
      if (ev.GetId() == self.passEntry.GetId() and 
            len(self.passEntry.GetValue()) > 0):
         self.passEntry.SetSelection(-1, -1)
      # need to Skip() this event in order to get the cursor in the focused box
      ev.Skip()


   def showInfoAlert(self, info):
      self.PushStatusText("")
      alert = wx.MessageDialog(self, info,
      # TRANSLATORS: this is the title for a small alert window that pops up when the server reports an error
         _("Server Message"), wx.OK|wx.ICON_INFORMATION)
      alert.ShowModal()


   def menuExit(self, ev):
      self.exitCallback(self)


