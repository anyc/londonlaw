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



from wxPython.wx import *
from utility import *
from SetHash import *
from londonlaw.common.config import *
import os


MAPSIZE = (2036, 1618)

# these are upper-left pixel locations of the map number graphics, indexed by map number
pixelTable = \
            ( None,  # No value for location 0; use location 1-199
               (175, 79),
               (504, 18),
               (780, 33),
               (931, 41),
               (1506, 60),    # 005
               (1676, 68),
               (1858, 41),
               (121, 200),
               (277, 196),
               (686, 173),    # 010
               (784, 165),
               (870, 157),
               (1044, 171),
               (1213, 119),
               (1355, 106),   # 015
               (1543, 173),
               (1840, 225),
               (52, 261),
               (191, 280),
               (358, 234),    # 020
               (535, 297),
               (805, 316),
               (933, 244),
               (1145, 238),
               (1241, 257),   # 025
               (1370, 170),
               (1379, 239),
               (1457, 223),
               (1676, 258),
               (1955, 276),   # 030
               (98, 320),
               (286, 358),
               (445, 326),
               (697, 352),
               (845, 394),    # 035
               (899, 392),
               (984, 311),
               (1199, 326),
               (1291, 304),
               (1427, 353),   # 040
               (1485, 330),
               (1847, 349),
               (9, 395),
               (207, 435),
               (355, 454),    # 045
               (462, 420),
               (583, 384),
               (732, 457),
               (949, 460),
               (1057, 402),   # 050
               (1242, 391),
               (1349, 368),
               (1445, 430),
               (1516, 407),
               (1694, 409),   # 055
               (1913, 435),
               (100, 487),
               (257, 491),
               (301, 530),
               (384, 518),    # 060
               (504, 541),
               (578, 525),
               (745, 580),
               (847, 560),
               (940, 540),    # 065
               (996, 529),
               (1134, 493),
               (1279, 489),
               (1388, 463),
               (1517, 499),   # 070
               (1676, 498),
               (1805, 500),
               (75, 555),
               (140, 620),
               (234, 596),    # 075
               (358, 584),
               (418, 650),
               (533, 630),
               (604, 615),
               (773, 653),    # 080
               (914, 678),
               (969, 642),
               (1092, 603),
               (1214, 541),
               (1279, 571),   # 085
               (1408, 598),
               (1533, 613),
               (1580, 635),
               (1668, 607),
               (1753, 603),   # 090
               (1899, 581),
               (30, 684),
               (36, 735),
               (157, 702),
               (221, 689),    # 095
               (501, 751),
               (568, 733),
               (645, 706),
               (735, 702),
               (874, 734),    # 100
               (996, 692),
               (1172, 628),
               (1285, 618),
               (1406, 663),
               (1716, 684),   # 105
               (1831, 709),
               (1932, 721),
               (1693, 810),
               (600, 846),
               (725, 763),    # 110
               (755, 807),
               (794, 782),
               (917, 807),
               (1034, 770),
               (1159, 715),   # 115
               (1407, 796),
               (1565, 849),
               (1409, 891),
               (1881, 896),
               (29, 1001),    # 120
               (100, 1002),
               (202, 991),
               (447, 969),
               (585, 934),
               (834, 867),    # 125
               (1091, 814),
               (1249, 859),
               (1493, 1125),
               (1555, 908),
               (803, 946),    # 130
               (863, 911),
               (1028, 874),
               (1181, 983),
               (1317, 935),
               (1608, 954),   # 135
               (1846, 1038),
               (387, 1052),
               (637, 1006),
               (791, 1013),
               (1032, 983),   # 140
               (1242, 1007),
               (1406, 1029),
               (1547, 1015),
               (57, 1182),
               (124, 1171),   # 145
               (221, 1160),
               (303, 1135),
               (388, 1123),
               (481, 1107),
               (572, 1081),   # 150
               (613, 1126),
               (679, 1055),
               (726, 1115),
               (893, 1069),
               (938, 1157),   # 155
               (1048, 1155),
               (1139, 1159),
               (1291, 1099),
               (1311, 1300),
               (1596, 1146),  # 160
               (1751, 1141),
               (1932, 1139),
               (208, 1206),
               (304, 1207),
               (506, 1232),   # 165
               (687, 1185),
               (841, 1212),
               (902, 1255),
               (1045, 1241),
               (1132, 1221),  # 170
               (1719, 1445),
               (1437, 1244),
               (1656, 1292),
               (1827, 1234),
               (1913, 1304),  # 175
               (15, 1302),
               (109, 1284),
               (259, 1261),
               (427, 1291),
               (533, 1308),   # 180
               (635, 1280),
               (676, 1301),
               (785, 1247),
               (986, 1319),
               (1095, 1386),  # 185
               (1211, 1369),
               (1363, 1378),
               (1565, 1365),
               (108, 1417),
               (198, 1472),   # 190
               (332, 1375),
               (341, 1491),
               (606, 1374),
               (639, 1409),
               (714, 1406),   # 195
               (837, 1340),
               (859, 1420),
               (1293, 1490),
               (1592, 1515)
            )

# Translate a map location number to a pixel value, adjusted
# for the map's zoom level.
def locToPixel(loc, zoom):
   pixel = pixelTable[loc]
   adjustedX = pixel[0] / zoom
   adjustedY = pixel[1] / zoom
   return (adjustedX, adjustedY)


GRIDSIZE = (100, 100)
MASKSIZE = (39, 42)  # size of a rect that contains a map number graphic
gridHash = SetHash()
wxInitAllImageHandlers()
maskImageFile = os.path.join(MEDIAROOT, "images/map-number-mask.png")
maskImage = wxImage(maskImageFile, wxBITMAP_TYPE_ANY)


# Create a hash table that assists in mapping pixel locations to map numbers.
# Specifically, this hash maps 100x100 grids from the map into sets of
# locations that overlap those grids.
def generateGridHash():
   gridHash.clear()
   for i in range(MAPSIZE[0]/GRIDSIZE[0] + 1):
      for j in range(MAPSIZE[1]/GRIDSIZE[1] + 1):
         grid = (i*GRIDSIZE[0], j*GRIDSIZE[1], GRIDSIZE[0], GRIDSIZE[1])
         for loc in range(1, len(pixelTable)):
            rect = (pixelTable[loc][0], pixelTable[loc][1],
               MASKSIZE[0], MASKSIZE[1])
            if collideRect(rect, grid):
               gridHash.add((i, j), loc)


# Map a pixel into a location on the map, adjusted for the map's zoom level.  
# The following algorithm is used:
# 1) Find the grid of size GRIDSIZE that contains this pixel.
# 2) Use the gridHash to get the set of location numbers that overlap
#    this grid (partially or completely).  (This is generally two or fewer
#    locations.)
# 3) Search through each of these locations.  Test whether the pixel is
#    contained in a rect that contains the map number graphic.
# 4) If yes, then check whether the pixel is contained in a bitmap mask that
#    exactly covers the map number graphic.  If yes, then return the location
#    number.
def pixelToLoc(pixel, zoom):
   adjPixel = (pixel[0]*zoom, pixel[1]*zoom)
   gridIndex = (adjPixel[0]/GRIDSIZE[0], adjPixel[1]/GRIDSIZE[1])
   try:
      locSet = gridHash.get(gridIndex)
   except KeyError:
      # we can't have a match if there are no numbers in this grid
      return 0

   for loc in locSet:
      if collidePoint(adjPixel, (pixelTable[loc][0], pixelTable[loc][1],
            MASKSIZE[0], MASKSIZE[1])):
         maskLoc = (adjPixel[0]-pixelTable[loc][0], adjPixel[1]-pixelTable[loc][1])
         if maskImage.GetRed(maskLoc[0], maskLoc[1]) == 0:
            return loc

   return 0





# arch-tag: DO_NOT_CHANGE_d9a46f16-5b20-4bc1-880f-1d6f10723d06 
