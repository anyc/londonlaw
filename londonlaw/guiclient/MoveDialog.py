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




# MoveDialog.py
#
# This class generates a wxDialog that is used to choose a move (or double move).
# Drop-down boxes allow the player to choose from the possible moves.  The code
# is rather lengthy because the MoveDialog validates itself on-the-fly: that is,
# the transportation drop-down box always shows only transports that are available
# for the currently selected destionation, etc.

# FIXME: this appears to be correct, but needs some major cleanup.  Maybe some portions
#        can be factored better into functions.

from wxPython.wx import *
from londonlaw.common.map import *



DIALOGDESTROYED = wxNewEventType() 
 
def EVT_DIALOGDESTROYED(window, function): 
    """Your documentation here""" 
    window.Connect(-1, -1, DIALOGDESTROYED, function)
 
class DialogDestroyedEvent(wxPyCommandEvent): 
    eventType = DIALOGDESTROYED
    def __init__(self, windowID): 
        wxPyCommandEvent.__init__(self, self.eventType, windowID) 
 
    def Clone(self): 
        self.__class__(self.GetId()) 
 



class MoveDialog(wxDialog):
   # currPos is an integer indicating the current player position
   # destPos is a first choice destination, which the player probably
   #    chose by clicking on a map location
   # players is a list of locations and tokens for all players
   # playerIdx is the index if this player in that list
   # Use EVT_GOT_MOVE to catch the return values (insert derogatory comment about
   #    lack of flexibility in return values for wxDialog::EndModal())
   def __init__(self, parent, ID, destPos, playerList, playerIdx, messenger):
      wxDialog.__init__(self, parent, ID, "Choose a Move")
      self.parent = parent

      self.panel = wxPanel(self, -1)

      self.playerIdx  = playerIdx
      self.playerList = playerList
      self.currPos    = self.playerList[self.playerIdx][1]
      self.messenger  = messenger

      # Mr. X gets the option of a double move
      if self.playerIdx == 0:
         self.moveType = wxRadioBox(self.panel, -1, "move type: ", wxDefaultPosition, wxDefaultSize,
            ["Single", "Double"], 1, wxRA_SPECIFY_ROWS)
         # If he has no double move tokens, then it's disabled
         if self.playerList[self.playerIdx][2][4] < 1:
            self.moveType.Enable(false)
      
      self.pos1Label = wxStaticText(self.panel, -1, "Move from "+`self.currPos`+" to ", wxPoint(0,0))
      self.trans1Label = wxStaticText(self.panel, -1, " using ", wxPoint(0,0))

      self.moves, self.movesStr = self.getAvailMoves(self.currPos, self.playerList, self.playerIdx)
      self.dest1Box = wxChoice(self.panel, -1, wxDefaultPosition, wxDefaultSize, self.movesStr)
      self.dest1Box.SetSelection(0)
      if destPos in self.moves:
         self.Show(TRUE)
         for i in range(len(self.moves)):
            if self.moves[i] == destPos:
               self.dest1Box.SetSelection(i)
               break
      else:
         self.Show(FALSE)
         if destPos != 0:
            self.drawMoveErrorDialog()
      

      self.trans1ID = wxNewId()
      self.trans, self.transStr = self.getAvailTransports(self.currPos, self.moves[self.dest1Box.GetSelection()],
         self.playerList[self.playerIdx][2], self.playerIdx)
      self.trans1Box = wxChoice(self.panel, self.trans1ID, wxDefaultPosition, wxDefaultSize, self.transStr)
      self.trans1Box.SetSelection(0)


      # double move options
      if self.playerIdx == 0:
         self.pos2Label = wxStaticText(self.panel, -1, "Move from "+self.dest1Box.GetStringSelection()+" to ", wxPoint(0,0))
         self.trans2Label = wxStaticText(self.panel, -1, " using ", wxPoint(0,0))

         # create a new playerList that has an updated location and list of tokens for Mr. X, assuming
         # that the first leg of the double move is complete.  This new list is required to figure out
         # which moves are available for the second leg.
         pl2 = []
         player = []
         player.append(self.playerList[0][0])
         player.append(self.moves[self.dest1Box.GetSelection()])
         tokenList = self.playerList[0][2][:]
         dummy = self.trans1Box.GetStringSelection()
         if dummy == "black ticket":
            tokenList[3] -= 1
         player.append(tokenList)
         pl2.append(player)
         for i in range(1, len(self.playerList)):
            pl2.append(self.playerList[i])

         self.dest2ID = wxNewId()
         self.moves2, self.moves2Str = self.getAvailMoves(self.moves[self.dest1Box.GetSelection()], pl2, 0)
         self.dest2Box = wxChoice(self.panel, self.dest2ID, wxDefaultPosition, wxDefaultSize, self.moves2Str)
         self.dest2Box.SetSelection(0)

         self.trans2ID = wxNewId()
         self.trans2, self.trans2Str = self.getAvailTransports(self.moves[self.dest1Box.GetSelection()],
            self.moves2[self.dest2Box.GetSelection()], pl2[0][2], 0)
         self.trans2Box = wxChoice(self.panel, self.trans2ID, wxDefaultPosition, wxDefaultSize, self.trans2Str)
         self.trans2Box.SetSelection(0)

         self.move2Sizer = wxBoxSizer(wxHORIZONTAL)
         self.move2Sizer.Add(self.pos2Label, 0, wxALIGN_CENTRE | wxALL | wxADJUST_MINSIZE, 5)
         self.move2Sizer.Add(self.dest2Box, 0, wxALIGN_CENTRE | wxALL, 5)
         self.move2Sizer.Add(self.trans2Label, 0, wxALIGN_CENTRE | wxALL | wxADJUST_MINSIZE, 5)
         self.move2Sizer.Add(self.trans2Box, 0, wxALIGN_CENTRE | wxALL, 5)

         labelFont = wxFont(self.GetFont().GetPointSize(), wxDEFAULT, wxNORMAL, wxBOLD)
         labelFont.SetWeight(wxBOLD)
         self.move1Label = wxStaticText(self.panel, -1, "Move One:")
         self.move2Label = wxStaticText(self.panel, -1, "Move Two:") 
         self.move1Label.SetFont(labelFont)
         self.move2Label.SetFont(labelFont)

         if self.playerIdx == 0:
            self.move2Label.Enable(false)
         self.pos2Label.Enable(false)
         self.trans2Label.Enable(false)
         self.dest2Box.Enable(false)
         self.trans2Box.Enable(false)


      okButton = wxButton(self.panel, wxID_OK, "OK")
      cancelButton = wxButton(self.panel, wxID_CANCEL, "Cancel")

      self.move1Sizer = wxBoxSizer(wxHORIZONTAL)
      self.move1Sizer.Add(self.pos1Label, 0, wxALIGN_CENTRE | wxALL | wxADJUST_MINSIZE, 5)
      self.move1Sizer.Add(self.dest1Box, 0, wxALIGN_CENTRE | wxALL, 5)
      self.move1Sizer.Add(self.trans1Label, 0, wxALIGN_CENTRE | wxALL | wxADJUST_MINSIZE, 5)
      self.move1Sizer.Add(self.trans1Box, 0, wxALIGN_CENTRE | wxALL, 5)

      buttonSizer = wxBoxSizer(wxHORIZONTAL)
      buttonSizer.Add(cancelButton, 0, wxALIGN_CENTRE | wxALL, 5)
      buttonSizer.Add(okButton, 0, wxALIGN_CENTRE | wxALL, 5)

      self.pSizer = wxBoxSizer(wxVERTICAL)
      if self.playerIdx == 0:
         self.pSizer.Add(self.moveType, 0, wxALIGN_CENTRE | wxALL, 5)
         self.pSizer.Add(self.move1Label, 0, wxALIGN_LEFT | wxLEFT | wxTOP, 5)
         self.move1Sizer.Prepend((10,1),0,0)
      self.pSizer.Add(self.move1Sizer, 0, wxALIGN_CENTRE | wxALL | wxADJUST_MINSIZE, 5)
      if self.playerIdx == 0:
         self.pSizer.Add(self.move2Label, 0, wxALIGN_LEFT | wxLEFT | wxTOP, 5)
         self.move2Sizer.Prepend((10,1),0,0)
         self.pSizer.Add(self.move2Sizer, 0, wxALIGN_CENTRE | wxALL | wxADJUST_MINSIZE, 5)
      self.pSizer.Add(buttonSizer, 0, wxALIGN_RIGHT | wxALL, 5)

      self.panel.SetSizer(self.pSizer)
      self.pSizer.Fit(self.panel)
      self.sizer = wxBoxSizer(wxVERTICAL)
      self.sizer.Add(self.panel, 1, wxEXPAND | wxALL | wxADJUST_MINSIZE, 5)
      self.SetSizer(self.sizer)
      self.sizer.Fit(self)
      self.SetAutoLayout(1)

      self.dest1Box.SetFocus()

      EVT_BUTTON(self, wxID_CANCEL, self.OnCancel)
      EVT_BUTTON(self, wxID_OK, self.OnOK)
      EVT_CHOICE(self, self.dest1Box.GetId(), self.updateTrans1)
      if self.playerIdx == 0:
         EVT_CHOICE(self, self.dest2Box.GetId(), self.updateTrans2Evt)
         EVT_RADIOBOX(self, self.moveType.GetId(), self.updateDouble)


   def drawMoveErrorDialog(self):
      if self.playerIdx == 0:
         prefix = "Mr. X"
      elif self.playerIdx == 1:
         prefix = "The Red Detective"
      elif self.playerIdx == 2:
         prefix = "The Yellow Detective"
      elif self.playerIdx == 3:
         prefix = "The Green Detective"
      elif self.playerIdx == 4:
         prefix = "The Blue Detective"
      elif self.playerIdx == 5:
         prefix = "The Black Detective"
      alert = wxMessageDialog(self.parent, prefix + " can't move to that location.", "Illegal Move", wxOK|wxICON_ERROR)
      alert.ShowModal()


   def setDest1(self, destPos):
      if destPos in self.moves:
         self.Show(TRUE)
         for i in range(len(self.moves)):
            if self.moves[i] == destPos:
               self.dest1Box.SetSelection(i)
               self.updateTrans1(None)
               break
      elif destPos != 0:
         self.drawMoveErrorDialog()


   def updateDouble(self, event):
      if self.moveType.GetSelection() == 0:
         self.move2Label.Enable(false)
         self.pos2Label.Enable(false)
         self.trans2Label.Enable(false)
         self.dest2Box.Enable(false)
         self.trans2Box.Enable(false)
      else:
         self.move2Label.Enable(true) 
         self.pos2Label.Enable(true)
         self.trans2Label.Enable(true)
         self.dest2Box.Enable(true)
         self.trans2Box.Enable(true)



   # after choosing a destination to move to, update the associated 
   # list of transportations
   def updateTrans1(self, event):
      self.trans, self.transStr = self.getAvailTransports(self.currPos, self.moves[self.dest1Box.GetSelection()],
         self.playerList[self.playerIdx][2], self.playerIdx)
      self.move1Sizer.Remove(self.trans1Box)
      self.trans1Box.Destroy()
      self.trans1Box = wxChoice(self.panel, self.trans1ID, wxDefaultPosition, wxDefaultSize, self.transStr)
      self.trans1Box.SetSelection(0)
      self.move1Sizer.Add(self.trans1Box, 0, wxALIGN_CENTRE | wxALL, 5)
      self.move1Sizer.Layout()
      self.updateDest2()


   def updateDest2(self):
      if self.playerIdx == 0:
         self.pos2Label.SetLabel("Move from "+self.dest1Box.GetStringSelection()+" to ")
         pl2 = []
         player = []
         player.append(self.playerList[0][0])
         player.append(self.moves[self.dest1Box.GetSelection()])
         tokenList = self.playerList[0][2][:]
         dummy = self.trans1Box.GetStringSelection()
         if dummy == "taxi":
            tokenList[0] -= 1
         elif dummy == "bus":
            tokenList[1] -= 1
         elif dummy == "underground":
            tokenList[2] -= 1
         elif dummy == "black ticket":
            tokenList[3] -= 1
         player.append(tokenList)
         pl2.append(player)
         for i in range(1, len(self.playerList)):
            pl2.append(self.playerList[i])

         self.moves2, self.moves2Str = self.getAvailMoves(self.moves[self.dest1Box.GetSelection()], pl2, 0)
         self.move2Sizer.Remove(self.pos2Label)
         self.move2Sizer.Remove(self.dest2Box)
         self.dest2Box.Destroy()
         self.dest2Box = wxChoice(self.panel, self.dest2ID, wxDefaultPosition, wxDefaultSize, self.moves2Str)
         self.dest2Box.SetSelection(0)
         if self.moveType.GetSelection() == 0:
            self.dest2Box.Enable(false)
         self.move2Sizer.Prepend(self.dest2Box, 0, wxALIGN_CENTRE | wxALL, 5)
         self.move2Sizer.Prepend(self.pos2Label, 0, wxALIGN_CENTRE | wxALL | wxADJUST_MINSIZE, 5)
         self.updateTrans2()
      else:
         self.sizer.Layout()


   def updateTrans2Evt(self, event):
      self.updateTrans2()

   def updateTrans2(self):
      xtokens = self.playerList[0][2][:]
      dummy = self.trans1Box.GetStringSelection()
      if dummy == "black ticket":
         xtokens[3] -= 1

      self.trans2, self.trans2Str = self.getAvailTransports(self.moves[self.dest1Box.GetSelection()],
         self.moves2[self.dest2Box.GetSelection()], xtokens, 0)
      self.move2Sizer.Remove(self.trans2Box)
      self.trans2Box.Destroy()
      self.trans2Box = wxChoice(self.panel, self.trans2ID, wxDefaultPosition, wxDefaultSize, self.trans2Str)
      self.trans2Box.SetSelection(0)
      if self.moveType.GetSelection() == 0:
         self.trans2Box.Enable(false)
      self.move2Sizer.Add(self.trans2Box, 0, wxALIGN_CENTRE | wxALL, 5)
      self.move2Sizer.Layout()
      self.sizer.Layout()



   # cancelled the dialog
   def OnCancel(self, event):
      event  = DialogDestroyedEvent(self.GetId())
      result = self.GetEventHandler().ProcessEvent(event)
      self.Destroy()


   def OnOK(self, event):
      index2PawnName = ["x", "red", "yellow", "green", "blue", "black"]
      move = [index2PawnName[self.playerIdx]]
      move.append(self.dest1Box.GetStringSelection())
      tstr = self.trans1Box.GetStringSelection()
      if tstr == "black ticket":
         tret = "black"
      else:
         tret = tstr
      move.append(tret)

      if self.playerIdx == 0 and self.moveType.GetSelection() == 1:
         move.append(self.dest2Box.GetStringSelection())
         tstr = self.trans2Box.GetStringSelection()
         if tstr == "black ticket":
            tret = "black"
         else:
            tret = tstr
         move.append(tret)

      self.messenger.netMakeMove(move) 
      event  = DialogDestroyedEvent(self.GetId())
      result = self.GetEventHandler().ProcessEvent(event)
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
            if ((TAXI in routes[1] and tokenList[0] > 0) or
                (BUS in routes[1] and tokenList[1] > 0) or
                (UNDERGROUND in routes[1] and tokenList[2] > 0) or
                (tokenList[3] > 0)):  # Mr. X can make black ticket moves too
               movesFromMap.append(routes[0])
         else:
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
            transportsStr.append("taxi")
         elif trans == BUS and (tokenList[1] > 0 or tokenList[1] == -1):
            transportsStr.append("bus")
         elif trans == UNDERGROUND and (tokenList[2] > 0 or tokenList[2] == -1):
            transportsStr.append("underground")
         elif trans == BLACK and (tokenList[3] > 0):
            transportsStr.append("black ticket")

      return transports, transportsStr



# arch-tag: move dialog
