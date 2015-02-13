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




# MoveDialog.py
#
# This class generates a wx.Dialog that is used to choose a move (or double move).
# Drop-down boxes allow the player to choose from the possible moves.  The code
# is rather lengthy because the MoveDialog validates itself on-the-fly: that is,
# the transportation drop-down box always shows only transports that are available
# for the currently selected destionation, etc.

# FIXME: this appears to be correct, but needs some major cleanup.  Maybe some portions
#        can be factored better into functions.

import gettext, wx
from londonlaw.common.map import *



DIALOGDESTROYED = wx.NewEventType() 
 
def EVT_DIALOGDESTROYED(window, function): 
    """Your documentation here""" 
    window.Connect(-1, -1, DIALOGDESTROYED, function)
 
class DialogDestroyedEvent(wx.PyCommandEvent): 
    eventType = DIALOGDESTROYED
    def __init__(self, windowID): 
        wx.PyCommandEvent.__init__(self, self.eventType, windowID) 
 
    def Clone(self): 
        self.__class__(self.GetId()) 
 



class MoveDialog(wx.Dialog):
   # currPos is an integer indicating the current player position
   # destPos is a first choice destination, which the player probably
   #    chose by clicking on a map location
   # players is a list of locations and tokens for all players
   # playerIdx is the index if this player in that list
   # messenger passes messages to the network interface
   # destroyedCallback informs the parent that this dialog is destroyed
   # Use EVT_GOT_MOVE to catch the return values (insert derogatory comment about
   #    lack of flexibility in return values for wxDialog::EndModal())
   def __init__(self, parent, ID, destPos, playerList, playerIdx, messenger, destroyedCallback):
      wx.Dialog.__init__(self, parent, ID, _("Choose a Move"))
      self.parent = parent

      self.panel = wx.Panel(self, -1)

      self.playerIdx         = playerIdx
      self.playerList        = playerList
      self.currPos           = self.playerList[self.playerIdx][1]
      self.messenger         = messenger
      self.destroyedCallback = destroyedCallback

      # Mr. X gets the option of a double move
      if self.playerIdx == 0:
         # TRANSLATORS: this is a label for a choose box that lets the user select single or double move
         self.moveType = wx.RadioBox(self.panel, -1, _("move type: "), wx.DefaultPosition, wx.DefaultSize,
            # TRANSLATORS: as in "single move", not "double move"
            [_("Single"), 
            # TRANSLATORS: as in "double move", not "single move"
            _("Double")], 1, wx.RA_SPECIFY_ROWS)
         # If he has no double move tokens, then it's disabled
         if self.playerList[self.playerIdx][2][4] < 1:
            self.moveType.Enable(False)
      
      # TRANSLATORS: this is for the move selection dialog
      self.pos1Label = wx.StaticText(self.panel, -1, _("Move from %(number)d to ") % 
            {"number" : self.currPos}, wx.Point(0,0))
      # TRANSLATORS: this is for the move selection dialog: "move from 102 to 110 'using' taxi"
      self.trans1Label = wx.StaticText(self.panel, -1, _(" using "), wx.Point(0,0))

      self.moves, self.movesStr = self.getAvailMoves(self.currPos, self.playerList, self.playerIdx)
      self.dest1Box = wx.Choice(self.panel, -1, wx.DefaultPosition, wx.DefaultSize, self.movesStr)
      self.dest1Box.SetSelection(0)
      if destPos in self.moves:
         self.Show(True)
         for i in range(len(self.moves)):
            if self.moves[i] == destPos:
               self.dest1Box.SetSelection(i)
               break
      else:
         self.Show(False)
         if destPos != 0:
            self.drawMoveErrorDialog()
      

      self.trans1ID = wx.NewId()
      if len(self.moves) > 0:
         self.trans, self.transStr = self.getAvailTransports(self.currPos, self.moves[self.dest1Box.GetSelection()],
            self.playerList[self.playerIdx][2], self.playerIdx)
      else:
         self.trans    = []
         self.transStr = []
      self.trans1Box = wx.Choice(self.panel, self.trans1ID, wx.DefaultPosition, wx.DefaultSize, self.transStr)
      self.trans1Box.SetSelection(0)


      # double move options
      if self.playerIdx == 0:
         # TRANSLATORS: this is for the move selection dialog
         self.pos2Label = wx.StaticText(self.panel, -1, _("Move from %(number)s to ") %
               {"number" : self.dest1Box.GetStringSelection()}, wx.Point(0,0))
         # TRANSLATORS: this is for the move selection dialog: "move from 102 to 110 'using' taxi"
         self.trans2Label = wx.StaticText(self.panel, -1, _(" using "), wx.Point(0,0))

         # create a new playerList that has an updated location and list of tokens for Mr. X, assuming
         # that the first leg of the double move is complete.  This new list is required to figure out
         # which moves are available for the second leg.
         pl2 = []
         player = []
         player.append(self.playerList[0][0])
         if len(self.moves) > 0:
            player.append(self.moves[self.dest1Box.GetSelection()])
         tokenList = self.playerList[0][2][:]
         dummy = self.trans1Box.GetStringSelection()
         if dummy == _("black ticket"):
            tokenList[3] -= 1
         player.append(tokenList)
         pl2.append(player)
         for i in range(1, len(self.playerList)):
            pl2.append(self.playerList[i])

         self.dest2ID = wx.NewId()
         if len(self.moves) > 0:
            self.moves2, self.moves2Str = self.getAvailMoves(self.moves[self.dest1Box.GetSelection()], pl2, 0)
         else:
            self.moves2    = []
            self.moves2Str = []
         self.dest2Box = wx.Choice(self.panel, self.dest2ID, wx.DefaultPosition, wx.DefaultSize, self.moves2Str)
         self.dest2Box.SetSelection(0)

         self.trans2ID = wx.NewId()
         if len(self.moves) > 0 and len(self.moves2) > 0:
            self.trans2, self.trans2Str = self.getAvailTransports(self.moves[self.dest1Box.GetSelection()],
               self.moves2[self.dest2Box.GetSelection()], pl2[0][2], 0)
         else:
            self.trans2    = []
            self.trans2Str = []
         self.trans2Box = wx.Choice(self.panel, self.trans2ID, wx.DefaultPosition, wx.DefaultSize, self.trans2Str)
         self.trans2Box.SetSelection(0)

         self.move2Sizer = wx.BoxSizer(wx.HORIZONTAL)
         self.move2Sizer.Add(self.pos2Label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.ADJUST_MINSIZE, 5)
         self.move2Sizer.Add(self.dest2Box, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
         self.move2Sizer.Add(self.trans2Label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.ADJUST_MINSIZE, 5)
         self.move2Sizer.Add(self.trans2Box, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

         labelFont = wx.Font(self.GetFont().GetPointSize(), wx.DEFAULT, wx.NORMAL, wx.BOLD)
         labelFont.SetWeight(wx.BOLD)
         # TRANSLATORS: as in "move number one" (of multiple moves)
         self.move1Label = wx.StaticText(self.panel, -1, _("Move One:"))
         # TRANSLATORS: as in "move number two" (of multiple moves)
         self.move2Label = wx.StaticText(self.panel, -1, _("Move Two:"))
         self.move1Label.SetFont(labelFont)
         self.move2Label.SetFont(labelFont)

         if self.playerIdx == 0:
            self.move2Label.Enable(False)
         self.pos2Label.Enable(False)
         self.trans2Label.Enable(False)
         self.dest2Box.Enable(False)
         self.trans2Box.Enable(False)


      okButton = wx.Button(self.panel, wx.ID_OK, _("OK"))
      cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _("Cancel"))

      self.move1Sizer = wx.BoxSizer(wx.HORIZONTAL)
      self.move1Sizer.Add(self.pos1Label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.ADJUST_MINSIZE, 5)
      self.move1Sizer.Add(self.dest1Box, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
      self.move1Sizer.Add(self.trans1Label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.ADJUST_MINSIZE, 5)
      self.move1Sizer.Add(self.trans1Box, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

      buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
      buttonSizer.Add(cancelButton, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
      buttonSizer.Add(okButton, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

      self.pSizer = wx.BoxSizer(wx.VERTICAL)
      if self.playerIdx == 0:
         self.pSizer.Add(self.moveType, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
         self.pSizer.Add(self.move1Label, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP, 5)
         self.move1Sizer.Prepend((10,1),0,0)
      self.pSizer.Add(self.move1Sizer, 0, wx.ALIGN_CENTRE | wx.ALL | wx.ADJUST_MINSIZE, 5)
      if self.playerIdx == 0:
         self.pSizer.Add(self.move2Label, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP, 5)
         self.move2Sizer.Prepend((10,1),0,0)
         self.pSizer.Add(self.move2Sizer, 0, wx.ALIGN_CENTRE | wx.ALL | wx.ADJUST_MINSIZE, 5)
      self.pSizer.Add(buttonSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

      self.panel.SetSizer(self.pSizer)
      self.pSizer.Fit(self.panel)
      self.sizer = wx.BoxSizer(wx.VERTICAL)
      self.sizer.Add(self.panel, 1, wx.EXPAND | wx.ALL | wx.ADJUST_MINSIZE, 5)
      self.SetSizer(self.sizer)
      self.sizer.Fit(self)
      self.SetAutoLayout(1)

      self.dest1Box.SetFocus()

      wx.EVT_BUTTON(self, wx.ID_CANCEL, self.OnCancel)
      wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)
      wx.EVT_CHOICE(self, self.dest1Box.GetId(), self.updateTrans1)
      if self.playerIdx == 0:
         wx.EVT_CHOICE(self, self.dest2Box.GetId(), self.updateTrans2Evt)
         wx.EVT_RADIOBOX(self, self.moveType.GetId(), self.updateDouble)


   def drawMoveErrorDialog(self):
      if self.playerIdx == 0:
         message = _("Mr. X can't move to that location.")
      elif self.playerIdx == 1:
         message = _("The Red Detective can't move to that location.")
      elif self.playerIdx == 2:
         message = _("The Yellow Detective can't move to that location.")
      elif self.playerIdx == 3:
         message = _("The Green Detective can't move to that location.")
      elif self.playerIdx == 4:
         message = _("The Blue Detective can't move to that location.")
      elif self.playerIdx == 5:
         message = _("The Black Detective can't move to that location.")
      # TRANSLATORS: this is the title of an alert window that pops up when the user tries to make an illegal move
      alert = wx.MessageDialog(self.parent, message, _("Illegal Move"), wx.OK|wx.ICON_ERROR)
      alert.ShowModal()


   def setDest1(self, destPos):
      if destPos in self.moves:
         self.Show(True)
         for i in range(len(self.moves)):
            if self.moves[i] == destPos:
               self.dest1Box.SetSelection(i)
               self.updateTrans1(None)
               break
      elif destPos != 0:
         self.Show(False)
         self.drawMoveErrorDialog()


   def updateDouble(self, event):
      if self.moveType.GetSelection() == 0:
         self.move2Label.Enable(False)
         self.pos2Label.Enable(False)
         self.trans2Label.Enable(False)
         self.dest2Box.Enable(False)
         self.trans2Box.Enable(False)
      else:
         self.move2Label.Enable(True) 
         self.pos2Label.Enable(True)
         self.trans2Label.Enable(True)
         self.dest2Box.Enable(True)
         self.trans2Box.Enable(True)



   # after choosing a destination to move to, update the associated 
   # list of transportations
   def updateTrans1(self, event):
      if len(self.moves) > 0:
         self.trans, self.transStr = self.getAvailTransports(self.currPos, self.moves[self.dest1Box.GetSelection()],
            self.playerList[self.playerIdx][2], self.playerIdx)
      else:
         self.trans    = []
         self.transStr = []
      self.move1Sizer.Remove(self.trans1Box)
      self.trans1Box.Destroy()
      self.trans1Box = wx.Choice(self.panel, self.trans1ID, wx.DefaultPosition, wx.DefaultSize, self.transStr)
      self.trans1Box.SetSelection(0)
      self.move1Sizer.Add(self.trans1Box, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
      self.move1Sizer.Layout()
      self.updateDest2()


   def updateDest2(self):
      if self.playerIdx == 0:
         # TRANSLATORS: this is for the move selection dialog
         self.pos2Label.SetLabel(_("Move from %(number)s to ") % {"number" : self.dest1Box.GetStringSelection()})
         pl2 = []
         player = []
         player.append(self.playerList[0][0])
         if len(self.moves) > 0:
            player.append(self.moves[self.dest1Box.GetSelection()])
         tokenList = self.playerList[0][2][:]
         dummy = self.trans1Box.GetStringSelection()
         if dummy == _("taxi"):
            tokenList[0] -= 1
         elif dummy == _("bus"):
            tokenList[1] -= 1
         elif dummy == _("underground"):
            tokenList[2] -= 1
         elif dummy == _("black ticket"):
            tokenList[3] -= 1
         player.append(tokenList)
         pl2.append(player)
         for i in range(1, len(self.playerList)):
            pl2.append(self.playerList[i])

         if len(self.moves) > 0:
            self.moves2, self.moves2Str = self.getAvailMoves(self.moves[self.dest1Box.GetSelection()], pl2, 0)
         else:
            self.moves2    = []
            self.moves2Str = []
         self.move2Sizer.Remove(self.pos2Label)
         self.move2Sizer.Remove(self.dest2Box)
         self.dest2Box.Destroy()
         self.dest2Box = wx.Choice(self.panel, self.dest2ID, wx.DefaultPosition, wx.DefaultSize, self.moves2Str)
         self.dest2Box.SetSelection(0)
         if self.moveType.GetSelection() == 0:
            self.dest2Box.Enable(False)
         self.move2Sizer.Prepend(self.dest2Box, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
         self.move2Sizer.Prepend(self.pos2Label, 0, wx.ALIGN_CENTRE | wx.ALL | wx.ADJUST_MINSIZE, 5)
         self.updateTrans2()
      else:
         self.sizer.Layout()


   def updateTrans2Evt(self, event):
      self.updateTrans2()

   def updateTrans2(self):
      xtokens = self.playerList[0][2][:]
      dummy = self.trans1Box.GetStringSelection()
      if dummy == _("black ticket"):
         xtokens[3] -= 1

      if len(self.moves) > 0 and len(self.moves2) > 0:
         self.trans2, self.trans2Str = self.getAvailTransports(self.moves[self.dest1Box.GetSelection()],
            self.moves2[self.dest2Box.GetSelection()], xtokens, 0)
      else:
         self.trans2    = []
         self.trans2Str = []
      self.move2Sizer.Remove(self.trans2Box)
      self.trans2Box.Destroy()
      self.trans2Box = wx.Choice(self.panel, self.trans2ID, wx.DefaultPosition, wx.DefaultSize, self.trans2Str)
      self.trans2Box.SetSelection(0)
      if self.moveType.GetSelection() == 0:
         self.trans2Box.Enable(False)
      self.move2Sizer.Add(self.trans2Box, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
      self.move2Sizer.Layout()
      self.sizer.Layout()



   # cancelled the dialog
   def OnCancel(self, event):
      self.destroyedCallback()
      self.Destroy()


   def OnOK(self, event):
      index2PawnName = ["x", "red", "yellow", "green", "blue", "black"]
      move = [index2PawnName[self.playerIdx]]
      move.append(self.dest1Box.GetStringSelection())
      tstr = self.trans1Box.GetStringSelection()
      if tstr == _("taxi"):
         tret = "taxi"
      elif tstr == _("bus"):
         tret = "bus"
      elif tstr == _("underground"):
         tret = "underground"
      else:
         tret = "black"
      move.append(tret)

      if self.playerIdx == 0 and self.moveType.GetSelection() == 1:
         move.append(self.dest2Box.GetStringSelection())
         tstr = self.trans2Box.GetStringSelection()
         if tstr == _("taxi"):
            tret = "taxi"
         elif tstr == _("bus"):
            tret = "bus"
         elif tstr == _("underground"):
            tret = "underground"
         else:
            tret = "black"
         move.append(tret)

      self.messenger.netMakeMove(move) 
      self.destroyedCallback()
      self.Destroy()



   # Returns a tuple.  The first element is a list of integer available
   # moves, the second is the same list converted to strings.
   def getAvailMoves(self, pos, playerList, playerIdx):
      tokenList = playerList[playerIdx][2]

      # These are the positions that the player could get to using his current tokens,
      # if no detectives were in the way.
      movesFromMap = []
      for routes in locToRoutes[pos]:
         if playerIdx == 0: 
            # Mr. X can always take a route with standard transports (infinite tickets)
            if (TAXI in routes[1]) or (BUS in routes[1]) or \
            (UNDERGROUND in routes[1]):
               movesFromMap.append(routes[0])
            # Mr. X also has the option of black ticket moves
            elif tokenList[3] > 0: 
               movesFromMap.append(routes[0])
         else:
            # Detectives have to pay for everything
            if ((TAXI in routes[1] and tokenList[0] > 0) or
                (BUS in routes[1] and tokenList[1] > 0) or
                (UNDERGROUND in routes[1] and tokenList[2] > 0)):
               movesFromMap.append(routes[0])

      # Remove positions that a detective is on.
      detPositions = []
      for det in playerList[1:]:
         detPositions.append(det[1])

      availMoves = []
      for move in movesFromMap:
         if (move not in detPositions) or (playerIdx == 0):
            # this is to check that the player has at least one ticket type
            # that will get him to this destination; otherwise it is
            # effectively an illegal move
            transports, transportsStr = self.getAvailTransports(pos, move, tokenList, playerIdx)
            if transports != []:
               availMoves.append(move)

      availMoves.sort()
      availMovesStr = []
      for move in availMoves:
         availMovesStr.append(str(move))

      return availMoves, availMovesStr



   # Returns a tuple.  The first element is a list of integer available
   # transports (TAXI, BUS, etc.), the second is a more pleasant
   # string version.
   def getAvailTransports(self, pos, destPos, tokenList, playerIdx):
      routes = locToRoutes[pos]
      for route in routes:
         if route[0] == destPos:
            transports = route[1]
            break

      # Mr. X has another option
      if playerIdx == 0:
         if BLACK not in transports and tokenList[3] > 0:
            transports = transports + (BLACK,)

      transportsStr = []
      for trans in transports:
         if trans == TAXI and (tokenList[0] > 0 or tokenList[0] == -1):
            # TRANSLATORS: this is used for choosing ticket type in the move dialog
            transportsStr.append(_("taxi"))
         elif trans == BUS and (tokenList[1] > 0 or tokenList[1] == -1):
            # TRANSLATORS: this is used for choosing ticket type in the move dialog
            transportsStr.append(_("bus"))
         elif trans == UNDERGROUND and (tokenList[2] > 0 or tokenList[2] == -1):
            # TRANSLATORS: this is used for choosing ticket type in the move dialog
            transportsStr.append(_("underground"))
         elif trans == BLACK and (tokenList[3] > 0):
            # TRANSLATORS: this is used for choosing ticket type in the move dialog
            transportsStr.append(_("black ticket"))

      return transports, transportsStr



