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




# RegistrationWindow.py
#
# This module contains the classes that generate the list of players within a
# game room, permit changing teams, etc.


from twisted.python import log
from wxPython.wx import *
from londonlaw.common.protocol import *
from londonlaw.common.config import *
from AutoListCtrl import *
from ChatPanel import *
import os.path



# Create a small dialog for choosing a team.
class TeamDialog(wxDialog):
   def __init__(self, parent):
      wxDialog.__init__(self, parent, -1, "Choose a Team", wxDefaultPosition, wxDefaultSize, wxDEFAULT_DIALOG_STYLE|wxSUNKEN_BORDER)
      panel = wxPanel(self, -1, wxDefaultPosition, wxDefaultSize, wxTAB_TRAVERSAL)

      self.choice = wxRadioBox(panel, -1, "team: ", wxDefaultPosition, wxDefaultSize,
         ["Detectives", "Mr. X"], 1, wxRA_SPECIFY_COLS)
      self.submitButton = wxButton(panel, wxID_OK, "OK")
      self.cancelButton = wxButton(panel, wxID_CANCEL, "Cancel")

      buttonSizer = wxBoxSizer(wxHORIZONTAL)
      buttonSizer.Add(self.cancelButton, 0, wxALIGN_CENTRE|wxALL, 5)
      buttonSizer.Add(self.submitButton, 0, wxALIGN_CENTRE|wxALL, 5)

      vSizer = wxBoxSizer(wxVERTICAL)
      vSizer.Add(self.choice, 0, wxALIGN_CENTRE|wxALL, 5)
      vSizer.Add((1, 1), 1, wxEXPAND)
      vSizer.Add(buttonSizer, 0, wxALIGN_RIGHT|wxALL, 5)

      panel.SetSizer(vSizer)
      vSizer.Fit(panel)
      sizer = wxBoxSizer(wxVERTICAL)
      sizer.Add(panel, 1, wxEXPAND | wxALL, 5)
      self.SetSizer(sizer)
      sizer.Fit(self)
      self.SetAutoLayout(1)

      EVT_BUTTON(self, wxID_OK, self.submit)
      EVT_BUTTON(self, wxID_CANCEL, self.cancel) 


   def submit(self, event):
      self.EndModal(self.choice.GetSelection())

   def cancel(self, event):
      self.EndModal(-1)





# Generate the main registration window.
class RegistrationWindow(wxFrame):
   def __init__(self, parent, ID, title, messenger):
      wxFrame.__init__(self, parent, ID, title)

      self._messenger = messenger

      DISCONNECT = 100
      EXIT       = 101

      # Create a menu bar
      fileMenu = wxMenu("File")
      fileMenu.Append(DISCONNECT, "Disconnect", "Disconnect from server")
      fileMenu.Append(EXIT, "Exit\tCTRL+Q", "Exit London Law")
      menuBar = wxMenuBar()
      menuBar.Append(fileMenu, "File")
      self.SetMenuBar(menuBar)

      self.status = self.CreateStatusBar()

      # stick everything in a panel
      mainPanel = wxPanel(self, -1)

      self.list = AutoListCtrl(mainPanel, -1,
            ("Player", "Team", "Votes to Start?", "Pawns"),
            ("(no players joined)", "", "", ""))

      self.list.SetColumnWidth(1, 140) 

      mainSizer = wxBoxSizer(wxVERTICAL)
      mainSizer.Add(self.list, 3, wxALIGN_CENTRE|wxEXPAND|wxALL, 5)

      self.chatWindow = ChatPanel(mainPanel, "", False)
      mainSizer.Add(self.chatWindow, 2, wxEXPAND|wxALL, 5)

      self.leaveButton = wxButton(mainPanel, -1, "Leave Game")
      self.teamButton  = wxButton(mainPanel, -1, "Choose Team")
      self.voteButton  = wxButton(mainPanel, -1, "Vote to Start")
      buttonSizer      = wxBoxSizer(wxHORIZONTAL)
      buttonSizer.Add(self.leaveButton, 0, wxALIGN_CENTRE | wxLEFT | wxRIGHT | wxBOTTOM | wxALL, 5)
      buttonSizer.Add((1, 1), 1, wxEXPAND)
      buttonSizer.Add(self.teamButton, 0, wxALIGN_CENTRE | wxRIGHT | wxBOTTOM | wxALL, 5)
      buttonSizer.Add(self.voteButton, 0, wxALIGN_CENTRE | wxRIGHT | wxBOTTOM | wxALL, 5)
      mainSizer.Add(buttonSizer, 0, wxEXPAND, 0)

      mainPanel.SetSizer(mainSizer)
      mainSizer.Fit(mainPanel)

      EVT_MENU(self, EXIT, self.menuExit)
      EVT_MENU(self, DISCONNECT, self.menuDisconnect)
      EVT_BUTTON(self, self.leaveButton.GetId(), self.leaveGame)
      EVT_BUTTON(self, self.teamButton.GetId(), self.chooseTeam)
      EVT_BUTTON(self, self.voteButton.GetId(), self.voteStart)
      EVT_TEXT_ENTER(self, self.chatWindow.chatEntry.GetId(), self.chatSend)


   def addPlayer(self, data):
      log.msg("called RegistrationWindow.addPlayer()")
      self.list.addItem(data)


   def removePlayer(self, data):
      log.msg("called RegistrationWindow.removePlayer()")
      self.list.removeItemByData(data)


   def addChatMessage(self, chatType, data):
      log.msg("called RegistrationWindow.addChatMessage()")
      self.chatWindow.AppendText("<" + data[0] + "> " + data[1])


   def chatSend(self, event):
      (text, sendTo) = self.chatWindow.GetEntry()
      if len(text) > 0:
         self.chatWindow.ClearEntry()
         self._messenger.netSendChat(text, sendTo)


   def enableSelectButton(self, event):
      self.selectButton.Enable(TRUE)


   def disableSelectButton(self, event):
      self.selectButton.Disable()

      
   def disableVoteButton(self):
      self.voteButton.Disable()


   def chooseTeam(self, event):
      teamDialog = TeamDialog(self)
      value = teamDialog.ShowModal()  # 0 == Detectives, 1 == Mr. X
      if value == 0:
         self._messenger.netSetTeam("Detectives")
      elif value == 1:
         self._messenger.netSetTeam("Mr. X")


   def leaveGame(self, event):
      self._messenger.netLeaveGame()


   def showInfoAlert(self, info):
      self.PushStatusText("")
      alert = wxMessageDialog(self, info,
         "Server Message", wxOK|wxICON_INFORMATION)
      alert.ShowModal()


   def voteStart(self, event):
      self._messenger.netVoteStart()


   def menuExit(self, event):
      alert = wxMessageDialog(self, "Disconnect from the server and exit London Law?",
         "Disconnect and Quit", wxYES_NO|wxICON_EXCLAMATION)
      if alert.ShowModal() == wxID_YES:
         self._messenger.netDisconnect()
         self.Close()


   def menuDisconnect(self, event):
      alert = wxMessageDialog(self, "Disconnect from the server?",
         "Disconnect", wxYES_NO|wxICON_EXCLAMATION)
      if alert.ShowModal() == wxID_YES:
         self._messenger.netDisconnect()
         self._messenger.guiLaunchConnectionWindow()

      



# arch-tag: DO_NOT_CHANGE_0d8bbe23-c615-4456-9f0d-4c927786fcfe 
