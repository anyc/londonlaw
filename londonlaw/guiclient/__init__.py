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


# Note: unfortunately the twisted "wxreactor" is broken at present and is
# unlikely to be fixed anytime soon.  Rather than trying to integrate the event
# loops, the solution used here is to run a single-threaded wxApp with a wxTimer
# that runs the twisted event loop periodically.


from twisted.internet import protocol, reactor
from twisted.python import log
from wxPython.wx import *
from ConnectWindow import *
from GameListWindow import *
from RegistrationWindow import *
from MainWindow import *
from Protocol import LLawClientProtocol
from GuiNetMessenger import *
import sys, socket



messenger = GuiNetMessenger()


class LLawClientFactory(protocol.ClientFactory):
   protocol = LLawClientProtocol

   def registerProtocol(self, p):
      messenger.registerProtocol(p)



# Run the whole shebang.
class MyApp(wxApp):

   def OnInit(self):
      TIMERID = 999999

      self.currentWindow = None
      messenger.registerConnectionWindowLauncher(self.chooseConnection)
      messenger.registerGameListWindowLauncher(self.chooseGame)
      messenger.registerRegistrationWindowLauncher(self.register)
      messenger.registerMainWindowLauncher(self.startGame)

      wxInitAllImageHandlers()  # Required to be able to load compressed images
      messenger.guiLaunchConnectionWindow()

      EVT_TIMER(self, TIMERID, self.OnTimer)
      self.timer = wxTimer(self, TIMERID)
      self.timer.Start(250, False)

      return true


   def OnTimer(self, event):
      reactor.runUntilCurrent()
      reactor.doIteration(0)


   def chooseConnection(self, event = None):
      if self.currentWindow:
         self.currentWindow.Destroy()
      self.connectFrame = ConnectWindow(None, -1, "London Law -- Connect to Server")
      self.connectFrame.Fit()
      self.connectFrame.Show(1)
      self.currentWindow = self.connectFrame
      EVT_BUTTON(self.connectFrame, self.connectFrame.connectButton.GetId(), self.connect)
      return self.connectFrame


   def chooseGame(self, event = None):
      if self.currentWindow:
         self.currentWindow.Destroy()
      self.chooseGameFrame = GameListWindow(None, -1, "London Law -- Choose a Game", messenger)
      self.chooseGameFrame.SetSize((640, 480))
      self.chooseGameFrame.Show(1)
      self.currentWindow = self.chooseGameFrame
      return self.chooseGameFrame


   def register(self, event = None):
      if self.currentWindow:
         self.currentWindow.Destroy()
      self.registerFrame = RegistrationWindow(None, -1, "London Law -- Team Selection", messenger)
      self.registerFrame.Fit()
      self.registerFrame.SetSize((640, 480))
      self.registerFrame.Show(1)
      self.currentWindow = self.registerFrame
      return self.registerFrame


   def startGame(self, username, playerList, event = None):
      if self.currentWindow:
         self.currentWindow.Destroy()
      self.mainFrame = MainWindow(None, -1, "London Law", username, playerList, messenger)
      self.mainFrame.SetSize((1000,740))
      self.mainFrame.Show(1)
      self.currentWindow = self.mainFrame
      return self.mainFrame


   def connect(self, event = None):
      hostname = self.connectFrame.hostEntry.GetValue()
      port     = self.connectFrame.portEntry.GetValue()
      username = self.connectFrame.usernameEntry.GetValue()
      password = self.connectFrame.passEntry.GetValue()
      if len(hostname) < 1:
         self.connectFrame.status.PushStatusText("You must enter a valid hostname.")
         return
      elif len(port) < 1:
         self.connectFrame.status.PushStatusText("You must enter a valid port number.")
         return
      elif len(username) < 1:
         self.connectFrame.status.PushStatusText("You must enter a valid username.")
         return
      else:
         try:
            portNum = int(port)
         except:
            self.connectFrame.status.PushStatusText("The port number must be an integer.")
            return

         messenger.setUsername(username)
         messenger.setPassword(password)
         self.connectFrame.status.PushStatusText("Connecting to server...")
         reactor.connectTCP(socket.gethostbyname(hostname), portNum, LLawClientFactory())


reactor.startRunning()
#log.startLogging(sys.stderr, 0)
app = MyApp(0)
app.MainLoop()



# arch-tag: main loop for gui
