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


from twisted.internet import protocol, reactor, task
from twisted.python import log
from londonlaw.common.protocol import *
from Protocol import LLawServerProtocol
from optparse import OptionParser
import GameRegistry
import sys, gettext



class LLawServerFactory(protocol.ServerFactory):
   protocol = LLawServerProtocol
   

def init():
   # Parse command-line options
   parser = OptionParser()
   parser.add_option("-p", "--port", dest="port",
         help=_("listen for connections on port NUM"), metavar=_("NUM"), default=str(LLAW_PORT))
   (options, args) = parser.parse_args()

   log.startLogging(sys.stdout, 0)

   registry = GameRegistry.getHandle()
   # Purge expired games every half hour
   gameKiller = task.LoopingCall(registry.purgeExpiredGames)
   gameKiller.start(1800)
   # Purge games involving AI clients
   registry.purgeBotGames()

   reactor.listenTCP(int(options.port), LLawServerFactory())
   reactor.run()

   registry.close()


# arch-tag: DO_NOT_CHANGE_9d2015c7-8192-4a96-979d-c2c2f84aecd3 
