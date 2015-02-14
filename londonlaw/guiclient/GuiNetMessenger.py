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



# messenger class that sends communications between
# protocol and gui
class GuiNetMessenger:

   def getUsername(self):
      return self._username

   def getPassword(self):
      return self._password

   def guiAddGame(self, data):
      self._gameListWindow.addGame(data)

   def guiAddPlayer(self, data):
      self._registrationWindow.addPlayer(data)

   def guiAlert(self, info):
      self._currentWindow.showInfoAlert(info)

   def guiDisableVoteButton(self):
      self._registrationWindow.disableVoteButton()

   def guiDisableMove(self):
      self._mainWindow.disableMoveButton()

   def guiDisplayMove(self, data):
      self._mainWindow.displayMove(data)

   def guiLaunchConnectionWindow(self):
      self._connectionWindow = self._launchConnectionWindow()
      self._currentWindow    = self._connectionWindow

   def guiLaunchGameListWindow(self):
      self._gameListWindow = self._launchGameListWindow()
      self._currentWindow  = self._gameListWindow

   def guiLaunchMainWindow(self, pawnInfo):
      self._mainWindow    = self._launchMainWindow(self._username, pawnInfo)
      self._currentWindow = self._mainWindow

   def guiLaunchRegistrationWindow(self):
      self._registrationWindow = self._launchRegistrationWindow()
      self._currentWindow      = self._registrationWindow

   def guiPawnStuck(self, pawnName):
      self._mainWindow.pawnStuck(pawnName)

   def guiRemoveGame(self, data):
      self._gameListWindow.removeGame(data)

   def guiRemovePlayer(self, data):
      self._registrationWindow.removePlayer(data)

   def guiSetTurnNum(self, turnNum):
      self._mainWindow.setTurnNum(int(turnNum))

   def guiSetPawnTurn(self, pawnName):
      self._mainWindow.setPawnTurn(pawnName)

   def guiUpdateHistory(self, history):
      self._mainWindow.updateHistory(history)

   def guiUpdateStatusBar(self, s):
      self._currentWindow.PushStatusText(s)

   def guiUpdateChat(self, chatType, data):
      self._currentWindow.addChatMessage(chatType, data)

   def netDisconnect(self):
      self._protocol.disconnect()

   def netJoinGame(self, name):
      self._protocol.join(name)

   def netMakeMove(self, data):
      self._protocol.makeMove(data)

   def netNewGame(self, data):
      self._protocol.newgame(data)

   def netSendChat(self, text, sendTo):
      self._protocol.sendChat(text, sendTo)

   def netSetTeam(self, team):
      self._protocol.setTeam(team)

   def netLeaveGame(self):
      self._protocol.leave()

   def netVoteStart(self):
      self._protocol.vote()

   def registerProtocol(self, p):
      self._protocol = p
      self._protocol.setMessenger(self)

   def registerConnectionWindowLauncher(self, f):
      self._launchConnectionWindow = f

   def registerGameListWindowLauncher(self, f):
      self._launchGameListWindow = f

   def registerMainWindowLauncher(self, f):
      self._launchMainWindow = f

   def registerRegistrationWindowLauncher(self, f):
      self._launchRegistrationWindow = f

   def setUsername(self, username):
      self._username = username

   def setPassword(self, password):
      self._password = password


# arch-tag: DO_NOT_CHANGE_38ff0d11-bcdb-48c7-92ed-45992c747886 
