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

# path.py
#
# General path and distance-finding algorithms, probably most useful for
# AI programming.
#
# Two pathfinding algorithms are provided: cheapest_path and shortest_path.
# shortest_path is the one to choose when trying to move a pawn from A to B as
# quickly as possible without regard for the tickets spent.  The rest of the
# time, cheapest_path is probably a better choice.

from londonlaw.common import map
import sets



# Cost function which penalizes all tickets (almost) equally.  The small
# cost differences are to provide a slight preference for the
# taxi->bus->underground->black ordering.
def equal_cost(ticket_amounts, ticket_type):
   if ticket_type == 'taxi':
      return 1
   elif ticket_type == 'bus':
      return 1.01
   elif ticket_type == 'underground':
      return 1.02
   else:
      return 1.03

# Same as above, but penalizes black tickets heavily.
def equal_cost_noblack(ticket_amounts, ticket_type):
   if ticket_type == 'taxi':
      return 1
   elif ticket_type == 'bus':
      return 1.01
   elif ticket_type == 'underground':
      return 1.02
   else:
      return 1000000

# Define an unlimited ticket set.
unlimited_tickets = {'taxi' : -1, 'bus' : -1, 'underground' : -1, 'black' : -1}

# Define a ticket set with unlimited non-black tickets.
unlimited_tickets_noblack = {'taxi' : -1, 'bus' : -1, 'underground' : -1, 'black' : 0}



# iterate backward through a 'previous' array to create a path
# in list form (used for cheapest_path and shortest_path)
def _compute_path(source, dest, previous):
   if source == dest:
      return []
   elif previous[dest] == None:
      return None
   else:
      # use the 'previous' array to compute a path in list form
      i = dest
      p = [(dest, previous[dest][1])]
      while previous[i][0] != source:
         p.append((previous[i][0], previous[previous[i][0]][1]))
         i = previous[i][0]
      p.reverse()
      return p 



# Compute the path of least cost from a source vertex to either one destination
# vertex or to all vertices, given an optional cost function that specifies the
# penalty associated with using taxi, bus, underground, and black tickets.
# A ticket set may also be specified, which will be used to eliminate paths that
# violate the ticket constraint.
#
# The cost function takes a set of ticket amounts as the first argument, and a
# ticket type as the second argument.  As the algorithm iterates through longer
# and longer paths, the set of tickets passed to the cost function will change,
# and the AI programmer may take advantage of this to adapt the relative cost
# for each ticket type as tickets become depleted.
# 
# (This is just Dijkstra's algorithm, with the addition of adaptive cost and 
# path pruning to satisfy the ticket constraint.)
#
# If dest=None, returns an array of paths, one for each destination.  If dest
# is a vertex, returns a single path.  (Using dest=None is more efficient than
# separately computing constrained_shortest_path(t, s, d) for all d.)
#
# The path(s) are provided as a list of (destination, transportation) tuples.  When
# no path can be found for a given destination, provides the value None.
#
# Note: since the graph is sparse, this could be done in a more efficient
#       manner... but it seems plenty fast for N=200.
def cheapest_path(source, dest=None, tickets=unlimited_tickets, cost=equal_cost):
   # U is unvisited vertices
   U = sets.Set()
   for u in range(1, len(map.locToRoutes)):
      U.add(u)
   path_cost         = [1e100] * len(map.locToRoutes)
   path_cost[source] = 0
   previous          = [None] * len(map.locToRoutes)
   t                 = [None] * len(map.locToRoutes)
   t[source]         = tickets.copy()
   
   while len(U) > 0:
      # extract vertex with minimum path
      min_cost = 1e200
      for u in U:
         if path_cost[u] < min_cost:
            min_cost = path_cost[u]
            min_u    = u
      U.remove(min_u)
      if t[min_u] != None:
         for (v, transports) in map.locToRoutes[min_u]:
            for transport in transports:
               if (path_cost[v] > path_cost[min_u] + cost(t[min_u], transport) and 
               t[min_u][transport] != 0):
                  t[v] = t[min_u].copy()
                  if t[v][transport] > 0:
                     t[v][transport] -= 1
                  path_cost[v] = path_cost[min_u] + cost(t[min_u], transport)
                  previous[v] = (min_u, transport)

   if dest == None:
      return ([None] + 
      [_compute_path(source, d, previous) for d in range(1, len(map.locToRoutes))])
   else:
      return _compute_path(source, dest, previous)



# Compute the shortest path between two map vertices, given an optional ticket
# constraint.  Uses a breadth-first search.  We always assume that a shorter
# path to a given vertex is better than a longer path, thus limiting the
# algorithmic complexity.
#
# The cost function takes a set of ticket amounts as the first argument, and a
# ticket type as the second argument.  As the algorithm iterates through longer
# and longer paths, the set of tickets passed to the cost function will change,
# and the AI programmer may take advantage of this to adapt the relative cost
# for each ticket type as tickets become depleted.  Specifying a cost function
# will allow the algorithm to judge between two paths of equal length to
# determine which is preferred.
#
# If dest=None, returns an array of paths, one for each destination.  If dest
# is a vertex, returns a single path.  (Using dest=None is more efficient than
# separately computing constrained_shortest_path(t, s, d) for all d.)
#
# The path(s) are provided as a list of (destination, transportation) tuples.  When
# no path can be found for a given destination, provides the value None.
#
def shortest_path(source, dest=None, tickets=unlimited_tickets, cost=equal_cost):
   # V is visited nodes, U is unvisited
   V = sets.Set([source])
   U = sets.Set()
   for i in range(1, len(map.locToRoutes)):
      U.add(i)
   U.remove(source)

   previous  = [ None ] * len(map.locToRoutes)
   t         = [ None ] * len(map.locToRoutes)
   t[source] = tickets.copy()

   search_vertices = V.copy()
   while (dest == None or dest in U) and len(search_vertices) > 0:
      next_search_vertices = sets.Set()
      for visited in search_vertices:
         for d, transports in map.locToRoutes[visited]:
            if d not in V:
               for transport in transports:
                  if t[visited][transport] != 0:
                     if previous[visited] == None:
                        old_cost = 0
                     else:
                        old_cost = previous[visited][2]
                     # If this destination is in next_search_vertices, then we
                     # are considering the case of choosing between two paths
                     # of the same length.  In that situation we must use the
                     # cost function to decide whether to replace the existing path.
                     if (d not in next_search_vertices or cost(t[visited], transport) + 
                     old_cost < previous[d][2]):
                        t[d] = t[visited].copy()
                        if t[d][transport] > 0:
                           t[d][transport] -= 1
                        previous[d] = (visited, transport, 
                              cost(t[visited], transport) + old_cost)
                        next_search_vertices.add(d)
      V.union_update(next_search_vertices)
      U.difference_update(next_search_vertices)
      search_vertices = next_search_vertices

   if dest == None:
      return ([None] + 
      [_compute_path(source, d, previous) for d in range(1, len(map.locToRoutes))])
   else:
      return _compute_path(source, dest, previous)



# Compute the distance between two map vertices, given optional pathfinding
# function, cost function, and ticket constraint.
#
# If dest=None, returns an array of distances, one for each destination.
# The distance value 'None' is provided when no path can be found which
# satisfies the constraint.
def distance(source, dest=None, pathfinder=shortest_path, 
      cost=equal_cost, tickets=unlimited_tickets):
   def compute_distance(p):
      if p == None:
         return None
      else:
         return len(p)

   paths = pathfinder(source, dest, tickets, cost)
   if dest == None:
      return [compute_distance(p) for p in paths]
   else:
      return compute_distance(paths)



# Given a starting location, number of turns, and optional ticket supply,
# compute the possible locations where a pawn could move.  (This will be slow
# for 'turns' bigger than about 4.)  Returns a Set.
#
# The optional 'eliminate' argument is a list of length 'turns'.  Each element
# of the list is a Set of locations where the pawn cannot move on that turn.
# Thus 'eliminate' could be used to rule out collisions between detectives
# or Mr. X capture scenarios.
#
# If 'force_move' == False, the algorithm assumes that pawns can get stuck due
# to ticket depletion or eliminated locations (as Detectives can), and will
# skip turns as necessary.  If 'force_move' == True, the algorithm will prune
# all scenarios in which the pawn cannot move (useful for determining Mr. X's
# possible destinations).
def possible_destinations(source, turns, tickets=unlimited_tickets, eliminate=None,
      force_move=True):
   if eliminate == None:
      eliminate = [sets.Set()] * turns

   # have to convert 'tickets' to a tuple, because otherwise we can't
   # store it in a Set ("dict objects are unhashable")
   tickets_assoc = ()
   for key in tickets:
      tickets_assoc = tickets_assoc + ((key, tickets[key]),)

   loc_sets  = [sets.Set([(source, tickets_assoc)])]
   for turn in range(turns):
      loc_sets.append(sets.Set())
      for loc, t in loc_sets[turn]:
         is_stuck = 1
         for dest, transports in map.locToRoutes[loc]:
            if dest not in eliminate[turn]:
               for transport in transports:
                  for i in range(len(t)):
                     ticket, amount = t[i]
                     if transport == ticket:
                        if amount != 0:
                           is_stuck = 0
                           if amount > 0:
                              t2 = t[:i] + ((ticket, amount - 1),) + t[i+1:]
                           else:
                              t2 = t
                           loc_sets[turn + 1].add((dest, t2))
         if not force_move and is_stuck:
            # if the pawn is stuck, he just waits in the same location until
            # the next turn
            loc_sets[turn + 1].add((loc, t))

   ret_val = sets.Set()
   for loc, t in loc_sets[turns]:
      ret_val.add(loc)
   return ret_val




# Given a starting location and list of tickets spent, compute the possible
# locations where a pawn could have moved.  (This will be slow for a lengthy
# list of tickets.)  Returns a Set.
#
# The optional 'eliminate' argument is a list of the same length as
# 'tickets_spent'.  Each element of the list is a Set of locations where the
# pawn could not have moved on that turn.  Thus 'eliminate' could be used to
# rule out Mr. X capture scenarios.
def possible_locations(source, tickets_spent, eliminate=None):
   if eliminate == None:
      eliminate = [sets.Set()] * len(tickets_spent)

   loc_sets = [sets.Set([source])]
   for turn in range(len(tickets_spent)):
      loc_sets.append(sets.Set())
      for loc in loc_sets[turn]:
         for dest, transports in map.locToRoutes[loc]:
            if tickets_spent[turn] in transports and dest not in eliminate[turn]:
               loc_sets[turn + 1].add(dest)

   return loc_sets[len(tickets_spent)]



