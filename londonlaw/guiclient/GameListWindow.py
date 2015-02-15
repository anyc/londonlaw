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


import os.path, gettext, wx
from twisted.python import log
import wx
from londonlaw.common.protocol import *
from londonlaw.common.config import *
from AutoListCtrl import *




# Create a small dialog for creating a game
class NewGameDialog(wx.Dialog):
   def __init__(self, parent, returnValue):
      wx.Dialog.__init__(self, parent, -1, _("Create a New Game"), 
            wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE|wx.SUNKEN_BORDER)
      panel = wx.Panel(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)

      self.returnValue = returnValue

      labelFont = wx.Font(self.GetFont().GetPointSize(), wx.DEFAULT, wx.NORMAL, wx.BOLD)
      labelFont.SetWeight(wx.BOLD)
      newGameLabel = wx.StaticText(panel, -1, _("New Game: "))
      newGameLabel.SetFont(labelFont)
      nameLabel         = wx.StaticText(panel, -1, _("game room name:"), wx.Point(0,0))
      self.nameEntry    = wx.TextCtrl(panel, -1, "", wx.DefaultPosition, (170, wx.DefaultSize[1]))
      typeLabel         = wx.StaticText(panel, -1, _("game type:"), wx.Point(0,0))
      self.typeList     = wx.Choice(panel, -1, wx.DefaultPosition, wx.DefaultSize, ["standard"])
      self.submitButton = wx.Button(panel, wx.ID_OK, _("OK"))
      self.cancelButton = wx.Button(panel, wx.ID_CANCEL, _("Cancel"))
      self.typeList.SetSelection(0)

      hSizer = wx.BoxSizer(wx.HORIZONTAL)
      hSizer.Add((30, 1), 0, 0)
      hSizer.Add(nameLabel, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      hSizer.Add(self.nameEntry, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      hSizer.Add((10, 1), 0, 0)
      hSizer.Add(typeLabel, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      hSizer.Add(self.typeList, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

      bSizer = wx.BoxSizer(wx.HORIZONTAL)
      bSizer.Add((1, 1), 1, 0)
      bSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      bSizer.Add(self.submitButton, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

      vSizer = wx.BoxSizer(wx.VERTICAL)
      vSizer.Add(newGameLabel, 0, wx.ALIGN_LEFT|wx.ALL, 5)
      vSizer.Add(hSizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
      vSizer.Add(bSizer, 0, wx.EXPAND|wx.ALL, 5)

      panel.SetSizer(vSizer)
      vSizer.Fit(panel)
      sizer = wx.BoxSizer(wx.VERTICAL)
      sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 5)
      self.SetSizer(sizer)
      sizer.Fit(self)
      self.SetAutoLayout(1)

      wx.EVT_BUTTON(self, wx.ID_OK, self.submit)
      wx.EVT_BUTTON(self, wx.ID_CANCEL, self.cancel) 


   def submit(self, event):
      self.returnValue[0] = self.nameEntry.GetValue()
      self.returnValue[1] = self.typeList.GetStringSelection()
      self.EndModal(1)

   def cancel(self, event):
      self.EndModal(-1)




# Generate the main registration window.
class GameListWindow(wx.Frame):
   def __init__(self, parent, ID, title, messenger, exitCallback):
      wx.Frame.__init__(self, parent, ID, title)

      self._messenger   = messenger
      self.exitCallback = exitCallback

      DISCONNECT = 100
      EXIT       = 101

      # Create a menu bar
      # TRANSLATORS: this is a menu bar entry
      fileMenu = wx.Menu(_("File"))
      # TRANSLATORS: this is a menu bar entry
      fileMenu.Append(DISCONNECT, _("Disconnect"), _("Disconnect from server"))
      fileMenu.Append(EXIT, _("Exit%(hotkey)s") % {"hotkey" : "\tCTRL+Q"}, _("Exit London Law"))
      menuBar = wx.MenuBar()
      # TRANSLATORS: this is a menu bar entry
      menuBar.Append(fileMenu, _("File"))
      self.SetMenuBar(menuBar)

      self.status = self.CreateStatusBar()

      # stick everything in a panel
      mainPanel = wx.Panel(self, -1)

      self.list = AutoListCtrl(mainPanel, -1,
      # TRANSLATORS: these are column labels for the window where the user chooses a game
            (_("Game Room"), 
      # TRANSLATORS: these are column labels for the window where the user chooses a game
               _("Status"), 
      # TRANSLATORS: these are column labels for the window where the user chooses a game
               _("Game Type"), 
      # TRANSLATORS: these are column labels for the window where the user chooses a game
               _("Players")),
            (_("(no games currently available)"), "", "", ""))

      self.list.SetColumnWidth(1, 140) 
      self.list.SetColumnWidth(2, 140) 

      mainSizer = wx.BoxSizer(wx.VERTICAL)
      mainSizer.Add(self.list, 1, wx.ALIGN_CENTRE|wx.EXPAND|wx.ALL, 5)

      self.selectButton = wx.Button(mainPanel, -1, _("Join Game"))
      self.selectButton.Disable()
      self.createButton = wx.Button(mainPanel, -1, _("New Game"))
      buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
      buttonSizer.Add((1, 1), 1, wx.EXPAND)
      buttonSizer.Add(self.createButton, 0, wx.ALIGN_CENTRE | wx.RIGHT | wx.BOTTOM | wx.ALL, 5)
      buttonSizer.Add(self.selectButton, 0, wx.ALIGN_CENTRE | wx.RIGHT | wx.BOTTOM | wx.ALL, 5)
      mainSizer.Add(buttonSizer, 0, wx.EXPAND, 0)

      mainPanel.SetSizer(mainSizer)
      mainSizer.Fit(mainPanel)

      wx.EVT_CLOSE(self, self.menuExit)
      wx.EVT_MENU(self, EXIT, self.menuExit)
      wx.EVT_MENU(self, DISCONNECT, self.menuDisconnect)
      wx.EVT_LIST_ITEM_SELECTED(self, self.list.GetId(), self.enableSelectButton)
      wx.EVT_LIST_ITEM_DESELECTED(self, self.list.GetId(), self.disableSelectButton)
      wx.EVT_BUTTON(self, self.selectButton.GetId(), self.joinGame)
      wx.EVT_BUTTON(self, self.createButton.GetId(), self.createGame)


   def addGame(self, data):
      log.msg("called GameListWindow.addGame()")
      self.list.addItem(data)


   def removeGame(self, data):
      log.msg("called GameListWindow.removeGame()")
      self.list.removeItemByData(data)


   def enableSelectButton(self, event):
      self.selectButton.Enable(True)


   def disableSelectButton(self, event):
      self.selectButton.Disable()


   def createGame(self, event):
      gameData = [None, None]
      gameDialog = NewGameDialog(self, gameData)
      result     = gameDialog.ShowModal()
      if result == 1:
         self._messenger.netNewGame(gameData)
   

   def joinGame(self, event):
      selected = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
      self._messenger.netJoinGame(self.list.GetItemText(selected))  


   def showInfoAlert(self, info):
      self.PushStatusText("")
      alert = wx.MessageDialog(self, info,
         # TRANSLATORS: this is the title for a small alert window that pops up when the server reports an error
         _("Server Message"), wx.OK|wx.ICON_INFORMATION)
      alert.ShowModal()


   def menuExit(self, event):
      alert = wx.MessageDialog(self, _("Disconnect from the server and exit London Law?"),
         _("Disconnect and Quit"), wx.YES_NO|wx.ICON_EXCLAMATION)
      if alert.ShowModal() == wx.ID_YES:
         self._messenger.netShutdown()
         self.exitCallback(self)
         self.Destroy()


   def menuDisconnect(self, event):
      alert = wx.MessageDialog(self, _("Disconnect from the server?"),
         _("Disconnect"), wx.YES_NO|wx.ICON_EXCLAMATION)
      if alert.ShowModal() == wx.ID_YES:
         self._messenger.netDisconnect()




