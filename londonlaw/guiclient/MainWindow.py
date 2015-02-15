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



# MainWindow.py
#
# This class handles the main in-game window.  It has a map window,
# a set of player status icons, a chat area, and some useful buttons.

import time, gettext, wx
from MapWindow import *
from ChatPanel import *
from PlayerIcon import *
from MoveDialog import *
from HistoryWindow import *
from graphicalmap import *
from londonlaw.common.protocol import LLAW_VERSION



class MainWindow(wx.Frame):
   # players is a list of Mr. X and all detectives, their
   # positions, and their tokens
   def __init__(self, parent, ID, title, username, playerList, messenger, exitCallback):
      wx.Frame.__init__(self, parent, ID, title)
      
      self.username         = username
      self.playerList       = playerList
      self.messenger        = messenger
      self.playerIdx        = -1
      self.gameover         = 0
      self.turn             = 0
      self.moveDialogExists = False
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

      self.exitCallback = exitCallback

      # Create a menu bar
      menuBar = wx.MenuBar()
      self.fileMenu = wx.Menu()
      # TRANSLATORS: this is a menu bar entry
      self.fileMenu.Append(self.DISCONNECT, _("Disconnect"), _("Disconnect from server"))
      # TRANSLATORS: this is a menu bar entry
      self.fileMenu.Append(self.EXIT, _("Exit%(hotkey)s") % {"hotkey": "\tCTRL+Q"}, _("Exit London Law"))
      # TRANSLATORS: this is a menu bar entry
      menuBar.Append(self.fileMenu, _("File"))
      self.viewMenu = wx.Menu()
      # TRANSLATORS: this is a menu bar entry
      self.viewMenu.AppendCheckItem(self.FULLSCREEN, _("Fullscreen Map%(hotkey)s") % {"hotkey": "\tCTRL+F11"}, 
            _("Toggle fullscreen map view"))
      # TRANSLATORS: this is a menu bar entry
      self.viewMenu.AppendCheckItem(self.ZOOM, _("Map Zoom%(hotkey)s") % {"hotkey": "\tCTRL+Z"}, 
            _("Toggle map zoom level"))
      # TRANSLATORS: this is a menu bar entry
      self.viewMenu.AppendCheckItem(self.HISTORY, _("Mr. X History%(hotkey)s") % {"hotkey": "\tCTRL+Y"}, 
            _("Show/hide the Mr. X history window"))
      self.viewMenu.Check(self.HISTORY, True)
      # TRANSLATORS: this is a menu bar entry
      menuBar.Append(self.viewMenu, _("View"))
      self.helpMenu = wx.Menu()
      # TRANSLATORS: this is a menu bar entry
      self.helpMenu.Append(self.ABOUT, _("About London Law"), _("About London Law"))
      # TRANSLATORS: this is a menu bar entry
      menuBar.Append(self.helpMenu, _("Help"))
      self.SetMenuBar(menuBar)

      self.status = self.CreateStatusBar(3)
      self.status.SetStatusWidths([-1, -1, 70])
      self.status.PushStatusText(_("The game has not yet started."), 0)
      # TRANSLATORS: this is the initial value of the turn counter at the bottom right of the game window
      self.status.PushStatusText(_("Turn: 0"), 2)

      usernameList = []
      tokenList = []
      for p in self.playerList:
         usernameList.append(p[0])
         tokenList.append(p[2])

      # contain everything in a panel to get rid of the lame dark grey
      # background in Win32
      self.panel = wx.Panel(self, -1)

      # create the map window
      self.mapWindow = MapWindow(self.panel, usernameList)
      for i in range(len(self.playerList)):
         if self.playerList[i][1] != -1:
            self.mapWindow.setLocation(i, self.playerList[i][1])
         

      if self.isMrX:
         # TRANSLATORS: this is the main game window title
         self.SetTitle(_("London Law -- Mr. X"))
      else:
         # TRANSLATORS: this is the main game window title
         self.SetTitle(_("London Law -- Detectives"))
      

      # create a chat view and chat entry area
      self.chatWindow = ChatPanel(self.panel, "", not self.isMrX)

      # create the player icons
      self.icons = PlayerIconGroup(self.panel, usernameList, tokenList)

      # create the pushbuttons
      # TRANSLATORS: label for the "make a move" button
      self.moveButton = wx.Button(self.panel, -1, _("Move"))
      self.moveButton.Enable(False)
      # TRANSLATORS: label for the "view Mr. X history" toggle checkbox
      self.historyButton = wx.CheckBox(self.panel, -1, _("View History"))
      self.historyButton.SetValue(True)
      # TRANSLATORS: label for the map zoom toggle checkbox
      self.zoomButton = wx.CheckBox(self.panel, -1, _("Zoom"))
      self.buttonSizer = wx.BoxSizer(wx.VERTICAL)
      self.buttonSizer.Add(self.zoomButton, 0, wx.ALL, 5)
      self.buttonSizer.Add(self.historyButton, 0, wx.ALL, 5)
      self.buttonSizer.Add(self.moveButton, 0, wx.ALL, 5)

      # create a history window
      self.historyWin = HistoryWindow(self.panel)

      self.centerSizer = wx.BoxSizer(wx.HORIZONTAL)
      self.centerSizer.Add(self.icons, 0, wx.ALIGN_CENTRE|wx.ALL)
      self.centerSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)
      
      # the main window is composed of three areas stacked vertically:
      # map window, player status icons, and chat windows.
      # Use a Sizer to handle this geometry.
      self.mainSizer = wx.BoxSizer(wx.VERTICAL)
      self.mainSizer.Add(self.mapWindow, 1, wx.EXPAND|wx.BOTTOM, 5)
      self.mainSizer.Add(self.centerSizer, 0, wx.ALIGN_CENTRE)
      self.mainSizer.Add(self.chatWindow, 0, wx.EXPAND | wx.ALL, 5)

      self.panelSizer = wx.BoxSizer(wx.HORIZONTAL)
      self.panelSizer.Add(self.historyWin, 0, wx.EXPAND)
      self.panelSizer.Add(self.mainSizer, 1, wx.EXPAND)
      
      self.panel.SetSizer(self.panelSizer)

      self.topSizer = wx.BoxSizer(wx.VERTICAL)
      self.topSizer.Add(self.panel, 1, wx.EXPAND)
      self.SetSizer(self.topSizer)
      self.topSizer.Fit(self)
      self.SetAutoLayout(1)

      self.chatWindow.SetFocus()

      # need a data structure to hold a move from a MoveDialog
      self.move = []
      self.moveDialogId = wx.NewId()

      # initialize pixelToLoc algorithm
      generateGridHash()

      # make the buttons do some stuff
      wx.EVT_CHECKBOX(self, self.zoomButton.GetId(), self.toggleZoom)
      wx.EVT_CHECKBOX(self, self.historyButton.GetId(), self.toggleHistory)
      wx.EVT_BUTTON(self, self.moveButton.GetId(), self.makeMove)
      wx.EVT_TEXT_ENTER(self, self.chatWindow.chatEntry.GetId(), self.chatSend)
      wx.EVT_MENU(self, self.EXIT, self.menuExit)
      wx.EVT_MENU(self, self.DISCONNECT, self.menuDisconnect)
      wx.EVT_MENU(self, self.FULLSCREEN, self.toggleFullscreen)
      wx.EVT_MENU(self, self.ZOOM, self.toggleMenuZoom)
      wx.EVT_MENU(self, self.HISTORY, self.toggleMenuHistory)
      wx.EVT_MENU(self, self.ABOUT, self.showAbout)
      wx.EVT_LEFT_DCLICK(self.icons.players[0].icon, self.scrollToPlayer0)
      wx.EVT_LEFT_DCLICK(self.icons.players[1].icon, self.scrollToPlayer1)
      wx.EVT_LEFT_DCLICK(self.icons.players[2].icon, self.scrollToPlayer2)
      wx.EVT_LEFT_DCLICK(self.icons.players[3].icon, self.scrollToPlayer3)
      wx.EVT_LEFT_DCLICK(self.icons.players[4].icon, self.scrollToPlayer4)
      wx.EVT_LEFT_DCLICK(self.icons.players[5].icon, self.scrollToPlayer5)
      wx.EVT_LEFT_DCLICK(self.mapWindow, self.moveToClicked)
      wx.EVT_CLOSE(self, self.menuExit)
      

   def addChatMessage(self, chatType, data):
      if chatType == "team":
         # TRANSLATORS: this is how team chat messages will appear
         self.chatWindow.AppendText(_("<%(playername)s [to team]> %(message)s") % 
         {"playername" : data[0], "message" : data[1]})
      else:
         # TRANSLATORS: this is how chat messages will appear
         self.chatWindow.AppendText(_("<%(playername)s> %(message)s") % 
         {"playername" : data[0], "message" : data[1]})


   def menuExit(self, event):
      alert = wx.MessageDialog(self, _("Disconnect from the server and exit London Law?"),
         _("Disconnect and Quit"), wx.YES_NO|wx.ICON_EXCLAMATION)
      if alert.ShowModal() == wx.ID_YES:
         self.messenger.netShutdown()
         self.exitCallback(self)
         self.Destroy()


   def menuDisconnect(self, event):
      alert = wx.MessageDialog(self, _("Disconnect from the server?"),
         _("Disconnect"), wx.YES_NO|wx.ICON_EXCLAMATION)
      if alert.ShowModal() == wx.ID_YES:
         self.messenger.netDisconnect()


   def moveDialogDestroyed(self):
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
         # TRANSLATORS: as in "Mr. X made his move using 'a taxi'."
         tstr = _("a taxi")
      elif ticket == "bus":
         if mover != 0:
            pawn[2][1] -= 1
         # TRANSLATORS: as in "Mr. X made his move using 'a bus'."
         tstr = _("a bus")
      elif ticket == "underground":
         if mover != 0:
            pawn[2][2] -= 1
         # TRANSLATORS: as in "Mr. X made his move using 'the underground'."
         tstr = _("the underground")
      elif ticket == "black":
         pawn[2][3] -= 1
         # TRANSLATORS: as in "Mr. X made his move using 'a black ticket'."
         tstr = _("a black ticket")
      if mover == self.lastMover:
         # double move
         pawn[2][4] -= 1
      self.icons.players[mover].updateTokens(pawn[2])

      if mover == 0:
         self.historyWin.setTicket(self.turn - 1, self.ticketName2Index[ticket])
         if loc == -1:
            self.status.PushStatusText(_("Mr. X made his move using %(transport)s.") % {"transport": tstr}, 1)
         else:
            if self.isMrX:
               self.status.PushStatusText(_("Mr. X moved to %(number)d using %(transport)s.") % 
                     {"number" : loc, "transport" : tstr}, 1)
            else:
               self.status.PushStatusText(_("Mr. X surfaced at %(number)d using %(transport)s.") %
                     {"number" : loc, "transport" : tstr}, 1)
            self.historyWin.setLocation(self.turn - 1, str(loc))
      elif mover == 1:
         self.status.PushStatusText(_("The Red Detective moved to %(number)d using %(transport)s.") %
               {"number" : loc, "transport" : tstr}, 1)
      elif mover == 2:
         self.status.PushStatusText(_("The Yellow Detective moved to %(number)d using %(transport)s.") %
               {"number" : loc, "transport" : tstr}, 1)
      elif mover == 3:
         self.status.PushStatusText(_("The Green Detective moved to %(number)d using %(transport)s.") %
               {"number" : loc, "transport" : tstr}, 1)
      elif mover == 4:
         self.status.PushStatusText(_("The Blue Detective moved to %(number)d using %(transport)s.") %
               {"number" : loc, "transport" : tstr}, 1)
      elif mover == 5:
         self.status.PushStatusText(_("The Black Detective moved to %(number)d using %(transport)s.") %
               {"number" : loc, "transport" : tstr}, 1)
      else:
         print "unrecognized mover: " + str(mover)

      # pop up an alert box when X uses a double move
      if mover == self.lastMover and not self.isMrX:
         alert = wx.MessageDialog(self, _("Mr. X just used a double move ticket!"),
            # TRANSLATORS: this is the title of an alert window that pops up when X double-moves
            _("Double Move"), wx.OK|wx.ICON_INFORMATION)
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
               self.playerIdx, self.messenger, self.moveDialogDestroyed)
         self.moveDialogExists = True
         self.moveDialog.Show(1)
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
                  self.playerList, self.playerIdx, self.messenger, self.moveDialogDestroyed)
            self.moveDialogExists = True
         else:
            self.moveDialog.setDest1(dest)
            # if the move dialog is already there, raise it to make sure the user can find it
            if self.moveDialog.IsShown():
               self.moveDialog.Raise()
               self.moveDialog.SetFocus()


   def pawnStuck(self, pawnName):
      self.icons.setStuck(self.pawnName2Index[pawnName])


   def showInfoAlert(self, info):
      alert = wx.MessageDialog(self, info,
         # TRANSLATORS: this is the title for a small alert window that pops up when the server reports an error
         _("Server Message"), wx.OK|wx.ICON_INFORMATION)
      alert.ShowModal()


   def toggleZoom(self, event):
      if self.zoomButton.GetValue():
         self.viewMenu.Check(self.ZOOM, True)
         self.mapWindow.zoomIn()
      else:
         self.viewMenu.Check(self.ZOOM, False)
         self.mapWindow.zoomOut()


   def toggleMenuZoom(self, event):
      self.zoomButton.SetValue(not self.zoomButton.GetValue())
      self.toggleZoom(event)


   def toggleHistory(self, event):
      if self.historyButton.GetValue():
         self.viewMenu.Check(self.HISTORY, True)
         self.panelSizer.Prepend(self.historyWin, 0, wx.EXPAND)
         self.historyWin.Show(True)
         self.panelSizer.Layout()
      else:
         self.viewMenu.Check(self.HISTORY, False)
         self.historyWin.Show(False)
#<<<<<<< HEAD
         #self.panelSizer.Remove(self.historyWin)
#=======
         self.panelSizer.Detach(self.historyWin)
#>>>>>>> Update for wxPython3.0 compatibility
         self.panelSizer.Layout()

      # fix for graphical glitches in wx.MSW
      self.zoomButton.Refresh()
      self.historyButton.Refresh()
      self.moveButton.Refresh()


   def toggleMenuHistory(self, event):
      self.historyButton.SetValue(not self.historyButton.GetValue())
      self.toggleHistory(event)


   def toggleFullscreen(self, event):
      if not self.fullscreen:
         self.fullscreen = 1
         self.viewMenu.Enable(self.HISTORY, False)
         self.viewMenu.Check(self.FULLSCREEN, True)
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
         self.viewMenu.Enable(self.HISTORY, True)
         self.viewMenu.Check(self.FULLSCREEN, False)
         if self.historyButton.GetValue():
            self.historyWin.Show()
            self.panelSizer.Prepend(self.historyWin, 0, wx.EXPAND)
         self.buttonSizer = wx.BoxSizer(wx.VERTICAL)
         self.buttonSizer.Add(self.zoomButton, 0, wx.ALL, 5)
         self.buttonSizer.Add(self.historyButton, 0, wx.ALL, 5)
         self.buttonSizer.Add(self.moveButton, 0, wx.ALL, 5)
         self.centerSizer = wx.BoxSizer(wx.HORIZONTAL)
         self.centerSizer.Add(self.icons, 0, wx.ALIGN_CENTRE|wx.ALL)
         self.centerSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)
         self.mainSizer.Add(self.centerSizer, 0, wx.ALIGN_CENTRE)
         self.icons.Show()
         self.zoomButton.Show()
         self.historyButton.Show()
         self.moveButton.Show()
         self.chatWindow.Show()
         self.mainSizer.Add(self.chatWindow, 0, wx.EXPAND | wx.ALL, 5)
         self.mainSizer.Layout()
         self.panelSizer.Layout()


   # display the About dialog
   def showAbout(self, event):
      about = wx.MessageDialog(self, 
              _("London Law v%(version)s\n\nA multiplayer manhunting adventure by Paul Pelzl") %
              {"version" : LLAW_VERSION},
              _("About London Law"), wx.OK|wx.ICON_INFORMATION)
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
      # TRANSLATORS: this is the turn counter at the lower right of the game window
      self.status.PushStatusText(_("Turn: %(num)d") % {"num" : self.turn}, 2)

   # FIXME: refactor.
   def setPawnTurn(self, pawnName):
      if pawnName == "X":
         if self.playerList[0][0] == self.username:
            self.moveButton.Enable(True)
            # TRANSLATORS: this should be reference to the user--in English, "you" or "yourself" would both work
            usernameStr = _("you")
         else:
            usernameStr = self.playerList[0][0]
         self.status.PushStatusText(_("It is Mr. X's turn (%(username)s).") % {"username" : usernameStr}, 0)
         self.playerIdx = 0
         self.icons.setTurn(0)
      elif pawnName == "Red":
         if self.playerList[1][0] == self.username:
            self.moveButton.Enable(True)
            # TRANSLATORS: this should be reference to the user--in English, "you" or "yourself" would both work
            usernameStr = _("you")
         else:
            usernameStr = self.playerList[1][0]
         self.status.PushStatusText(_("It is the Red Detective's turn (%(username)s).") % {"username" : usernameStr}, 0)
         self.playerIdx = 1
         self.icons.setTurn(1)
      elif pawnName == "Yellow":
         if self.playerList[2][0] == self.username:
            self.moveButton.Enable(True)
            # TRANSLATORS: this should be reference to the user--in English, "you" or "yourself" would both work
            usernameStr = _("you")
         else:
            usernameStr = self.playerList[2][0]
         self.status.PushStatusText(_("It is the Yellow Detective's turn (%(username)s).") % {"username" : usernameStr}, 0)
         self.playerIdx = 2
         self.icons.setTurn(2)
      elif pawnName == "Green":
         if self.playerList[3][0] == self.username:
            self.moveButton.Enable(True)
            # TRANSLATORS: this should be reference to the user--in English, "you" or "yourself" would both work
            usernameStr = _("you")
         else:
            usernameStr = self.playerList[3][0]
         self.status.PushStatusText(_("It is the Green Detective's turn (%(username)s).") % {"username" : usernameStr}, 0)
         self.playerIdx = 3
         self.icons.setTurn(3)
      elif pawnName == "Blue":
         if self.playerList[4][0] == self.username:
            self.moveButton.Enable(True)
            # TRANSLATORS: this should be reference to the user--in English, "you" or "yourself" would both work
            usernameStr = _("you")
         else:
            usernameStr = self.playerList[4][0]
         self.status.PushStatusText(_("It is the Blue Detective's turn (%(username)s).") % {"username" : usernameStr}, 0)
         self.playerIdx = 4
         self.icons.setTurn(4)
      elif pawnName == "Black":
         if self.playerList[5][0] == self.username:
            self.moveButton.Enable(True)
            # TRANSLATORS: this should be reference to the user--in English, "you" or "yourself" would both work
            usernameStr = _("you")
         else:
            usernameStr = self.playerList[5][0]
         self.status.PushStatusText(_("It is the Black Detective's turn (%(username)s).") % {"username" : usernameStr}, 0)
         self.playerIdx = 5
         self.icons.setTurn(5)
      

   def updateHistory(self, hist):
      for t in range(1, len(hist)):
         for move in hist[t]:
            if move[0] == "X":
               if int(move[1]) != -1:
                  self.historyWin.setLocation(t - 1, move[1])
               self.historyWin.setTicket(t - 1, self.ticketName2Index[move[2]])



