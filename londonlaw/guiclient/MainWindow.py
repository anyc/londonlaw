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



# MainWindow.py
#
# This class handles the main in-game window.  It has a map window,
# a set of player status icons, a chat area, and some useful buttons.

from wxPython.wx import *
from MapWindow import *
from ChatPanel import *
from PlayerIcon import *
from MoveDialog import *
from HistoryWindow import *
from graphicalmap import *
from londonlaw.common.protocol import LLAW_VERSION
import time



class MainWindow(wxFrame):
   # players is a list of Mr. X and all detectives, their
   # positions, and their tokens
   def __init__(self, parent, ID, title, username, playerList, messenger):
      wxFrame.__init__(self, parent, ID, title)
      
      self.username         = username
      self.playerList       = playerList
      self.messenger        = messenger
      self.playerIdx        = -1
      self.gameover         = 0
      self.turn             = 0
      self.moveDialogExists = 0
      self.fullscreen       = 0
      self.lastMover        = None
      self.isMrX = (username == self.playerList[0][0])
      self.pawnName2Index = {"X" : 0, "Red" : 1, "Yellow" : 2,
            "Green" : 3, "Blue" : 4, "Black" : 5}
      self.ticketName2Index = {"taxi" : 0, "bus" : 1,
            "underground" : 2, "black" : 3, "double" : 4}

      self.EXIT       = 100
      self.DISCONNECT = 101
      self.FULLSCREEN = 102
      self.ZOOM       = 103
      self.HISTORY    = 104
      self.ABOUT      = 105

      # Create a menu bar
      menuBar = wxMenuBar()
      self.fileMenu = wxMenu()
      self.fileMenu.Append(self.DISCONNECT, "Disconnect", "Disconnect from server")
      self.fileMenu.Append(self.EXIT, "Exit\tCTRL+Q", "Exit London Law")
      menuBar.Append(self.fileMenu, "File")
      self.viewMenu = wxMenu()
      self.viewMenu.AppendCheckItem(self.FULLSCREEN, "Fullscreen Map\tCTRL+F11", "Toggle fullscreen map view")
      self.viewMenu.AppendCheckItem(self.ZOOM, "Map Zoom\tCTRL+Z", "Toggle map zoom level")
      self.viewMenu.AppendCheckItem(self.HISTORY, "Mr. X History\tCTRL+Y", "Show/hide the Mr. X history window")
      self.viewMenu.Check(self.HISTORY, true)
      menuBar.Append(self.viewMenu, "View")
      self.helpMenu = wxMenu()
      self.helpMenu.Append(self.ABOUT, "About London Law", "About London Law")
      menuBar.Append(self.helpMenu, "Help")
      self.SetMenuBar(menuBar)

      self.status = self.CreateStatusBar(3)
      self.status.SetStatusWidths([-1, -1, 70])
      self.status.PushStatusText("The game has not yet started.", 0)
      self.status.PushStatusText("Turn: 0", 2)

      usernameList = []
      tokenList = []
      for p in self.playerList:
         usernameList.append(p[0])
         tokenList.append(p[2])

      # contain everything in a panel to get rid of the lame dark grey
      # background in Win32
      self.panel = wxPanel(self, -1)

      # create the map window
      self.mapWindow = MapWindow(self.panel, usernameList)
      for i in range(len(self.playerList)):
         if self.playerList[i][1] != -1:
            self.mapWindow.setLocation(i, self.playerList[i][1])
         

      if self.isMrX:
         self.SetTitle("London Law -- Mr. X")
      else:
         self.SetTitle("London Law -- Detectives")
      

      # create a chat view and chat entry area
      self.chatWindow = ChatPanel(self.panel, "", not self.isMrX)

      # create the player icons
      self.icons = PlayerIconGroup(self.panel, usernameList, tokenList)

      # create the pushbuttons
      self.moveButton = wxButton(self.panel, -1, "Move")
      self.moveButton.Enable(false)
      self.historyButton = wxCheckBox(self.panel, -1, "View History")
      self.historyButton.SetValue(true)
      self.zoomButton = wxCheckBox(self.panel, -1, "Zoom")
      self.buttonSizer = wxBoxSizer(wxVERTICAL)
      self.buttonSizer.Add(self.zoomButton, 0, wxALL, 5)
      self.buttonSizer.Add(self.historyButton, 0, wxALL, 5)
      self.buttonSizer.Add(self.moveButton, 0, wxALL, 5)

      # create a history window
      self.historyWin = HistoryWindow(self.panel)

      self.centerSizer = wxBoxSizer(wxHORIZONTAL)
      self.centerSizer.Add(self.icons, 0, wxALIGN_CENTRE|wxALL)
      self.centerSizer.Add(self.buttonSizer, 0, wxALIGN_CENTRE)
      
      # the main window is composed of three areas stacked vertically:
      # map window, player status icons, and chat windows.
      # Use a Sizer to handle this geometry.
      self.mainSizer = wxBoxSizer(wxVERTICAL)
      self.mainSizer.Add(self.mapWindow, 1, wxEXPAND|wxBOTTOM, 5)
      self.mainSizer.Add(self.centerSizer, 0, wxALIGN_CENTRE)
      self.mainSizer.Add(self.chatWindow, 0, wxEXPAND | wxALL, 5)

      self.panelSizer = wxBoxSizer(wxHORIZONTAL)
      self.panelSizer.Add(self.historyWin, 0, wxEXPAND)
      self.panelSizer.Add(self.mainSizer, 1, wxEXPAND)
      
      self.panel.SetSizer(self.panelSizer)

      self.topSizer = wxBoxSizer(wxVERTICAL)
      self.topSizer.Add(self.panel, 1, wxEXPAND)
      self.SetSizer(self.topSizer)
      self.topSizer.Fit(self)
      self.SetAutoLayout(1)

      self.chatWindow.SetFocus()

      # need a data structure to hold a move from a MoveDialog
      self.move = []
      self.moveDialogId  = wxNewId()

      # initialize pixelToLoc algorithm
      generateGridHash()

      # make the buttons do some stuff
      EVT_CHECKBOX(self, self.zoomButton.GetId(), self.toggleZoom)
      EVT_CHECKBOX(self, self.historyButton.GetId(), self.toggleHistory)
      EVT_BUTTON(self, self.moveButton.GetId(), self.makeMove)
      EVT_TEXT_ENTER(self, self.chatWindow.chatEntry.GetId(), self.chatSend)
      EVT_MENU(self, self.EXIT, self.menuExit)
      EVT_MENU(self, self.DISCONNECT, self.menuDisconnect)
      EVT_MENU(self, self.FULLSCREEN, self.toggleFullscreen)
      EVT_MENU(self, self.ZOOM, self.toggleMenuZoom)
      EVT_MENU(self, self.HISTORY, self.toggleMenuHistory)
      EVT_MENU(self, self.ABOUT, self.showAbout)
      EVT_LEFT_DCLICK(self.icons.players[0].icon, self.scrollToPlayer0)
      EVT_LEFT_DCLICK(self.icons.players[1].icon, self.scrollToPlayer1)
      EVT_LEFT_DCLICK(self.icons.players[2].icon, self.scrollToPlayer2)
      EVT_LEFT_DCLICK(self.icons.players[3].icon, self.scrollToPlayer3)
      EVT_LEFT_DCLICK(self.icons.players[4].icon, self.scrollToPlayer4)
      EVT_LEFT_DCLICK(self.icons.players[5].icon, self.scrollToPlayer5)
      EVT_LEFT_DCLICK(self.mapWindow, self.moveToClicked)
      

   def addChatMessage(self, chatType, data):
      if chatType == "team":
         self.chatWindow.AppendText("<" + data[0] + " [to team]> " + data[1])
      else:
         self.chatWindow.AppendText("<" + data[0] + "> " + data[1])


   def menuExit(self, event):
      alert = wxMessageDialog(self, "Disconnect from the server and exit London Law?",
         "Disconnect and Quit", wxYES_NO|wxICON_EXCLAMATION)
      if alert.ShowModal() == wxID_YES:
         self.messenger.netDisconnect()
         self.Close()


   def menuDisconnect(self, event):
      alert = wxMessageDialog(self, "Disconnect from the server?",
         "Disconnect", wxYES_NO|wxICON_EXCLAMATION)
      if alert.ShowModal() == wxID_YES:
         self.messenger.netDisconnect()
         self.messenger.guiLaunchConnectionWindow()


   def moveDialogDestroyed(self, event):
      self.moveDialogExists = False


   def disableMoveButton(self):
      self.moveButton.Disable()


   def displayMove(self, data):
      mover  = self.pawnName2Index[data[0]]
      loc    = int(data[1])
      ticket = data[2]
      if loc != -1:
         self.mapWindow.setLocation(mover, loc)
         # FIXME: the map does need to be updated to move the pushpins, but
         # it can be done more effectively than redrawing the entire MapWindow.
         self.mapWindow.redraw()

      # update ticket inventories
      pawn    = self.playerList[mover]
      pawn[1] = loc
      if ticket == "taxi":
         if mover != 0:
            pawn[2][0] -= 1
         tstr = "a taxi."
      elif ticket == "bus":
         if mover != 0:
            pawn[2][1] -= 1
         tstr = "a bus."
      elif ticket == "underground":
         if mover != 0:
            pawn[2][2] -= 1
         tstr = "the underground."
      elif ticket == "black":
         pawn[2][3] -= 1
         tstr = "a black ticket."
      if mover == self.lastMover:
         # double move
         pawn[2][4] -= 1
      self.icons.players[mover].updateTokens(pawn[2])

      if mover == 0:
         self.historyWin.setTicket(self.turn - 1, self.ticketName2Index[ticket])
         if loc == -1:
            self.status.PushStatusText("Mr. X made his move using " + tstr, 1)
         else:
            if self.isMrX:
               self.status.PushStatusText("Mr. X moved to "+`loc`+" using " + tstr, 1)
            else:
               self.status.PushStatusText("Mr. X surfaced at "+`loc`+" using " + tstr, 1)
            self.historyWin.setLocation(self.turn - 1, str(loc))
      elif mover == 1:
         self.status.PushStatusText("The Red Detective moved to "+`loc`+" using " + tstr, 1)
      elif mover == 2:
         self.status.PushStatusText("The Yellow Detective moved to "+`loc`+" using " + tstr, 1)
      elif mover == 3:
         self.status.PushStatusText("The Green Detective moved to "+`loc`+" using " + tstr, 1)
      elif mover == 4:
         self.status.PushStatusText("The Blue Detective moved to "+`loc`+" using " + tstr, 1)
      elif mover == 5:
         self.status.PushStatusText("The Black Detective moved to "+`loc`+" using " + tstr, 1)
      else:
         print "unrecognized mover: " + str(mover)

      # pop up an alert box when X uses a double move
      if mover == self.lastMover and not self.isMrX:
         alert = wxMessageDialog(self, "Mr. X just used a double move ticket!",
            "Double Move", wxOK|wxICON_INFORMATION)
         alert.ShowModal()

      self.lastMover = mover
            

   # send out a chat message
   def chatSend(self, event):
      (text, sendTo) = self.chatWindow.GetEntry()
      if len(text) > 0:
         self.chatWindow.ClearEntry()
         self.messenger.netSendChat(text, sendTo)


   def makeMove(self, event):
      if not self.moveDialogExists:
         self.moveDialog = MoveDialog(self, self.moveDialogId, 0, self.playerList, 
               self.playerIdx, self.messenger)
         self.moveDialogExists = True
         self.moveDialog.Show(1)
         EVT_DIALOGDESTROYED(self.moveDialog, self.moveDialogDestroyed)
      else:
         # if the move dialog is already there, raise it to make sure the user can find it
         self.moveDialog.Show(1)
         self.moveDialog.Raise()
         self.moveDialog.SetFocus()


   def moveToClicked(self, event):
      if self.moveButton.IsEnabled():
         x, y   = event.GetPosition()
         dx, dy = self.mapWindow.GetScrollPixelsPerUnit()
         sx, sy = self.mapWindow.GetViewStart()
         dest   = pixelToLoc((sx*dx + x, sy*dy + y), self.mapWindow.zoomLevel)
         if not self.moveDialogExists:
            self.moveDialog = MoveDialog(self, self.moveDialogId, dest, 
                  self.playerList, self.playerIdx, self.messenger)
            self.moveDialogExists = True
            EVT_DIALOGDESTROYED(self.moveDialog, self.moveDialogDestroyed)
         else:
            self.moveDialog.setDest1(dest)
            # if the move dialog is already there, raise it to make sure the user can find it
            self.moveDialog.Raise()
            self.moveDialog.SetFocus()


   def pawnStuck(self, pawnName):
      self.icons.setStuck(self.pawnName2Index[pawnName])


   def showInfoAlert(self, info):
      alert = wxMessageDialog(self, info,
         "Server Message", wxOK|wxICON_INFORMATION)
      alert.ShowModal()


   def toggleZoom(self, event):
      if self.zoomButton.GetValue():
         self.viewMenu.Check(self.ZOOM, true)
         self.mapWindow.zoomIn()
      else:
         self.viewMenu.Check(self.ZOOM, false)
         self.mapWindow.zoomOut()


   def toggleMenuZoom(self, event):
      self.zoomButton.SetValue(not self.zoomButton.GetValue())
      self.toggleZoom(event)


   def toggleHistory(self, event):
      if self.historyButton.GetValue():
         self.viewMenu.Check(self.HISTORY, true)
         self.panelSizer.Prepend(self.historyWin, 0, wxEXPAND)
         self.historyWin.Show(true)
         self.panelSizer.Layout()
      else:
         self.viewMenu.Check(self.HISTORY, false)
         self.historyWin.Show(false)
         self.panelSizer.Remove(self.historyWin)
         self.panelSizer.Layout()

      # fix for graphical glitches in wxMSW
      self.zoomButton.Refresh()
      self.historyButton.Refresh()
      self.moveButton.Refresh()


   def toggleMenuHistory(self, event):
      self.historyButton.SetValue(not self.historyButton.GetValue())
      self.toggleHistory(event)


   def toggleFullscreen(self, event):
      if not self.fullscreen:
         self.fullscreen = 1
         self.viewMenu.Enable(self.HISTORY, false)
         self.viewMenu.Check(self.FULLSCREEN, true)
         if self.historyButton.GetValue():
            self.historyWin.Hide()
            self.panelSizer.Remove(self.historyWin)
         self.chatWindow.Hide()
         self.mainSizer.Remove(self.chatWindow)
         self.icons.Hide()
         self.zoomButton.Hide()
         self.historyButton.Hide()
         self.moveButton.Hide()
         self.buttonSizer.Remove(self.zoomButton)
         self.buttonSizer.Remove(self.historyButton)
         self.buttonSizer.Remove(self.moveButton)
         self.centerSizer.Remove(self.buttonSizer)
         self.centerSizer.Remove(self.icons)
         self.mainSizer.Remove(self.centerSizer)
         self.mainSizer.Layout()
         self.panelSizer.Layout()
      else:
         self.fullscreen = 0
         self.viewMenu.Enable(self.HISTORY, true)
         self.viewMenu.Check(self.FULLSCREEN, false)
         if self.historyButton.GetValue():
            self.historyWin.Show()
            self.panelSizer.Prepend(self.historyWin, 0, wxEXPAND)
         self.buttonSizer = wxBoxSizer(wxVERTICAL)
         self.buttonSizer.Add(self.zoomButton, 0, wxALL, 5)
         self.buttonSizer.Add(self.historyButton, 0, wxALL, 5)
         self.buttonSizer.Add(self.moveButton, 0, wxALL, 5)
         self.centerSizer = wxBoxSizer(wxHORIZONTAL)
         self.centerSizer.Add(self.icons, 0, wxALIGN_CENTRE|wxALL)
         self.centerSizer.Add(self.buttonSizer, 0, wxALIGN_CENTRE)
         self.mainSizer.Add(self.centerSizer, 0, wxALIGN_CENTRE)
         self.icons.Show()
         self.zoomButton.Show()
         self.historyButton.Show()
         self.moveButton.Show()
         self.chatWindow.Show()
         self.mainSizer.Add(self.chatWindow, 0, wxEXPAND | wxALL, 5)
         self.mainSizer.Layout()
         self.panelSizer.Layout()


   # display the About dialog
   def showAbout(self, event):
      about = wxMessageDialog(self, "London Law v" + LLAW_VERSION + 
              "\n\nA multiplayer manhunting adventure by Paul Pelzl",
              "About London Law", wxOK|wxICON_INFORMATION)
      about.ShowModal()

   def scrollToPlayer0(self, event):
      self.mapWindow.scrollToPlayer(0)

   def scrollToPlayer1(self, event):
      self.mapWindow.scrollToPlayer(1)
      
   def scrollToPlayer2(self, event):
      self.mapWindow.scrollToPlayer(2)

   def scrollToPlayer3(self, event):
      self.mapWindow.scrollToPlayer(3)

   def scrollToPlayer4(self, event):
      self.mapWindow.scrollToPlayer(4)

   def scrollToPlayer5(self, event):
      self.mapWindow.scrollToPlayer(5)

   def setTurnNum(self, turnNum):
      self.turn = turnNum
      self.status.PushStatusText("Turn: "+`self.turn`, 2)

   # FIXME: refactor.
   def setPawnTurn(self, pawnName):
      if pawnName == "X":
         if self.playerList[0][0] == self.username:
            self.moveButton.Enable(true)
            usernameStr = "you"
         else:
            usernameStr = self.playerList[0][0]
         self.status.PushStatusText("It is Mr. X's turn (" + usernameStr + ").", 0)
         self.playerIdx = 0
         self.icons.setTurn(0)
      elif pawnName == "Red":
         if self.playerList[1][0] == self.username:
            self.moveButton.Enable(true)
            usernameStr = "you"
         else:
            usernameStr = self.playerList[1][0]
         self.status.PushStatusText("It is the Red Detective's turn (" + usernameStr + ").", 0)
         self.playerIdx = 1
         self.icons.setTurn(1)
      elif pawnName == "Yellow":
         if self.playerList[2][0] == self.username:
            self.moveButton.Enable(true)
            usernameStr = "you"
         else:
            usernameStr = self.playerList[2][0]
         self.status.PushStatusText("It is the Yellow Detective's turn (" + usernameStr + ").", 0)
         self.playerIdx = 2
         self.icons.setTurn(2)
      elif pawnName == "Green":
         if self.playerList[3][0] == self.username:
            self.moveButton.Enable(true)
            usernameStr = "you"
         else:
            usernameStr = self.playerList[3][0]
         self.status.PushStatusText("It is the Green Detective's turn (" + usernameStr + ").", 0)
         self.playerIdx = 3
         self.icons.setTurn(3)
      elif pawnName == "Blue":
         if self.playerList[4][0] == self.username:
            self.moveButton.Enable(true)
            usernameStr = "you"
         else:
            usernameStr = self.playerList[4][0]
         self.status.PushStatusText("It is the Blue Detective's turn (" + usernameStr + ").", 0)
         self.playerIdx = 4
         self.icons.setTurn(4)
      elif pawnName == "Black":
         if self.playerList[5][0] == self.username:
            self.moveButton.Enable(true)
            usernameStr = "you"
         else:
            usernameStr = self.playerList[5][0]
         self.status.PushStatusText("It is the Black Detective's turn (" + usernameStr + ").", 0)
         self.playerIdx = 5
         self.icons.setTurn(5)
      

   def updateHistory(self, hist):
      for t in range(1, len(hist)):
         for move in hist[t]:
            if move[0] == "X":
               if int(move[1]) != -1:
                  self.historyWin.setLocation(t - 1, move[1])
               self.historyWin.setTicket(t - 1, self.ticketName2Index[move[2]])


#   def OnIdle(self, ev):
#      try:
#         event = guiQueue.get_nowait()
#         if event[0] == "game socket":
#            self.socket = event[1]
#         elif event[0] == "created move":
#            self.moveButton.Enable(false)
#         elif event[0] == "move dialog destroyed":
#            self.moveDialogExists = 0
#         elif event[0] == "incoming chat":
#            self.chatWindow.AppendText("<" + event[1] + "> " + event[2])
#         elif event[0] == "new turn":
#            self.turn = event[1]
#            self.status.PushStatusText("Turn: " + `self.turn`, 2)
#         elif event[0] == "someone's turn":
#            self.playerIdx = event[1]
#            if self.playerIdx == 0:
#               self.status.PushStatusText("It is Mr. X's turn (" + self.playerList[self.playerIdx][0] + ").", 0)
#            elif self.playerIdx == 1:
#               self.status.PushStatusText("It is the Red Detective's turn (" + self.playerList[self.playerIdx][0] + ").", 0)
#            elif self.playerIdx == 2:
#               self.status.PushStatusText("It is the Yellow Detective's turn (" + self.playerList[self.playerIdx][0] + ").", 0)
#            elif self.playerIdx == 3:
#               self.status.PushStatusText("It is the Green Detective's turn (" + self.playerList[self.playerIdx][0] + ").", 0)
#            elif self.playerIdx == 4:
#               self.status.PushStatusText("It is the Blue Detective's turn (" + self.playerList[self.playerIdx][0] + ").", 0)
#            elif self.playerIdx == 5:
#               self.status.PushStatusText("It is the Black Detective's turn (" + self.playerList[self.playerIdx][0] + ").", 0)
#            self.icons.setTurn(self.playerIdx)
#         elif event[0] == "your turn":
#            if self.playerIdx == 0:
#               self.status.PushStatusText("It is Mr. X's turn (you).", 0)
#            elif self.playerIdx == 1:
#               self.status.PushStatusText("It is the Red Detective's turn (you).", 0)
#            elif self.playerIdx == 2:
#               self.status.PushStatusText("It is the Yellow Detective's turn (you).", 0)
#            elif self.playerIdx == 3:
#               self.status.PushStatusText("It is the Green Detective's turn (you).", 0)
#            elif self.playerIdx == 4:
#               self.status.PushStatusText("It is the Blue Detective's turn (you).", 0)
#            elif self.playerIdx == 5:
#               self.status.PushStatusText("It is the Black Detective's turn (you).", 0)
#            self.moveButton.Enable(true)
#         elif event[0] == "move accepted":
#            self.moveButton.Enable(false)
#         elif event[0] == "move rejected":
#            self.moveButton.Enable(true) # just in case
#            self.status.PushStatusText("The server rejected your move.  It is still your turn.", 0)
#         elif event[0] == "double rejected":
#            self.moveButton.Enable(true) # just in case
#            self.status.PushStatusText("The server rejected your double move.  It is still your turn.", 0) 
#         elif event[0] == "someone moved":
#            mover = event[1]
#            loc   = event[2]
#            trans = event[3]
#            if loc != -1:
#               self.mapWindow.setLocation(mover, loc)
#               # FIXME: the map does need to be updated to move the pushpins, but
#               # it can be done more effectively than redrawing the entire MapWindow.
#               self.mapWindow.redraw()
#            # update the location and token list
#            if mover > 0:
#               # if this was a detective's move, the tokens
#               # go to Mr. X
#               x = self.playerList[0]
#               p = self.playerList[mover]
#               p[1] = loc
#               if trans == TAXI:
#                  p[2][0] -= 1
#                  x[2][0] += 1
#                  tstr = "a taxi."
#               elif trans == BUS:
#                  p[2][1] -= 1
#                  x[2][1] += 1
#                  tstr = "a bus."
#               elif trans == UNDERGROUND:
#                  p[2][2] -= 1
#                  x[2][2] += 1
#                  tstr = "the underground."
#               elif trans == BLACK:
#                  p[2][3] -= 1
#                  x[2][3] += 1
#                  tstr = "a black ticket."
#               self.playerList[mover] = p
#               self.playerList[0] = x
#               # update the player icon to show this info
#               self.icons.players[mover].updateTokens(self.playerList[mover][2])
#               self.icons.players[0].updateTokens(self.playerList[0][2])
#            else:
#               # if this was Mr. X's move, then just discard those tokens
#               p = self.playerList[mover]
#               p[1] = loc
#               if trans == TAXI:
#                  p[2][0] -= 1
#                  tstr = "a taxi."
#               elif trans == BUS:
#                  p[2][1] -= 1
#                  tstr = "a bus."
#               elif trans == UNDERGROUND:
#                  p[2][2] -= 1
#                  tstr = "the underground."
#               elif trans == BLACK:
#                  p[2][3] -= 1
#                  tstr = "a black ticket."
#               self.playerList[mover] = p
#               # update the player icon to show this info
#               self.icons.players[mover].updateTokens(self.playerList[mover][2])
#
#            if mover == 0:
#               self.historyWin.setTicket(self.turn-1, trans)
#               if loc == -1:
#                  self.status.PushStatusText("Mr. X made his move using " + tstr, 1)
#               else:
#                  if self.isMrX:
#                     self.status.PushStatusText("You moved to "+`loc`+" using " + tstr, 1)
#                  else:
#                     self.status.PushStatusText("Mr. X surfaced at "+`loc`+" using " + tstr, 1)
#                  self.historyWin.setLocation(self.turn-1, str(loc))
#            elif mover == 1:
#               self.status.PushStatusText("The Red Detective moved to "+`loc`+" using " + tstr, 1)
#            elif mover == 2:
#               self.status.PushStatusText("The Yellow Detective moved to "+`loc`+" using " + tstr, 1)
#            elif mover == 3:
#               self.status.PushStatusText("The Green Detective moved to "+`loc`+" using " + tstr, 1)
#            elif mover == 4:
#               self.status.PushStatusText("The Blue Detective moved to "+`loc`+" using " + tstr, 1)
#            elif mover == 5:
#               self.status.PushStatusText("The Black Detective moved to "+`loc`+" using " + tstr, 1)
#         elif event[0] == "double move":
#            self.status.PushStatusText("Mr. X is using a double move...", 1)
#            p = self.playerList[0]
#            p[2][4] -= 1
#            self.playerList[0] = p
#            self.icons.players[0].updateTokens(self.playerList[0][2])
#            self.status.PushStatusText("Turn: "+`self.turn`, 2)
#         elif event[0] == "someone's stuck":
#            # update the icons to show this information
#            if event[1] == 0:
#               self.status.PushStatusText("It is Mr. X's turn, but he is stuck!", 0)
#            elif event[1] == 1:
#               self.status.PushStatusText("It is the Red Detective's turn, but he is stuck!", 0)
#            elif event[1] == 2:
#               self.status.PushStatusText("It is the Yellow Detective's turn, but he is stuck!", 0)
#            elif event[1] == 3:
#               self.status.PushStatusText("It is the Green Detective's turn, but he is stuck!", 0)
#            elif event[1] == 4:
#               self.status.PushStatusText("It is the Blue Detective's turn, but he is stuck!", 0)
#            elif event[1] == 5:
#               self.status.PushStatusText("It is the Black Detective's turn, but he is stuck!", 0)
#            self.icons.setStuck(event[1])
#         elif event[0] == "x is stuck":
#            self.gameover = 1
#            self.status.PushStatusText("Mr. X is stuck.  The detectives win!", 0)
#         elif event[0] == "x survived":
#            self.gameover = 1
#            self.status.PushStatusText("Mr. X survived!  Game over.", 0)
#            alert = wxMessageDialog(self, "Mr. X successfully evaded the detectives!\nGame over.",
#               "Game Over", wxOK|wxICON_INFORMATION)
#            alert.ShowModal()
#         elif event[0] == "detectives all stuck":
#            for i in range(1, 6):
#               self.icons.setStuck(i)
#            self.gameover = 1
#            self.status.PushStatusText("The detectives are all stuck!  Game over.", 0)
#            alert = wxMessageDialog(self, "The detectives are all stuck!\nMr. X makes a clean getaway.  Game over.",
#               "Game Over", wxOK|wxICON_INFORMATION)
#            alert.ShowModal()
#         elif event[0] == "x is caught":
#            self.gameover = 1
#            if event[1] == 1:
#               detstr = "the Red Detective"
#            elif event[1] == 2:
#               detstr = "the Yellow Detective"
#            elif event[1] == 3:
#               detstr = "the Green Detective"
#            elif event[1] == 4:
#               detstr = "the Blue Detective"
#            elif event[1] == 5:
#               detstr = "the Black Detective"
#            self.status.PushStatusText("Mr. X was caught by "+detstr+" at "+`event[2]`+".  The detectives win!", 0)
#            alert = wxMessageDialog(self, "Mr. X was caught by "+detstr+" at "+`event[2]`+
#               ".  The detectives win!\nGame over.", "Game Over", wxOK|wxICON_INFORMATION)
#            alert.ShowModal()
#         elif event[0] == "connection error":
#            alert = wxMessageDialog(self, "The server reports that the connection to "+`event[1]`+" was lost.\n" +
#               "The game will end.", "Connection Error", wxOK|wxICON_INFORMATION)
#            alert.ShowModal()
#            self.disconnecting = 1
#            # FIXME: need a little more here... disable some widgets and so forth
#         elif event[0] == "disconnecting":
#            self.connected = 0
#            if self.exiting:
#               self.status.PushStatusText("Disconnected from server.  Exiting...", 0)
#               self.Close()
#            elif self.disconnecting:
#               self.status.PushStatusText("Disconnected from server.", 0)
#               # FIXME: need a little more here... disable some widgets and so forth
#            elif not self.gameover:
#               alert = wxMessageDialog(self, "The connection to the server was lost.\nThe game will end.",
#                  "Connection Error", wxOK|wxICON_ERROR)
#               alert.ShowModal()
#               # FIXME: need a little more here... disable some widgets and so forth
#         elif event[0] == "replay turn":
#            self.turn = event[1]
#         elif event[0] == "replay move":
#            mover = event[1]
#            loc   = event[2]
#            trans = event[3]
#            if not self.isMrX:
#               self.historyWin.setLocation(self.turn-1, str(loc))
#         else:
#            print "Unhandled event in MainWindow: " + event[0]
#
#         ev.RequestMore()
#
#      except Empty:
#         pass
#
#      ev.Skip()


# arch-tag: main window for gui
