#!/usr/bin/env python
#
# Distutils installation script for London Law
#
from distutils.core import setup
import os, string, sys


# Generate the binary translation files
if 'sdist' in sys.argv:
   os.system("cd londonlaw/locale && make mo")
   os.system("cd doc && make")


# Read off the PREFIX value, so we can tell londonlaw where to find its
# data files (FIXME: is there a clean way to handle this through distutils?)
if 'sdist' not in sys.argv and 'clean' not in sys.argv:
   DATA_PREFIX=os.path.normpath(sys.prefix)+"/share/"  # default
   for arg in sys.argv:
      index = string.find(arg, "--install-data=")
      if index > -1:
         DATA_PREFIX = os.path.normpath(arg[(index+len("--install-data=")):])

   config = open("londonlaw/common/config.py", "w")
   config.write("MEDIAROOT = \"" + os.path.join(DATA_PREFIX,"londonlaw/guiclient") + "\"\n")
   config.close()


# Append "dirname" and its datafiles to the list of files to install.
# This is called once per directory via os.path.walk().
def appendImageFiles(installList, dirname, files):
   newFiles = []
   for file in files:
      if file[-3:] != ".id" and file[-3:] != "=id":   # don't install Arch id files
         fullFile = os.path.join(dirname, file)
         if os.path.isfile(fullFile):
            newFiles.append(fullFile)
   if newFiles != []:
      splitDir = dirname.split('/')
      dirname = ('/').join(splitDir[1:])
      installList.append( (os.path.join(DATA_PREFIX, 'londonlaw', dirname), newFiles) )
      #installList.append( (dirname, newFiles) )


def appendMOFiles(installList, dirname, files):
   newFiles = []
   for file in files:
      if file[-3:] == ".mo":
         newFiles.append(os.path.join(dirname, file))
   if newFiles != []:
      splitDir = dirname.split('/')
      dirname = ('/').join(splitDir[1:])
      installList.append( (os.path.join(DATA_PREFIX, 'londonlaw', dirname), newFiles) )
      #installList.append( (dirname, newFiles) )


# Get all data files by walking through the proper directory trees
# and calling 'appendDataFiles'.
def getDataFilesList():
   installList = []
   os.path.walk('londonlaw/guiclient/images', appendImageFiles, installList)
   os.path.walk('londonlaw/locale', appendMOFiles, installList)
   return installList


# Run the distutils setup.
setup(name = "londonlaw",
   version = "0.3.0pre1",
   description = "networked multiplayer manhunting board game",
   author = "Paul J. Pelzl",
   author_email = "pelzlpj@eecs.umich.edu",
   maintainer = "Paul J. Pelzl",
   maintainer_email = "pelzlpj@eecs.umich.edu", 
   url = "http://www.eecs.umich.edu/~pelzlpj/londonlaw", 
   license = "GNU General Public License, Version 2",
   platforms = "*nix/X11, OS X, Win32",
   keywords = "Scotland Yard board game multiplayer",
   long_description = ( 
      "London Law is a networked multiplayer adaptation of the classic\n" +
      "Scotland Yard board game.  Mr. X must evade a number of detectives by\n" +
      "carefully concealing his movements across London.  One of only a\n" +
      "handful of asymmetric board games (Mr. X and the detectives have\n" +
      "different goals and abilities)." ),
   packages = [ 'londonlaw',                      # install all the .py files
                'londonlaw.common',
                'londonlaw.server',
                'londonlaw.guiclient',
                'londonlaw.aiclients',
                'londonlaw.adminclient'],
   scripts  = [ 'londonlaw/london-server',        # install the executable scripts
                'londonlaw/london-client',
                'londonlaw/london-admin'],
   data_files = getDataFilesList()                # install the game media and documentation
)


# Reset 'config.py' for the source distribution.
config = open("londonlaw/common/config.py", "w")
config.write("MEDIAROOT = \"guiclient\"\n")
config.close()