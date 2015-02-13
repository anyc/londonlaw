#!/usr/bin/env python
#
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

# Command-line launcher for x_simple AI.  Use it like
# $ python x_simple_launcher.py "gameroom name" PORT
# (where PORT is optional, defaulting to the obvious choice)
#
# The gameroom name should be encoded using UTF-8.


from twisted.internet import reactor
from twisted.python import log
import sys, os


# add the parent directories to PYTHONPATH
sys.path.append(os.getcwd())
parent = os.path.split(os.path.abspath(os.getcwd()))[0]
root   = os.path.split(os.path.abspath(parent))[0]
sys.path.append(parent)
sys.path.append(root)
from londonlaw.aiclients import x_simple
from londonlaw.common.protocol import LLAW_PORT


log.startLogging(sys.stderr, 0)
if len(sys.argv) > 3:
   port = int(sys.argv[3])
else:
   port = LLAW_PORT
log.msg("Using server at localhost port " + str(port))
log.msg("Sending simple AI client \"" + sys.argv[1] + "\" to game room \"" + sys.argv[2] + "\"")

f = x_simple.XSimpleAIFactory(sys.argv[1].decode("utf-8"), sys.argv[2].decode("utf-8"))
reactor.connectTCP("localhost", port, f)
reactor.run()



