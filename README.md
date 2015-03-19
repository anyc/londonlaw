
London Law
----------

London Law is an online multiplayer adaptation of the [classic Scotland Yard
board game](http://www.boardgamegeek.com/boardgame/438/scotland-yard)
([Wikipedia](http://en.wikipedia.org/wiki/Scotland_Yard_board_game)).

This repository is based on a copy of the [last known pre-release](http://www.freelists.org/post/londonlaw-users/030-preview-release)
(0.3pre1) of [London Law](http://pessimization.com/software/londonlaw/) released
by the original author Paul Pelzl and contains additional patches to make this
game work with modern software.

Please note: I will not invest much time into development but patches are welcome.

Screenshot:
-----------

[![Screenshot](http://anyc.github.io/londonlaw/images/screenshot_thumb.jpg)](http://anyc.github.io/londonlaw/images/screenshot.jpg)

Dependencies:
-------------
* Python
* [Twisted](https://twistedmatrix.com)
* [wxPython](http://www.wxpython.org/)
* [zope-interface](https://pypi.python.org/pypi/zope.interface)

The code has been tested with the following versions:
* Python 2.7
* Twisted-13.0.0
* wxPython-3.0.1.1
* zope-interface-4.1.1


Changes
-------

0.3.0pre2:

   * wxPython3.0 compatibility by Olly Betts
   * Fix for newer python-twisted by Hans de Goede
   * Accept custom data directory by Mr Bones
   * More small fixes by Mario Kicherer

[0.3.0pre1 by Paul Pelzl](http://www.freelists.org/post/londonlaw-users/030-preview-release):

   * i18n.  Thanks to the efforts of numerous translators, there is
     at least partial support for 11 different languages.
   * AI clients.  Players can request an AI opponent while registering
     for a game.  At the moment there is only a pair of "Rather Dumb"
     AI clients available, meant as a proof of concept.
   * Admin client.  There is a text-mode admin client that can be used
     to delete games, eject players, etc.  It has an online help system,
     which is hopefully enough to explain the usage.

     The admin client won't work without setting up an admin password.
     Create a file called ~/.londonlaw/server/config that looks like
     this:

         [server]
         admin_password: PASSWORD
         game_expiration: 240

     Replace PASSWORD with whatever you want.  The game expiration is
     the number of hours after which stale games should be purged.
