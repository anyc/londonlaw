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



TAXI        = "taxi"
BUS         = "bus"
UNDERGROUND = "underground"
BLACK       = "black"


# To find the routes available at location 100, set routes=locToRoutes[100].
# routes[n][0] is one of the locations that location 100 can connect to,
# and routes[n][1] is a tuple of the methods that can be used to reach
# that location.  So for example:
#
#   routes = locToRoutes[100]
#   possible_moves = []
#   for route in routes:
#      if (has_taxi() and TAXI in route[1]) or
#         (has_bus() and BUS in route[1]) or
#         (has_underground() and UNDERGROUND in route[1]) or
#         has_black():
#      possible_moves.append(route[0])
#
# This routine would create a list of all possible locations that the
# player could move to, assuming has_taxi() and friend are properly
# defined.


# Note for proofreading: the algorithm for creating this map was (roughly) to look
# for first taxi routes (clockwise from the route going upward), then bus routes
# and underground routes.
locToRoutes = \
      ( None,  # locToRoutes[0] has no value; need to access locToRoutes[1] and higher               
         ( (8, (TAXI,)), (9, (TAXI,)), (58, (BUS,)), (46, (BUS, UNDERGROUND)) ),     # 001 
         ( (20, (TAXI,)), (10, (TAXI,)) ),
         ( (11, (TAXI,)), (12, (TAXI,)), (4, (TAXI,)), (22, (BUS,)), (23, (BUS,)) ),
         ( (3, (TAXI,)), (13, (TAXI,)) ),
         ( (15, (TAXI,)), (16, (TAXI,)) ),                                           # 005
         ( (29, (TAXI,)), (7, (TAXI,)) ),
         ( (6, (TAXI,)), (17, (TAXI,)), (42, (BUS,)) ),
         ( (1, (TAXI,)), (19, (TAXI,)), (18, (TAXI,)) ),
         ( (1, (TAXI,)), (19, (TAXI,)), (20, (TAXI,)) ),
         ( (2, (TAXI,)), (11, (TAXI,)), (34, (TAXI,)), (21, (TAXI,)) ),              # 010
         ( (3, (TAXI,)), (10, (TAXI,)), (22, (TAXI,)) ),
         ( (3, (TAXI,)), (23, (TAXI,)) ),
         ( (4, (TAXI,)), (14, (TAXI, BUS)), (24, (TAXI,)), (23, (TAXI, BUS)), (52, (BUS,)), 
            (89, (UNDERGROUND,)), (67, (UNDERGROUND,)), (46, (UNDERGROUND,)) ),
         ( (13, (TAXI, BUS)), (15, (TAXI, BUS)), (25, (TAXI,)) ),
         ( (5, (TAXI,)), (16, (TAXI,)), (28, (TAXI,)), (26, (TAXI,)), (14, (TAXI, BUS)),
            (29, (BUS,)), (41, (BUS,)) ),                                            # 015
         ( (5, (TAXI,)), (29, (TAXI,)), (28, (TAXI,)), (15, (TAXI,)) ),
         ( (7, (TAXI,)), (30, (TAXI,)), (29, (TAXI,)) ),
         ( (8, (TAXI,)), (31, (TAXI,)), (43, (TAXI,)) ),
         ( (8, (TAXI,)), (9, (TAXI,)), (32, (TAXI,)) ),
         ( (2, (TAXI,)), (9, (TAXI,)), (33, (TAXI,)) ),                              # 020
         ( (10, (TAXI,)), (33, (TAXI,)) ),
         ( (11, (TAXI,)), (23, (TAXI, BUS)), (35, (TAXI,)), (34, (TAXI, BUS)),
            (3, (BUS,)), (65, (BUS,)) ),
         ( (12, (TAXI,)), (13, (TAXI, BUS)), (37, (TAXI,)), (22, (TAXI, BUS)), 
            (3, (BUS,)), (67, (BUS,)) ),
         ( (13, (TAXI,)), (38, (TAXI,)), (37, (TAXI,)) ),
         ( (14, (TAXI,)), (39, (TAXI,)), (38, (TAXI,)) ),                            # 025
         ( (15, (TAXI,)), (27, (TAXI,)), (39, (TAXI,)) ),
         ( (26, (TAXI,)), (28, (TAXI,)), (40, (TAXI,)) ),
         ( (15, (TAXI,)), (16, (TAXI,)), (41, (TAXI,)), (27, (TAXI,)) ),
         ( (6, (TAXI,)), (17, (TAXI,)), (42, (TAXI, BUS)), (41, (TAXI, BUS)), (16, (TAXI,)),
            (55, (BUS,)), (15, (BUS,)) ),
         ( (17, (TAXI,)), (42, (TAXI,)) ),                                           # 030
         ( (18, (TAXI,)), (44, (TAXI,)), (43, (TAXI,)) ),
         ( (19, (TAXI,)), (33, (TAXI,)), (45, (TAXI,)), (44, (TAXI,)) ),
         ( (20, (TAXI,)), (21, (TAXI,)), (46, (TAXI,)), (32, (TAXI,)) ),
         ( (10, (TAXI,)), (22, (TAXI, BUS)), (48, (TAXI,)), (47, (TAXI,)), (63, (BUS,)),
            (46, (BUS,)) ),
         ( (22, (TAXI,)), (36, (TAXI,)), (65, (TAXI,)), (48, (TAXI,)) ),             # 035
         ( (37, (TAXI,)), (49, (TAXI,)), (35, (TAXI,)) ),
         ( (23, (TAXI,)), (24, (TAXI,)), (50, (TAXI,)), (36, (TAXI,)) ),
         ( (24, (TAXI,)), (25, (TAXI,)), (51, (TAXI,)), (50, (TAXI,)) ),
         ( (26, (TAXI,)), (52, (TAXI,)), (51, (TAXI,)), (25, (TAXI,)) ),
         ( (27, (TAXI,)), (41, (TAXI,)), (53, (TAXI,)), (52, (TAXI,)) ),             # 040
         ( (28, (TAXI,)), (29, (TAXI, BUS)), (54, (TAXI,)), (40, (TAXI,)),
            (15, (BUS,)), (87, (BUS,)), (52, (BUS,)) ),
         ( (30, (TAXI,)), (56, (TAXI,)), (72, (TAXI, BUS)), (29, (TAXI, BUS)),
            (7, (BUS,)) ),
         ( (18, (TAXI,)), (31, (TAXI,)), (57, (TAXI,)) ),
         ( (32, (TAXI,)), (58, (TAXI,)), (31, (TAXI,)) ),
         ( (32, (TAXI,)), (46, (TAXI,)), (60, (TAXI,)), (59, (TAXI,)),               # 045
            (58, (TAXI,)) ),
         ( (33, (TAXI,)), (47, (TAXI,)), (61, (TAXI,)), (45, (TAXI,)), (34, (BUS,)),
            (78, (BUS,)), (58, (BUS,)), (1, (BUS, UNDERGROUND)), (13, (UNDERGROUND,)),
            (79, (UNDERGROUND,)), (74, (UNDERGROUND,)) ),
         ( (34, (TAXI,)), (62, (TAXI,)), (46, (TAXI,)) ),
         ( (34, (TAXI,)), (35, (TAXI,)), (63, (TAXI,)), (62, (TAXI,)) ),
         ( (36, (TAXI,)), (50, (TAXI,)), (66, (TAXI,)) ),
         ( (37, (TAXI,)), (38, (TAXI,)), (49, (TAXI,)) ),                            # 050
         ( (38, (TAXI,)), (39, (TAXI,)), (52, (TAXI,)), (68, (TAXI,)), (67, (TAXI,)) ),
         ( (39, (TAXI,)), (40, (TAXI,)), (69, (TAXI,)), (51, (TAXI,)), (13, (BUS,)),
            (41, (BUS,)), (86, (BUS,)), (67, (BUS,)) ),
         ( (40, (TAXI,)), (54, (TAXI,)), (69, (TAXI,)) ),
         ( (41, (TAXI,)), (55, (TAXI,)), (70, (TAXI,)), (53, (TAXI,)) ),
         ( (71, (TAXI,)), (54, (TAXI,)), (29, (BUS,)), (89, (BUS,)) ),               # 055
         ( (42, (TAXI,)), (91, (TAXI,)) ),
         ( (43, (TAXI,)), (58, (TAXI,)), (73, (TAXI,)) ),
         ( (45, (TAXI,)), (59, (TAXI,)), (75, (TAXI,)), (74, (TAXI, BUS)), (57, (TAXI,)),
            (44, (TAXI,)), (46, (BUS,)), (77, (BUS,)), (1, (BUS,)) ),
         ( (45, (TAXI,)), (76, (TAXI,)), (75, (TAXI,)), (58, (TAXI,)) ),
         ( (45, (TAXI,)), (61, (TAXI,)), (76, (TAXI,)) ),                            # 060
         ( (46, (TAXI,)), (62, (TAXI,)), (78, (TAXI,)), (76, (TAXI,)), (60, (TAXI,)) ),
         ( (47, (TAXI,)), (48, (TAXI,)), (79, (TAXI,)), (61, (TAXI,)) ),
         ( (48, (TAXI,)), (64, (TAXI,)), (80, (TAXI,)), (79, (TAXI, BUS)),
            (34, (BUS,)), (65, (BUS,)), (100, (BUS,)) ),
         ( (65, (TAXI,)), (81, (TAXI,)), (63, (TAXI,)) ),
         ( (35, (TAXI,)), (66, (TAXI,)), (82, (TAXI, BUS)), (64, (TAXI,)),           # 065
            (22, (BUS,)), (67, (BUS,)), (63, (BUS,)) ),                                           
         ( (49, (TAXI,)), (67, (TAXI,)), (82, (TAXI,)), (65, (TAXI,)) ),
         ( (51, (TAXI,)), (68, (TAXI,)), (84, (TAXI,)), (66, (TAXI,)), (23, (BUS,)),
            (52, (BUS,)), (102, (BUS,)), (82, (BUS,)), (65, (BUS,)),
            (13, (UNDERGROUND,)), (89, (UNDERGROUND,)), (111, (UNDERGROUND,)),
            (79, (UNDERGROUND,)) ),
         ( (51, (TAXI,)), (69, (TAXI,)), (85, (TAXI,)), (67, (TAXI,)) ),
         ( (52, (TAXI,)), (53, (TAXI,)), (86, (TAXI,)), (68, (TAXI,)) ),
         ( (54, (TAXI,)), (71, (TAXI,)), (87, (TAXI,)) ),                            # 070
         ( (55, (TAXI,)), (72, (TAXI,)), (89, (TAXI,)), (70, (TAXI,)) ),
         ( (42, (TAXI, BUS)), (91, (TAXI,)), (90, (TAXI,)), (71, (TAXI,)),
            (107, (BUS,)), (105, (BUS,)) ),
         ( (57, (TAXI,)), (74, (TAXI,)), (92, (TAXI,)) ),
         ( (58, (TAXI, BUS)), (75, (TAXI,)), (92, (TAXI,)), (73, (TAXI,)),
            (94, (BUS,)), (46, (UNDERGROUND,)) ),
         ( (58, (TAXI,)), (59, (TAXI,)), (94, (TAXI,)), (74, (TAXI,)) ),             # 075
         ( (59, (TAXI,)), (60, (TAXI,)), (61, (TAXI,)), (77, (TAXI,)) ),
         ( (78, (TAXI, BUS)), (96, (TAXI,)), (95, (TAXI,)), (76, (TAXI,)),
            (124, (BUS,)), (94, (BUS,)), (58, (BUS,)) ),
         ( (61, (TAXI,)), (79, (TAXI, BUS)), (97, (TAXI,)), (77, (TAXI, BUS)),
            (46, (BUS,)) ),
         ( (62, (TAXI,)), (63, (TAXI, BUS)), (98, (TAXI,)), (78, (TAXI, BUS)),
            (46, (UNDERGROUND,)), (67, (UNDERGROUND,)), (111, (UNDERGROUND,)),
            (93, (UNDERGROUND,)) ),
         ( (63, (TAXI,)), (100, (TAXI,)), (99, (TAXI,)) ),                           # 080
         ( (64, (TAXI,)), (82, (TAXI,)), (100, (TAXI,)) ),
         ( (65, (TAXI, BUS)), (66, (TAXI,)), (67, (BUS,)), (101, (TAXI,)), (140, (BUS,)),
            (81, (TAXI,)), (100, (BUS,)) ),
         ( (102, (TAXI,)), (101, (TAXI,)) ),
         ( (67, (TAXI,)), (85, (TAXI,)) ),
         ( (68, (TAXI,)), (103, (TAXI,)), (84, (TAXI,)) ),                           # 085
         ( (69, (TAXI,)), (52, (BUS,)), (87, (BUS,)), (104, (TAXI,)), (116, (BUS,)),
            (103, (TAXI,)), (102, (BUS,)) ),
         ( (70, (TAXI,)), (41, (BUS,)), (88, (TAXI,)), (105, (BUS,)), (86, (BUS,)) ),
         ( (89, (TAXI,)), (117, (TAXI,)), (87, (TAXI,)) ),
         ( (71, (TAXI,)), (55, (BUS,)), (13, (UNDERGROUND,)), (105, (TAXI, BUS)),
            (128, (UNDERGROUND,)), (88, (TAXI,)), (140, (UNDERGROUND,)),
            (67, (UNDERGROUND,)) ),
         ( (72, (TAXI,)), (91, (TAXI,)), (105, (TAXI,)) ),                           # 090 
         ( (56, (TAXI,)), (107, (TAXI,)), (105, (TAXI,)), (90, (TAXI,)), (72, (TAXI,)) ),
         ( (73, (TAXI,)), (74, (TAXI,)), (93, (TAXI,)) ),
         ( (92, (TAXI,)), (94, (TAXI, BUS)), (79, (UNDERGROUND,)) ),
         ( (74, (BUS,)), (75, (TAXI,)), (95, (TAXI,)), (77, (BUS,)), (93, (TAXI, BUS)) ),
         ( (77, (TAXI,)), (122, (TAXI,)), (94, (TAXI,)) ),                           # 095
         ( (77, (TAXI,)), (97, (TAXI,)), (109, (TAXI,)) ),
         ( (78, (TAXI,)), (98, (TAXI,)), (109, (TAXI,)), (96, (TAXI,)) ),
         ( (79, (TAXI,)), (99, (TAXI,)), (110, (TAXI,)), (97, (TAXI,)) ),
         ( (80, (TAXI,)), (112, (TAXI,)), (110, (TAXI,)), (98, (TAXI,)) ),
         ( (81, (TAXI,)), (82, (BUS,)), (101, (TAXI,)), (113, (TAXI,)),              # 100
            (112, (TAXI,)), (111, (BUS,)), (80, (TAXI,)), (63, (BUS,)) ),
         ( (83, (TAXI,)), (114, (TAXI,)), (100, (TAXI,)), (82, (TAXI,)) ),
         ( (67, (BUS,)), (103, (TAXI,)), (86, (BUS,)), (115, (TAXI,)), (127, (BUS,)),
            (83, (TAXI,)) ),
         ( (85, (TAXI,)), (86, (TAXI,)), (102, (TAXI,)) ),
         ( (86, (TAXI,)), (116, (TAXI,)) ),
         ( (90, (TAXI,)), (72, (BUS,)), (91, (TAXI,)), (106, (TAXI,)),               # 105
            (107, (BUS,)), (108, (TAXI, BUS)), (87, (BUS,)), (89, (TAXI, BUS)) ),
         ( (107, (TAXI,)), (105, (TAXI,)) ),
         ( (91, (TAXI,)), (72, (BUS,)), (119, (TAXI,)), (161, (BUS,)),
            (106, (TAXI,)), (105, (BUS,)) ),
         ( (105, (TAXI, BUS)), (119, (TAXI,)), (135, (BUS,)), (117, (TAXI,)),
            (116, (BUS,)), (115, (BLACK,)) ),
         ( (97, (TAXI,)), (110, (TAXI,)), (124, (TAXI,)), (96, (TAXI,)) ),
         ( (99, (TAXI,)), (111, (TAXI,)), (109, (TAXI,)), (98, (TAXI,)) ),           # 110
         ( (112, (TAXI,)), (100, (BUS,)), (67, (UNDERGROUND,)),
            (153, (UNDERGROUND,)), (124, (TAXI, BUS)), (163, (UNDERGROUND,)),
            (110, (TAXI,)), (79, (UNDERGROUND,)) ),
         ( (100, (TAXI,)), (125, (TAXI,)), (111, (TAXI,)), (99, (TAXI,)) ),
         ( (114, (TAXI,)), (125, (TAXI,)), (100, (TAXI,)) ),
         ( (101, (TAXI,)), (115, (TAXI,)), (126, (TAXI,)),
            (132, (TAXI,)), (131, (TAXI,)), (113, (TAXI,)) ),
         ( (102, (TAXI,)), (127, (TAXI,)), (126, (TAXI,)), (114, (TAXI,)),           # 115
            (108, (BLACK,)), (157, (BLACK,)) ),
         ( (104, (TAXI,)), (86, (BUS,)), (117, (TAXI,)), (108, (BUS,)),
            (118, (TAXI,)), (142, (BUS,)), (127, (TAXI, BUS)) ),
         ( (88, (TAXI,)), (108, (TAXI,)), (129, (TAXI,)), (116, (TAXI,)) ),
         ( (116, (TAXI,)), (129, (TAXI,)), (142, (TAXI,)), (134, (TAXI,)) ),
         ( (107, (TAXI,)), (136, (TAXI,)), (108, (TAXI,)) ),
         ( (121, (TAXI,)), (144, (TAXI,)) ),                                         # 120
         ( (122, (TAXI,)), (145, (TAXI,)), (120, (TAXI,)) ),
         ( (95, (TAXI,)), (123, (TAXI, BUS)), (146, (TAXI,)),
            (121, (TAXI,)), (144, (BUS,)) ),
         ( (124, (TAXI, BUS)), (149, (TAXI,)), (165, (BUS,)), (148, (TAXI,)),
            (137, (TAXI,)), (144, (BUS,)), (122, (TAXI, BUS)) ),
         ( (109, (TAXI,)), (111, (TAXI, BUS)), (130, (TAXI,)), (138, (TAXI,)),
            (153, (BUS,)), (123, (TAXI, BUS)), (77, (BUS,)) ),
         ( (113, (TAXI,)), (131, (TAXI,)), (112, (TAXI,)) ),                         # 125
         ( (115, (TAXI,)), (127, (TAXI,)), (140, (TAXI,)), (114, (TAXI,)) ),
         ( (116, (TAXI, BUS)), (134, (TAXI,)), (133, (TAXI, BUS)),
            (126, (TAXI,)), (115, (TAXI,)), (102, (BUS,)) ),
         ( (143, (TAXI,)), (135, (BUS,)), (89, (UNDERGROUND,)), (160, (TAXI,)),
            (161, (BUS,)), (188, (TAXI,)), (199, (BUS,)), (172, (TAXI,)),
            (187, (BUS,)), (185, (UNDERGROUND,)), (142, (TAXI, BUS)),
            (140, (UNDERGROUND,)) ),
         ( (117, (TAXI,)), (135, (TAXI,)), (143, (TAXI,)), (142, (TAXI,)),
            (118, (TAXI,)) ),
         ( (131, (TAXI,)), (139, (TAXI,)), (124, (TAXI,)) ),                         # 130
         ( (114, (TAXI,)), (130, (TAXI,)), (125, (TAXI,)) ),
         ( (114, (TAXI,)), (140, (TAXI,)) ),
         ( (127, (TAXI, BUS)), (141, (TAXI,)), (157, (BUS,)), (140, (TAXI, BUS)) ),
         ( (118, (TAXI,)), (142, (TAXI,)), (141, (TAXI,)), (127, (TAXI,)) ),
         ( (108, (BUS,)), (136, (TAXI,)), (161, (TAXI, BUS)), (143, (TAXI,)),        # 135
            (128, (BUS,)), (129, (TAXI,)) ),
         ( (119, (TAXI,)), (162, (TAXI,)), (135, (TAXI,)) ),
         ( (123, (TAXI,)), (147, (TAXI,)) ),
         ( (152, (TAXI,)), (150, (TAXI,)), (124, (TAXI,)) ),
         ( (130, (TAXI,)), (140, (TAXI,)), (154, (TAXI,)), (153, (TAXI,)) ),
         ( (132, (TAXI,)), (82, (BUS,)), (126, (TAXI,)), (89, (UNDERGROUND,)),       # 140
            (133, (TAXI, BUS)), (128, (UNDERGROUND,)), (156, (TAXI, BUS)),
            (154, (TAXI, BUS)), (153, (UNDERGROUND,)), (139, (TAXI,)) ),
         ( (134, (TAXI,)), (142, (TAXI,)), (158, (TAXI,)), (133, (TAXI,)) ),
         ( (118, (TAXI,)), (116, (BUS,)), (129, (TAXI,)), (143, (TAXI,)),
            (128, (TAXI, BUS)), (158, (TAXI,)), (157, (BUS,)), (141, (TAXI,)),
            (134, (TAXI,)) ),
         ( (135, (TAXI,)), (160, (TAXI,)), (128, (TAXI,)), (142, (TAXI,)),
            (129, (TAXI,)) ),
         ( (120, (TAXI,)), (122, (BUS,)), (145, (TAXI,)), (123, (BUS,)),
            (163, (BUS,)), (177, (TAXI,)) ),
         ( (121, (TAXI,)), (146, (TAXI,)), (144, (TAXI,)) ),                         # 145
         ( (122, (TAXI,)), (147, (TAXI,)), (163, (TAXI,)), (145, (TAXI,)) ),
         ( (137, (TAXI,)), (164, (TAXI,)), (146, (TAXI,)) ),
         ( (123, (TAXI,)), (149, (TAXI,)), (164, (TAXI,)) ),
         ( (123, (TAXI,)), (150, (TAXI,)), (165, (TAXI,)), (148, (TAXI,)) ),
         ( (138, (TAXI,)), (151, (TAXI,)), (149, (TAXI,)) ),                         # 150
         ( (152, (TAXI,)), (166, (TAXI,)), (165, (TAXI,)), (150, (TAXI,)) ),
         ( (153, (TAXI,)), (151, (TAXI,)), (138, (TAXI,)) ),
         ( (139, (TAXI,)), (111, (UNDERGROUND,)), (154, (TAXI, BUS)),
            (140, (UNDERGROUND,)), (167, (TAXI,)), (184, (BUS,)),
            (185, (UNDERGROUND,)), (166, (TAXI,)), (180, (BUS,)),
            (163, (UNDERGROUND,)), (152, (TAXI,)), (124, (BUS,)) ),
         ( (140, (TAXI, BUS)), (155, (TAXI,)), (156, (BUS,)), (153, (TAXI, BUS)),
            (139, (TAXI,)) ),
         ( (156, (TAXI,)), (168, (TAXI,)), (167, (TAXI,)), (154, (TAXI,)) ),         # 155
         ( (140, (TAXI, BUS)), (157, (TAXI, BUS)), (169, (TAXI,)),
            (184, (BUS,)), (155, (TAXI,)), (154, (BUS,)) ),
         ( (133, (BUS,)), (158, (TAXI,)), (142, (BUS,)), (170, (TAXI,)),
            (185, (BUS,)), (156, (TAXI, BUS)), (115, (BLACK,)), (194, (BLACK,)) ),
         ( (141, (TAXI,)), (142, (TAXI,)), (159, (TAXI,)), (157, (TAXI,)) ),
         ( (158, (TAXI,)), (172, (TAXI,)), (198, (TAXI,)), (186, (TAXI,)),
            (170, (TAXI,)) ),
         ( (143, (TAXI,)), (161, (TAXI,)), (173, (TAXI,)), (128, (TAXI,)) ),         # 160
         ( (107, (BUS,)), (174, (TAXI,)), (199, (BUS,)), (160, (TAXI,)),
            (128, (BUS,)), (135, (TAXI, BUS)) ),
         ( (175, (TAXI,)), (136, (TAXI,)) ),
         ( (146, (TAXI,)), (111, (UNDERGROUND,)), (153, (UNDERGROUND,)),
            (191, (BUS,)), (177, (TAXI,)), (176, (BUS,)), (144, (BUS,)) ),
         ( (147, (TAXI,)), (148, (TAXI,)), (179, (TAXI,)), (178, (TAXI,)) ),
         ( (149, (TAXI,)), (123, (BUS,)), (151, (TAXI,)), (180, (TAXI, BUS)),        # 165
            (179, (TAXI,)), (191, (BUS,)) ),
         ( (153, (TAXI,)), (183, (TAXI,)), (181, (TAXI,)), (151, (TAXI,)) ),
         ( (155, (TAXI,)), (168, (TAXI,)), (183, (TAXI,)), (153, (TAXI,)) ),
         ( (155, (TAXI,)), (184, (TAXI,)), (167, (TAXI,)) ),
         ( (156, (TAXI,)), (184, (TAXI,)) ),
         ( (157, (TAXI,)), (159, (TAXI,)), (185, (TAXI,)) ),                         # 170
         ( (173, (TAXI,)), (175, (TAXI,)), (199, (TAXI,)) ),
         ( (128, (TAXI,)), (187, (TAXI,)), (159, (TAXI,)) ),
         ( (160, (TAXI,)), (174, (TAXI,)), (171, (TAXI,)), (188, (TAXI,)) ),
         ( (175, (TAXI,)), (173, (TAXI,)), (161, (TAXI,)) ),
         ( (162, (TAXI,)), (171, (TAXI,)), (174, (TAXI,)) ),                         # 175
         ( (177, (TAXI,)), (163, (BUS,)), (189, (TAXI,)), (190, (BUS,)) ),
         ( (144, (TAXI,)), (163, (TAXI,)), (176, (TAXI,)) ),
         ( (164, (TAXI,)), (191, (TAXI,)), (189, (TAXI,)) ),
         ( (165, (TAXI,)), (191, (TAXI,)), (164, (TAXI,)) ),
         ( (165, (TAXI, BUS)), (181, (TAXI,)), (153, (BUS,)), (193, (TAXI,)),        # 180
            (184, (BUS,)), (190, (BUS,)) ),
         ( (166, (TAXI,)), (182, (TAXI,)), (193, (TAXI,)), (180, (TAXI,)) ),
         ( (183, (TAXI,)), (195, (TAXI,)), (181, (TAXI,)) ),
         ( (167, (TAXI,)), (196, (TAXI,)), (182, (TAXI,)), (166, (TAXI,)) ),
         ( (169, (TAXI,)), (156, (BUS,)), (185, (TAXI, BUS)), (197, (TAXI,)),
            (196, (TAXI,)), (180, (BUS,)), (168, (TAXI,)), (153, (BUS,)) ),
         ( (170, (TAXI,)), (157, (BUS,)), (186, (TAXI,)), (187, (BUS,)),             # 185
            (128, (UNDERGROUND,)), (184, (TAXI, BUS)), (153, (UNDERGROUND,)) ),
         ( (159, (TAXI,)), (198, (TAXI,)), (185, (TAXI,)) ),
         ( (172, (TAXI,)), (128, (BUS,)), (188, (TAXI,)), (198, (TAXI,)),
            (185, (BUS,)) ),
         ( (128, (TAXI,)), (173, (TAXI,)), (199, (TAXI,)), (187, (TAXI,)) ),
         ( (178, (TAXI,)), (190, (TAXI,)), (176, (TAXI,)) ),
         ( (191, (TAXI, BUS)), (192, (TAXI,)), (180, (BUS,)),                        # 190
            (189, (TAXI,)), (176, (BUS,)) ),
         ( (179, (TAXI,)), (165, (BUS,)), (192, (TAXI,)), (190, (TAXI, BUS)),
            (178, (TAXI,)), (163, (BUS,)) ),
         ( (191, (TAXI,)), (194, (TAXI,)), (190, (TAXI,)) ),
         ( (181, (TAXI,)), (194, (TAXI,)), (180, (TAXI,)) ),
         ( (195, (TAXI,)), (192, (TAXI,)), (193, (TAXI,)), (157, (BLACK,)) ),
         ( (182, (TAXI,)), (197, (TAXI,)), (194, (TAXI,)) ),                         # 195
         ( (183, (TAXI,)), (184, (TAXI,)), (197, (TAXI,)) ),
         ( (196, (TAXI,)), (184, (TAXI,)), (195, (TAXI,)) ),
         ( (159, (TAXI,)), (187, (TAXI,)), (199, (TAXI,)), (186, (TAXI,)) ),
         ( (188, (TAXI,)), (128, (BUS,)), (171, (TAXI,)), (161, (BUS,)),
            (198, (TAXI,)) ) 
      )






# Test a map to see if it is self-consistent--i.e., check that routes from A to B also
# exist from B to A.  More effective than proofreading...
def checkMap(m):
   passed = 1
   partial = 0
   for i in range(1, len(m)):
      print "testing location " + str(i)
      routes = m[i]
      for route in routes:
         if route[0] < len(m):
            destRoutes = m[route[0]]
            matched = 0
            for destRoute in destRoutes:
               if destRoute[0] == i:
                  matched = 1
                  if destRoute[1] != route[1]:
                     print ("Error at location "+str(i)+": route to " + str(route[0]) +
                        " is not self-consistent.")
                     passed = 0
                  break
            if not matched:
               print "Error at location "+str(i)+": missing route from "+str(route[0])+"."
               passed = 0
         else:
            partial = 1
   print "----------------------------------------------------------------------------------"
   if partial:
      cstr = "Incomplete"
   else:
      cstr = "Complete"
   if passed:
      print cstr + " map is self-consistent."
   else:
      print "Error: "+cstr+" map is not self-consistent."





# Generate a random map with valid connections, for testing purposes.
# Note that is uses lists, because they are mutable and easier to work with.
# The real map ought to be done with tuples.
#def getRandomMap(SIZE):
#   transMethods = [TAXI, BUS, UNDERGROUND, BLACK]
#
#   # Generate outgoing routes from all locations
#   map = [None]
#   for i in range(1,SIZE+1):
#      routes = [] 
#      destList = []  # throwaway counter variable
#      for routeNum in range(random.randrange(1,4)):
#         destination = random.randrange(1, SIZE+1)
#         while destination in destList or destination == i:
#            destination = random.randrange(1, SIZE+1)
#         transports = []
#         for transNum in range(random.randrange(1,4)):
#            dummy = random.choice(transMethods)
#            if dummy not in transports:
#               transports.append(dummy)
#         routes.append([destination, transports])
#         destList.append(destination)
#      map.append(routes)
#
#   # Now make the map consistent by adding the reverse paths when necessary
#   for i in range(1,SIZE+1):
#      routes = map[i]
#      for routeNum in range(len(routes)):
#         destRoutes = map[routes[routeNum][0]]
#         matchRoute = None
#         for destRoute in destRoutes:
#            if destRoute[0] == i:
#               matchRoute = destRoute
#               break
#         if matchRoute:
#            routes[routeNum][1] = matchRoute[1][:]
#         else:
#            destRoutes.append(routes[routeNum])
#     # map is mutable, so it gets changed simply by changing 'routes'.
#
#   return map





# arch-tag: graph representation of map
