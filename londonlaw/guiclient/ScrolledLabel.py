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




# ScrolledLabel.py
#
# This class handles a wxStaticText that is managed by a scrolled window.


from wxPython.wx import *

class ScrolledLabel(wxScrolledWindow):
   def __init__(self, parent, label):
      wxScrolledWindow.__init__(self, parent, -1, wxDefaultPosition, wxDefaultSize, 
         wxVSCROLL | wxSIMPLE_BORDER)
      self.SetBackgroundColour(wxColour(200, 200, 200))
      self.SetScrollRate(0, 5)

      # create the text that will be scrolled
      self.text = wxStaticText(self, -1, label, wxPoint(0,0))

      # use a Sizer to handle geometry
      self.topSizer = wxBoxSizer(wxVERTICAL)
      self.topSizer.Add(self.text, 1, wxEXPAND)
      self.SetSizer(self.topSizer)
      self.topSizer.SetVirtualSizeHints(self)

      self.ScrollToEnd()

   def SetText(self, text):
      self.text.SetLabel(text)

      # force the sizer to readjust to the new text, so the scroll bars
      # will properly cover the entire region
      txtsize = self.text.GetSize()
      self.topSizer.SetMinSize(txtsize)
      self.ScrollToEnd()

   def AppendText(self, txt):
      self.text.SetLabel(self.text.GetLabel() + '\n' + txt)

      txtsize = self.text.GetSize()
      self.topSizer.SetMinSize(txtsize)
      self.ScrollToEnd()



   # scroll to the bottom of the text
   def ScrollToEnd(self):
      self.topSizer.SetVirtualSizeHints(self)
      self.Scroll(0, self.GetVirtualSize()[1]/5)


# arch-tag: scrolled label for gui chat
