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
# loops, the solution used here is to run a single-threaded wx.App with a wx.Timer
# that runs the twisted event loop periodically.


from londonlaw.common import threadedselectreactor
threadedselectreactor.install()

import sys, gettext
from twisted.internet import protocol, reactor
from twisted.python import log
import wxversion
try:
	wxversion.select("3.0")
except wxversion.VersionError:
	wxversion.select("2.8")

import wx
from ConnectWindow import *
from GameListWindow import *
from RegistrationWindow import *
from MainWindow import *
from Protocol import LLawClientProtocol
from GuiNetMessenger import *



messenger = GuiNetMessenger()


class LLawClientFactory(protocol.ClientFactory):
   protocol = LLawClientProtocol

   def registerProtocol(self, p):
      messenger.registerProtocol(p)

   def clientConnectionFailed(self, connector, reason):
      messenger.guiAlert(_("Unable to connect to server."))


# ensure the Twisted reactor gets cleanly shut down
def shutdown(shutdownWindow):
   reactor.addSystemEventTrigger('after', 'shutdown', shutdownWindow.Close, True)
   reactor.stop()


# Run the whole shebang.
class MyApp(wx.App):

   def OnInit(self):
      TIMERID = 999999

      self.currentWindow = None
      messenger.registerConnectionWindowLauncher(self.chooseConnection)
      messenger.registerGameListWindowLauncher(self.chooseGame)
      messenger.registerRegistrationWindowLauncher(self.register)
      messenger.registerMainWindowLauncher(self.startGame)

#<<<<<<< HEAD
      #wx.InitAllImageHandlers()        # Required to be able to load compressed images
      #reactor.interleave(wx.CallAfter) # Integrate Twisted and wxPython event loops
##=======
      #messenger.guiLaunchConnectionWindow()

      #wx.EVT_TIMER(self, TIMERID, self.OnTimer)
      #self.timer = wx.Timer(self, TIMERID)
      #self.timer.Start(250, False)

      #return True
#>>>>>>> Update for wxPython3.0 compatibility

      messenger.guiLaunchConnectionWindow()

      return True


   def chooseConnection(self, event = None):
      if self.currentWindow:
         self.currentWindow.Destroy()
      # TRANSLATORS: window title for server connection
      self.connectFrame = ConnectWindow(None, -1, _("London Law -- Connect to Server"), shutdown)
      self.connectFrame.Fit()
      self.connectFrame.Show(1)
      self.currentWindow = self.connectFrame
      wx.EVT_BUTTON(self.connectFrame, self.connectFrame.connectButton.GetId(), self.connect)
      return self.connectFrame


   def chooseGame(self, event = None):
      if self.currentWindow:
         self.currentWindow.Destroy()
      # TRANSLATORS: window title for game selection
      self.chooseGameFrame = GameListWindow(None, -1, _("London Law -- Choose a Game"), 
            messenger, shutdown)
      self.chooseGameFrame.SetSize((640, 480))
      self.chooseGameFrame.Show(1)
      self.currentWindow = self.chooseGameFrame
      return self.chooseGameFrame


   def register(self, event = None):
      if self.currentWindow:
         self.currentWindow.Destroy()
      # TRANSLATORS: window title for team selection
      self.registerFrame = RegistrationWindow(None, -1, _("London Law -- Team Selection"), 
            messenger, shutdown)
      self.registerFrame.Fit()
      self.registerFrame.SetSize((640, 480))
      self.registerFrame.Show(1)
      self.currentWindow = self.registerFrame
      return self.registerFrame


   def startGame(self, username, playerList, event = None):
      if self.currentWindow:
         self.currentWindow.Destroy()
      # TRANSLATORS: main window title
      self.mainFrame = MainWindow(None, -1, _("London Law"), username, playerList, 
            messenger, shutdown)
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
         self.connectFrame.status.PushStatusText(_("You must enter a valid hostname."))
         return
      elif len(port) < 1:
         self.connectFrame.status.PushStatusText(_("You must enter a valid port number."))
         return
      elif len(username) < 1:
         self.connectFrame.status.PushStatusText(_("You must enter a valid username."))
         return
      else:
         try:
            portNum = int(port)
         except:
            self.connectFrame.status.PushStatusText(_("The port number must be an integer."))
            return

         messenger.setUsername(username)
         messenger.setPassword(password)
         self.connectFrame.status.PushStatusText(_("Connecting to server..."))
         reactor.connectTCP(hostname, portNum, LLawClientFactory())



def init():
   reactor.startRunning()
   log.startLogging(sys.stderr, 0)
   app = MyApp(0)
   app.MainLoop()



# arch-tag: main loop for gui
