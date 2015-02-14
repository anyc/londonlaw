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




# GameListWindow.py
#
# This module contains the classes that generate the list of game rooms, which
# appears after first logging in to a server.  Users may join exactly one game
# at a time, at which point a player registration window is spawned.


from twisted.python import log
from wxPython.wx import *
from londonlaw.common.protocol import *
from londonlaw.common.config import *
from AutoListCtrl import *
import os.path




# Create a small dialog for creating a game
class NewGameDialog(wxDialog):
   def __init__(self, parent, returnValue):
      wxDialog.__init__(self, parent, -1, "Create a New Game", 
            wxDefaultPosition, wxDefaultSize, wxDEFAULT_DIALOG_STYLE|wxSUNKEN_BORDER)
      panel = wxPanel(self, -1, wxDefaultPosition, wxDefaultSize, wxTAB_TRAVERSAL)

      self.returnValue = returnValue

      labelFont = wxFont(self.GetFont().GetPointSize(), wxDEFAULT, wxNORMAL, wxBOLD)
      labelFont.SetWeight(wxBOLD)
      newGameLabel = wxStaticText(panel, -1, "New Game: ")
      newGameLabel.SetFont(labelFont)
      nameLabel         = wxStaticText(panel, -1, "game room name:", wxPoint(0,0))
      self.nameEntry    = wxTextCtrl(panel, -1, "", wxDefaultPosition, (170, wxDefaultSize[1]))
      typeLabel         = wxStaticText(panel, -1, "game type:", wxPoint(0,0))
      self.typeList     = wxChoice(panel, -1, wxDefaultPosition, wxDefaultSize, ["standard"])
      self.submitButton = wxButton(panel, wxID_OK, "OK")
      self.cancelButton = wxButton(panel, wxID_CANCEL, "Cancel")
      self.typeList.SetSelection(0)

      hSizer = wxBoxSizer(wxHORIZONTAL)
      hSizer.Add((30, 1), 0, 0)
      hSizer.Add(nameLabel, 0, wxALIGN_CENTRE|wxALL, 5)
      hSizer.Add(self.nameEntry, 0, wxALIGN_CENTRE|wxALL, 5)
      hSizer.Add((10, 1), 0, 0)
      hSizer.Add(typeLabel, 0, wxALIGN_CENTRE|wxALL, 5)
      hSizer.Add(self.typeList, 0, wxALIGN_CENTRE|wxALL, 5)

      bSizer = wxBoxSizer(wxHORIZONTAL)
      bSizer.Add((1, 1), 1, 0)
      bSizer.Add(self.cancelButton, 0, wxALIGN_CENTRE|wxALL, 5)
      bSizer.Add(self.submitButton, 0, wxALIGN_CENTRE|wxALL, 5)

      vSizer = wxBoxSizer(wxVERTICAL)
      vSizer.Add(newGameLabel, 0, wxALIGN_LEFT|wxALL, 5)
      vSizer.Add(hSizer, 0, wxALIGN_LEFT|wxALL, 5)
      vSizer.Add(bSizer, 0, wxEXPAND|wxALL, 5)

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
      self.returnValue[0] = self.nameEntry.GetValue()
      self.returnValue[1] = self.typeList.GetStringSelection()
      self.EndModal(1)

   def cancel(self, event):
      self.EndModal(-1)




# Generate the main registration window.
class GameListWindow(wxFrame):
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
            ("Game Room", "Status", "Game Type", "Players"),
            ("(no games currently available)", "", "", ""))

      self.list.SetColumnWidth(1, 140) 
      self.list.SetColumnWidth(2, 140) 

      mainSizer = wxBoxSizer(wxVERTICAL)
      mainSizer.Add(self.list, 1, wxALIGN_CENTRE|wxEXPAND|wxALL, 5)

      self.selectButton = wxButton(mainPanel, -1, "Join Game")
      self.selectButton.Disable()
      self.createButton = wxButton(mainPanel, -1, "New Game")
      buttonSizer = wxBoxSizer(wxHORIZONTAL)
      buttonSizer.Add((1, 1), 1, wxEXPAND)
      buttonSizer.Add(self.createButton, 0, wxALIGN_CENTRE | wxRIGHT | wxBOTTOM | wxALL, 5)
      buttonSizer.Add(self.selectButton, 0, wxALIGN_CENTRE | wxRIGHT | wxBOTTOM | wxALL, 5)
      mainSizer.Add(buttonSizer, 0, wxEXPAND, 0)

      mainPanel.SetSizer(mainSizer)
      mainSizer.Fit(mainPanel)

      EVT_MENU(self, EXIT, self.menuExit)
      EVT_MENU(self, DISCONNECT, self.menuDisconnect)
      EVT_LIST_ITEM_SELECTED(self, self.list.GetId(), self.enableSelectButton)
      EVT_LIST_ITEM_DESELECTED(self, self.list.GetId(), self.disableSelectButton)
      EVT_BUTTON(self, self.selectButton.GetId(), self.joinGame)
      EVT_BUTTON(self, self.createButton.GetId(), self.createGame)


   def addGame(self, data):
      log.msg("called GameListWindow.addGame()")
      self.list.addItem(data)


   def removeGame(self, data):
      log.msg("called GameListWindow.removeGame()")
      self.list.removeItemByData(data)


   def enableSelectButton(self, event):
      self.selectButton.Enable(TRUE)


   def disableSelectButton(self, event):
      self.selectButton.Disable()


   def createGame(self, event):
      gameData = [None, None]
      gameDialog = NewGameDialog(self, gameData)
      result     = gameDialog.ShowModal()
      if result == 1:
         self._messenger.netNewGame(gameData)
   

   def joinGame(self, event):
      selected = self.list.GetNextItem(-1, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED)
      self._messenger.netJoinGame(self.list.GetItemText(selected))  


   def showInfoAlert(self, info):
      self.PushStatusText("")
      alert = wxMessageDialog(self, info,
         "Server Message", wxOK|wxICON_INFORMATION)
      alert.ShowModal()


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





# arch-tag: DO_NOT_CHANGE_a132dd66-4b99-4f90-8d6e-f79cbb67a0bb 
