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




# PlayerIcon.py
#
# These classes handle display of a set of icons that show the player status.
# There are captions for names and readouts of the available tokens.
# Status icons can be overlaid on the player icons to show whose turn it is, etc.

from wxPython.wx import *
from TextPanel import *
from StaticBitmap import *
from londonlaw.common.config import *
import os


# draw an icon to represent a player, with a caption for the name and a
# readout of the available tokens.
# expects a list of three tokens (taxi, bus, undergnd) or a list of five
# tokens (taxi, bus, undergnd, black, double)
class PlayerIcon(wxPanel):
   def __init__(self, parent, imagefile, thinkingimagefile, stuckimagefile, 
            name, tokenList, isMrX = False):
      wxPanel.__init__(self, parent, -1) #wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)

      self.iconPanel = wxPanel(self, -1)
      self.isStuck   = False
      self.isMrX     = isMrX

      # load the image
      iconImage = wxImage(imagefile, wxBITMAP_TYPE_ANY)
      # we need an extra copy of the player icon, so we can blit to one of them in memory
      self.playerBitmap = wxBitmapFromImage(iconImage)
      self.iconBitmap   = wxBitmapFromImage(iconImage)
      self.iconBitmap2  = wxBitmapFromImage(iconImage)
      self.icon = StaticBitmap(self.iconPanel, -1, self.iconBitmap)

      # load the overlay image for the "I'm thinking" question mark
      thinkingImage = wxImage(thinkingimagefile, wxBITMAP_TYPE_ANY)
      thinkingImage.SetMaskColour(255, 0, 242) # the purplish colour is not to be drawn
      self.thinkingBitmap = wxBitmapFromImage(thinkingImage)

      # load the overlay image for the "I'm stuck" stop sign
      stuckImage = wxImage(stuckimagefile, wxBITMAP_TYPE_ANY)
      stuckImage.SetMaskColour(255, 0, 242) # the purplish colour is not to be drawn
      self.stuckBitmap = wxBitmapFromImage(stuckImage)

      iconSizer = wxBoxSizer(wxVERTICAL)
      iconSizer.Add(self.icon, 0, wxADJUST_MINSIZE)
      self.iconPanel.SetSizer(iconSizer)
      iconSizer.Fit(self.iconPanel)


      # create the caption
      self.caption = TextPanel(self, " "+name[:20]+" ", 10, wxSIMPLE_BORDER)#|wxALIGN_CENTRE

      # create the inventory labels
      if self.isMrX:
         self.blackLabel = TextPanel(self, " "+`tokenList[3]`+" ", 10, wxEXPAND)
         self.blackLabel.SetBackgroundColour(wxColour(0,0,0))
         self.blackLabel.SetForegroundColour(wxColour(255,255,255))
         self.doubleLabel = TextPanel(self, " "+`tokenList[4]`+" ", 10, wxEXPAND)
         self.doubleLabel.SetBackgroundColour(wxColour(255,84,166))
      else:
         self.taxiLabel = TextPanel(self, " "+`tokenList[0]`+" ", 10, wxEXPAND)
         self.taxiLabel.SetBackgroundColour(wxColour(255, 191, 0))
         self.busLabel = TextPanel(self, " "+`tokenList[1]`+" ", 10, wxEXPAND)
         self.busLabel.SetBackgroundColour(wxColour(7, 155, 0))
         self.ugndLabel = TextPanel(self, " "+`tokenList[2]`+" ", 10, wxEXPAND)
         self.ugndLabel.SetBackgroundColour(wxColour(160, 36, 96))
         self.ugndLabel.SetForegroundColour(wxColour(255, 255, 255))

      # stack the inventory labels vertically
      self.invSizer = wxBoxSizer(wxVERTICAL)
      if self.isMrX:
         self.invSizer.Add(self.blackLabel, 1, wxEXPAND|wxADJUST_MINSIZE)
         self.invSizer.Add(self.doubleLabel, 1, wxEXPAND|wxADJUST_MINSIZE)
      else:
         self.invSizer.Add(self.taxiLabel, 1, wxEXPAND|wxADJUST_MINSIZE)
         self.invSizer.Add(self.busLabel, 1, wxEXPAND|wxADJUST_MINSIZE)
         self.invSizer.Add(self.ugndLabel, 1, wxEXPAND|wxADJUST_MINSIZE)

      # group the icon with the inventory
      iconInvSizer = wxBoxSizer(wxHORIZONTAL)
      iconInvSizer.Add(self.iconPanel, 0, wxALIGN_TOP|wxADJUST_MINSIZE)
      iconInvSizer.Add(self.invSizer, 0, wxALIGN_TOP|wxADJUST_MINSIZE)

      # put the caption under the bitmap and inventory lists
      self.topSizer = wxBoxSizer(wxVERTICAL)
      self.topSizer.Add(iconInvSizer, 0, wxEXPAND|wxLEFT|wxRIGHT|wxADJUST_MINSIZE, 20)
      self.topSizer.Add(self.caption, 0, wxEXPAND|wxALIGN_CENTRE|wxALL, 2)
      self.SetSizer(self.topSizer)
      self.topSizer.SetSizeHints(self)

      self.iconDC = wxMemoryDC()
      self.srcDC  = wxMemoryDC()


   def updateTokens(self, tokenList):
      if self.isMrX:
         self.blackLabel.SetText(" "+`tokenList[3]`+" ")
         self.doubleLabel.SetText(" "+`tokenList[4]`+" ")
      else:
         self.taxiLabel.SetText(" "+`tokenList[0]`+" ")
         self.busLabel.SetText(" "+`tokenList[1]`+" ")
         self.ugndLabel.SetText(" "+`tokenList[2]`+" ")
      self.invSizer.Layout()


   def setTurn(self):
      self.srcDC.SelectObject(self.playerBitmap)
      self.iconDC.SelectObject(self.iconBitmap2)
      self.iconDC.BeginDrawing()
      self.iconDC.Blit(0, 0, self.iconBitmap.GetWidth(), self.iconBitmap.GetHeight(),
            self.srcDC, 0, 0)
      self.srcDC.SelectObject(self.thinkingBitmap)
      self.iconDC.Blit(0, 0, self.iconBitmap.GetWidth(), self.iconBitmap.GetHeight(),
            self.srcDC, 0, 0, wxCOPY, TRUE)
      self.iconDC.EndDrawing()
      self.iconDC.SelectObject(wxNullBitmap)
      temp             = self.iconBitmap
      self.iconBitmap  = self.iconBitmap2
      self.iconBitmap2 = temp
      self.icon.SetBitmap(self.iconBitmap)
      self.icon.Refresh(FALSE)
      self.isStuck = False


   def setStuck(self):
      self.srcDC.SelectObject(self.playerBitmap)
      self.iconDC.SelectObject(self.iconBitmap2)
      self.iconDC.BeginDrawing()
      self.iconDC.Blit(0, 0, self.iconBitmap.GetWidth(), self.iconBitmap.GetHeight(),
            self.srcDC, 0, 0)
      self.srcDC.SelectObject(self.stuckBitmap)
      self.iconDC.Blit(0, 0, self.iconBitmap.GetWidth(), self.iconBitmap.GetHeight(),
            self.srcDC, 0, 0, wxCOPY, TRUE)
      self.iconDC.EndDrawing()
      self.iconDC.SelectObject(wxNullBitmap)
      temp             = self.iconBitmap
      self.iconBitmap  = self.iconBitmap2
      self.iconBitmap2 = temp
      self.icon.SetBitmap(self.iconBitmap)
      self.icon.Refresh(FALSE)
      self.isStuck = True


   def clearOverlay(self):
      self.srcDC.SelectObject(self.playerBitmap)
      self.iconDC.SelectObject(self.iconBitmap2)
      self.iconDC.BeginDrawing()
      self.iconDC.Blit(0, 0, self.iconBitmap.GetWidth(), self.iconBitmap.GetHeight(),
            self.srcDC, 0, 0)
      self.iconDC.EndDrawing()
      self.iconDC.SelectObject(wxNullBitmap)
      temp             = self.iconBitmap
      self.iconBitmap  = self.iconBitmap2
      self.iconBitmap2 = temp
      self.icon.SetBitmap(self.iconBitmap)
      self.icon.Refresh(FALSE)



# Manage a group of icons to represent all six players.
class PlayerIconGroup(wxPanel):
   def __init__(self, parent, nameList, tokenList):
      wxPanel.__init__(self, parent, -1)

      # Get icons for all the players
      if len(nameList) != 6:
         sys.exit("PlayerIconGroup must be called with len(nameList) == 6\n" +
            "(here it was called with length "+`len(nameList)`+")")
      
      self.players = [PlayerIcon(self, 
         os.path.normpath(os.path.join(MEDIAROOT, "images/playericon0.jpg")),
         os.path.normpath(os.path.join(MEDIAROOT, "images/thinking.png")), 
         os.path.normpath(os.path.join(MEDIAROOT, "images/stuck.png")), 
         nameList[0], tokenList[0], True)]
      for i in range(1, 6):
         filename = os.path.normpath(os.path.join(MEDIAROOT, "images/playericon" + str(i) + ".jpg"))
         self.players.append(PlayerIcon(self, filename,
            os.path.normpath(os.path.join(MEDIAROOT, "images/thinking.png")), 
            os.path.normpath(os.path.join(MEDIAROOT, "images/stuck.png")), 
            nameList[i], tokenList[i]))


      self.topSizer = wxBoxSizer(wxHORIZONTAL)
      for p in self.players:
         self.topSizer.Add(p, 0, wxALIGN_CENTRE) 
      self.SetSizer(self.topSizer)
      self.topSizer.SetSizeHints(self)


   # update the icons to show whose turn it is
   def setTurn(self, index):
      for i in range(6):
         if i == index:
            self.isStuck = False
            self.players[i].setTurn()
         else:
            if not self.players[i].isStuck:
               self.players[i].clearOverlay()


   # update the icons to show someone is stuck
   def setStuck(self, index):
      self.players[index].setStuck()



# arch-tag: player icon
