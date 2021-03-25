import json
import datetime
import re
import copy
import sys
import time
import pprint
from data_cleaning import load_all_data

def parse_time(date_str):
  if re.match(r'\d\d\/\d\d\/20\d\d$', date_str):
    return datetime.datetime.strptime(date_str, '%m/%d/%Y')
  elif re.match(r'\d\d\/\d\d\/\d\d$', date_str):
    return datetime.datetime.strptime(date_str, '%m/%d/%y')

def days_til_end(calendar):
  today = datetime.datetime.now()
  end_day = parse_time(calendar['end_day'])
  diff = (end_day - today).days

  # need to drop any weekends?
  if not calendar['run_on_weekends']:
    day_generator = (today + datetime.timedelta(x + 1) for x in range((end_day - today).days))
    diff = sum(1 for day in day_generator if day.weekday() < 5)
  # drop the holidays that need dropped
  for holiday in calendar['holidays']:
    holiday_as_date = parse_time(holiday)
    if (holiday_as_date - today).days >= 0 and (holiday_as_date - end_day).days >= 0:
      diff -= 1
  return diff

def add_routes(buses, routes):
  best = {
    'buses': {},
    'score': sys.maxsize
  }

  # get all the evening pairings
  pairs = all_evening_pairings(routes, buses)
  pairs.append(None)

  # go through and calculate all assignments given each pair
  for pair in pairs:
    # send in a copy of buses
    assignments = copy.deepcopy(buses)
    add_routes_basic(assignments, routes, pair)
    # "score" the resulting assignments
    curr_score = score_assignments(assignments, routes)
    if curr_score < best['score']:
      best['score'] = curr_score
      best['buses'] = assignments
  
  # now that we have the best, set it in the persistent data
  for bus in buses:
    for a in best['buses']:
      if a['name'] == bus['name']:
        bus['routes'] = a['routes']

def add_routes_basic(buses, routes, pair):
  # prep buses so everyone has empty routes and are sorted highest target mileage to lowest
  buses.sort(key=lambda bus: bus['target_mileage'], reverse=True)
  specific_assignments = False
  for bus in buses:
    bus['routes'] = []
    if bus['assigned_route'] != '':
      specific_assignments = True
  removed_buses = [x for x in buses if not x['should_run']]
  buses = [x for x in buses if x['should_run']]
  # we're going to add a "fake" route that is our pairing and take out the two we've paired
  processed_routes = copy.deepcopy(routes)
  merge_pair(processed_routes, pair)
  processed_routes.sort(key=lambda route: route['avg_daily_mileage'], reverse=True)

  if specific_assignments:
    for bus in buses:
      if bus['assigned_route'] != '':
        for route in processed_routes:
          if route['name'] == bus['assigned_route']:
            bus['routes'].append(route)
            processed_routes.remove(route)

  for route in processed_routes:
    for bus in buses:
      if route['name'] not in bus['excluded'] and not bus['routes']:
        # processing needed if it's the fake route
        if route['name'] == 'fake':
          # split back into proper routes
          two_routes = split_pair(routes, pair)
          bus['routes'].append(two_routes[0])
          bus['routes'].append(two_routes[1])
        else:
          bus['routes'].append(route)
        break
  buses.extend(removed_buses)

def all_evening_pairings(routes, buses):
  not_allowed = []
  for bus in buses:
    if bus['assigned_route'] != '':
      not_allowed.append(bus['assigned_route'])
  pairs = []
  for route in routes:
    if route['name'] != 'evening' and route['name'] not in not_allowed and route['can_double']:
      pairs.append(route['name'])
  return pairs

def merge_pair(routes, pair):
  if pair != None:
    evening = {}
    paired = {}
    for route in routes:
      if route['name'] == 'evening':
        evening = route
      elif route['name'] == pair:
        paired = route
    routes.remove(evening)
    routes.remove(paired)
    routes.append({
      'name': 'fake',
      'avg_daily_mileage': evening['avg_daily_mileage'] + paired['avg_daily_mileage']
    })

def split_pair(routes, pair):
  evening = {}
  paired = {}
  for route in routes:
    if route['name'] == 'evening':
      evening = route
    elif route['name'] == pair:
      paired = route
  return (evening, paired)

def score_assignments(buses, routes = []):
  total = 0
  assigned = []
  for bus in buses:
    total += abs(get_expected_mileage(bus) - bus['target_mileage'])
    if routes:
      for route in bus['routes']:
        assigned.append(route['name'])
  if routes:
    not_assigned = []
    for route in routes:
      if route['name'] not in assigned:
        total += 10000
  return total

def get_expected_mileage(bus):
  expected = 0
  for route in bus['routes']:
    expected += route['avg_daily_mileage']
  return expected

def process_not_assigned(buses, routes):
  assigned = []
  for bus in buses:
    for route in bus['routes']:
      assigned.append(route['name'])
  not_assigned = []
  for route in routes:
    if route['name'] not in assigned:
      not_assigned.append(route['name'])
  if not_assigned:
    print('!!! Unable to assign all routes !!!')
    for route_name in not_assigned:
      print('Route {} was not assigned'.format(route_name))
    print()
    input("Hit enter to see route assignments")
  return not_assigned

def multiple_routes(bus):
  routes = bus['routes']
  if not routes and not bus['should_run']:
    return "None"
  elif not routes:
    return "SPARE"
  ret = ''
  for route in routes:
    ret += route['name'] + ' (' + str(route['avg_daily_mileage'])[:-2] + '), '
  return ret[:-2]

def output_routes(buses):
  print('BUS\tCURRENT\t\tTARGET\t\tROUTE AND AVG MILEAGE')
  for bus in buses:
    print('{}\t{:<16.0f}{:<16.2f}{}'.format(
      bus['name'],
      bus['current_mileage'],
      bus['target_mileage'],
      multiple_routes(bus)))


if __name__ == "__main__":
  # load the data
  data = load_all_data()

  pp = pprint.PrettyPrinter(indent=2)
  # pp.pprint(data['buses'])
  # exit()

  # calculate how many days from today until end day
  days_left = days_til_end(data['calendar'])
  if days_left == 0:
    days_left = 1

  # calculate the target mileage for each bus
  for bus in data['buses']:
    bus['target_mileage'] = (bus['desired_mileage'] - bus['current_mileage']) / days_left
  
  # pair each bus with a route (or two)
  add_routes(data['buses'], data['routes'])

  # see if any routes were not assigned and output that info
  process_not_assigned(data['buses'], data['routes'])

  # output which routes each bus was assigned to
  output_routes(data['buses'])

  # hold the program open
  input('hit enter to close the program')



# additional features to add next releases:
# option in daily to manually set date you're calculating for
# consider moving away from having evening hard coded in as being named "evening"
#   alex suggests having another column and listing the route(s) it can double with

# known bug:
#   if the bus that wants the least mileage cannot be assigned to the route that has the least mileage
#   that route will not be assigned
#   maybe fix it with a pass afterward to see if there is an unassigned route and unassigned bus
#   work your way up, as it were (can bus that wants least mileage "swap" with bus that wants second last mileage?)

