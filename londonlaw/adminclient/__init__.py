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


from twisted.internet import protocol, reactor
from twisted.python import log
import sys
from optparse import OptionParser
from londonlaw.adminclient.Protocol import *


class AdminClientFactory(protocol.ClientFactory):
   protocol = AdminClientProtocol

   def __init__(self, password):
      self._password = password

   def registerProtocol(self, p):
      p._password = self._password

   def clientConnectionFailed(self, connector, reason):
      print "Unable to connect to server."
      reactor.stop()


def init():
   # Parse command-line options
   usage = "usage: london-admin [options] password"
   parser = OptionParser(usage)
   parser.add_option("-s", "--server", dest="host",
         help="connect to server on host SERVER", metavar="SERVER",
         default="localhost")
   parser.add_option("-p", "--port", dest="port",
         help="connect to server on port NUM", metavar="NUM", default=str(LLAW_PORT))
   (options, args) = parser.parse_args()

   if len(args) < 1:
      print usage
   else:
      log.startLogging(sys.stdout, 0)
      reactor.connectTCP(options.host, int(options.port), AdminClientFactory(args[0]))
      reactor.run()



