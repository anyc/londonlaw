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




# ConnectWindow.py
#
# This class handles the initial connection window, where players
# enter server information and provide usernames.

from wxPython.wx import *
from twisted.internet import reactor
from londonlaw.common.protocol import *
import sys


# Initial window.  Creates a form for the user to enter a host, port, and user information.
class ConnectWindow(wxFrame):
   def __init__(self, parent, ID, title):
      wxFrame.__init__(self, parent, ID, title)

      EXIT = 100

      # Create a menu bar
      fileMenu = wxMenu("File")
      fileMenu.Append(EXIT, "Exit\tCTRL+Q", "Exit London Law")
      menuBar = wxMenuBar()
      menuBar.Append(fileMenu, "File")
      self.SetMenuBar(menuBar)

      # Create a status bar
      self.status = self.CreateStatusBar()

      # stick everything in a panel to enable tab traversal
      mainPanel = wxPanel(self, -1)

      labelFont = wxFont(self.GetFont().GetPointSize(), wxDEFAULT, wxNORMAL, wxBOLD)
      labelFont.SetWeight(wxBOLD)
      connectLabel = wxStaticText(mainPanel, -1, "Connect to: ")
      connectLabel.SetFont(labelFont)
      self.hostEntryLabel = wxStaticText(mainPanel, -1, "host:", wxPoint(0,0))
      self.hostEntry      = wxTextCtrl(mainPanel, -1, "localhost", wxDefaultPosition, (170, wxDefaultSize[1]))
      self.portEntryLabel = wxStaticText(mainPanel, -1, "port:", wxPoint(0,0))
      self.portEntry      = wxTextCtrl(mainPanel, -1, str(LLAW_PORT), wxDefaultPosition, (50, wxDefaultSize[1]))
      self.portEntry.SetMaxLength(5)

      connectSizer = wxBoxSizer(wxHORIZONTAL)
      connectSizer.Add((30,1),0,0)
      connectSizer.Add(self.hostEntryLabel, 0, wxALIGN_CENTRE | wxLEFT, 5)
      connectSizer.Add(self.hostEntry, 0, wxALIGN_CENTRE | wxALL, 5)
      connectSizer.Add((10,1),0,0)
      connectSizer.Add(self.portEntryLabel, 0, wxALIGN_CENTRE)
      connectSizer.Add(self.portEntry, 0, wxALIGN_CENTRE | wxALL, 5)

      userLabel = wxStaticText(mainPanel, -1, "User information: ")
      userLabel.SetFont(labelFont)
      self.usernameEntryLabel = wxStaticText(mainPanel, -1, "username:", wxPoint(0,0))
      self.usernameEntry = wxTextCtrl(mainPanel, -1)
      self.usernameEntry.SetMaxLength(20)
      self.passEntryLabel = wxStaticText(mainPanel, -1, "password:", wxPoint(0,0))
      self.passEntry = wxTextCtrl(mainPanel, -1, style=wxTE_PASSWORD)
      self.passEntry.SetMaxLength(20)

      userSizer = wxBoxSizer(wxHORIZONTAL)
      userSizer.Add((30,1),0,0)
      userSizer.Add(self.usernameEntryLabel, 0, wxALIGN_CENTRE)
      userSizer.Add(self.usernameEntry, 0, wxALIGN_CENTRE | wxALL, 5)
      userSizer.Add((10,1),1,1)
      userSizer.Add(self.passEntryLabel, 0, wxALIGN_CENTRE)
      userSizer.Add(self.passEntry, 0, wxALIGN_CENTRE | wxALL, 5)

      # Add some buttons
      self.connectButton = wxButton(mainPanel, -1, "Connect")
      self.quitButton    = wxButton(mainPanel, -1, "Quit")
      buttonSizer = wxBoxSizer(wxHORIZONTAL)
      buttonSizer.Add(self.quitButton, 0, wxALIGN_CENTRE | wxALL, 5)
      if sys.platform.lower()[:-3] == "win":
         # Win32 users like their buttons in the wrong order
         buttonSizer.Prepend(self.connectButton, 0, wxALIGN_CENTRE | wxALL, 5)
      else:
         buttonSizer.Add(self.connectButton, 0, wxALIGN_CENTRE | wxALL, 5)
      buttonSizer.Prepend((10,1),1,wxEXPAND)

      self.topSizer = wxBoxSizer(wxVERTICAL)
      self.topSizer.Add(connectLabel, 0, wxALIGN_LEFT | wxLEFT | wxTOP, 10)
      self.topSizer.Add(connectSizer, 0, wxALIGN_LEFT | wxALL, 5)
      self.topSizer.Add(userLabel, 0, wxALIGN_LEFT | wxLEFT | wxTOP, 10)
      self.topSizer.Add(userSizer, 0, wxALIGN_LEFT | wxALL, 5)
      self.topSizer.Add((10,10),1,wxEXPAND)
      self.topSizer.Add(buttonSizer, 0, wxEXPAND | wxALL, 5)
      mainPanel.SetSizer(self.topSizer)
      self.topSizer.Fit(mainPanel)
      mainPanel.SetAutoLayout(1)

      self.hostEntry.SetFocus()

      EVT_SET_FOCUS(self.hostEntry, self.selectFocused)
      EVT_SET_FOCUS(self.portEntry, self.selectFocused)
      EVT_SET_FOCUS(self.usernameEntry, self.selectFocused)
      EVT_SET_FOCUS(self.passEntry, self.selectFocused)
      EVT_BUTTON(self, self.quitButton.GetId(), self.menuExit)
      EVT_MENU(self, EXIT, self.menuExit)


   # select contents of a focused wxTextCtrl
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
      alert = wxMessageDialog(self, info,
         "Server Message", wxOK|wxICON_INFORMATION)
      alert.ShowModal()


   def menuExit(self, ev):
      self.Close()


# arch-tag: connection window
