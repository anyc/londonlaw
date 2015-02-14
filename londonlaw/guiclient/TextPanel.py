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




# TextPanel.py
#
# This class handles a wxStaticText drawn on a wxPanel.  The combination
# allows one to set both foreground and background colors, as well as
# borders around the window.

from wxPython.wx import *

# Generate a text label drawn on a wxPanel.
class TextPanel(wxPanel):
   def __init__(self, parent, text, points = 10, style = 0):
      wxPanel.__init__(self, parent, -1, wxDefaultPosition, wxDefaultSize, style)

      font = wxFont(points, wxDEFAULT, wxNORMAL, wxNORMAL)
      self.text = wxStaticText(self, -1, text, wxPoint(0,0))
      self.text.SetFont(font)

      self.sizer = wxBoxSizer(wxVERTICAL)
      self.sizer.Add((0, 0), 1, wxEXPAND)
      self.sizer.Add(self.text, 0, wxALIGN_CENTRE|wxADJUST_MINSIZE)
      self.sizer.Add((0, 0), 1, wxEXPAND)
      self.SetSizer(self.sizer)
      self.sizer.SetSizeHints(self)

   def SetText(self, text):
      self.text.SetLabel(text)
      txtsize = self.text.GetSize()
      self.sizer.SetMinSize(txtsize)

   def SetForegroundColour(self, color):
      self.text.SetForegroundColour(color)
      wxPanel.SetForegroundColour(self, color)

   # def SetBackgroundColour(self, color)
   # (this function falls through to call SetBackgroundColour on the wxPanel)
   def SetBackgroundColour(self, color):
      self.text.SetBackgroundColour(color)
      wxPanel.SetBackgroundColour(self, color)
   


# arch-tag: text panel for gui
