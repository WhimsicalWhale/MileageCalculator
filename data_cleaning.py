# this is just reading in the data from the csv files and parsing them to the format I want to deal with
import re

def parse_as_digit(field):
    if field.isdigit():
        field = float(field)
    else:
        raise Exception("Expecting a whole number, instead got {}".format(field))
    return field

def parse_as_boolean(field):
    if field.lower() in ['true', 't']:
        field = True
    elif field.lower() in ['false', 'f']:
        field = False
    else:
        raise Exception("Expecting a True/False value, instead got {}".format(field))
    return field

def parse_excluded_list(field):
    if field == '':
        field = []
    elif '-' in field:
        field = field.split('-')
    else:
        field = [field]
    return field

def parse_as_date(field):
    if re.match(r'\d\d\/\d\d\/20\d\d$', field) == None:
        raise Exception("Dates must be in MM/DD/YYYY format, got {} instead".format(field))
    return field

parsing_dict = {
    'name': lambda x: x,
    'bus_name': lambda x: x,
    'curr_mileage': parse_as_digit,
    'desired_mileage': parse_as_digit,
    'avg_daily_mileage': parse_as_digit,
    'can_double': parse_as_boolean,
    'available_evening': parse_as_boolean,
    'should_run': parse_as_boolean,
    'weekends': parse_as_boolean,
    'excluded': parse_excluded_list,
    'date': parse_as_date,
    'assigned_route': lambda x: x
}

def is_route(name, routes):
    if name == '':
        return name
    for route in routes:
        if route['name'] == name:
            return name
    raise Exception("You have attempted to manually assign a bus to {}, which is not a real route.".format(name))

def parse_field(field, label):
    return parsing_dict[label](field)

def load_data(filename, labels):
    loaded = []
    with open(filename) as f:
        # toss the column names, we have provided some code ones
        f.readline()
        for line in f:
            details = line.strip().split(',')
            obj = {}
            for i in range(len(labels)):
                if i < len(details):
                    obj[labels[i]] = parse_field(details[i], labels[i])
            loaded.append(obj)
    return loaded

def load_calendar_data():
    calendar = {}
    with open('data/calendar.csv') as f:
        # toss column names
        f.readline()
        calendar['holidays'] = []
        details = f.readline().strip().split(',')
        calendar['holidays'].append(parse_field(details[0], 'date'))
        calendar['start_day'] = parse_field(details[1], 'date')
        calendar['end_day'] = parse_field(details[2], 'date')
        calendar['run_on_weekends'] = parse_field(details[3], 'weekends')
        # any remaining lines have holidays in the first entry
        for line in f:
            calendar['holidays'].append(parse_field(line.strip().split(',')[0], 'date'))
    return calendar

def add_daily_data(data):
    daily_data = load_data('data/daily.csv', ['bus_name','curr_mileage','should_run', 'assigned_route'])
    for i in range(len(data['buses'])):
        for daily in daily_data:
            if data['buses'][i]['name'] == daily['bus_name']:
                # update current_mileage, should_run, and any assigned route
                data['buses'][i]['current_mileage'] = daily['curr_mileage']
                data['buses'][i]['should_run'] = daily['should_run']
                data['buses'][i]['assigned_route'] = is_route(daily['assigned_route'], data['routes'])
    return data

def update_exclusions(buses):
    for bus in buses:
        if 'evening' in bus['excluded']:
            bus['excluded'].append('fake')

def check_route_exclusions(data):
    just_route_names = [route['name'] for route in data['routes']]
    just_route_names.append('fake')
    did_warn = False
    for bus in data['buses']:
        for exRoute in bus['excluded']:
            if not did_warn and exRoute not in just_route_names:
                print('!!! Nonexistent route detected !!!')
            if exRoute not in just_route_names:
                did_warn = True
                print('Bus ' + bus['name'] + ' has route ' + exRoute + ' listed in their exclusions, but that route is not listed in routes.csv.')
    if did_warn:
        input('Results may not be accurate/desired.\n\nHit enter to see route assignments.')

def load_all_data():
    # set up all our variables we're going to use
    data = {}
    bus_labels = [
        'name',
        'desired_mileage',
        'excluded',
        'available_evening'
    ]
    route_labels = [
        'name',
        'avg_daily_mileage',
        'can_double'
    ]

    # parse each csv file and add it to the dictionary
    data['buses'] = load_data('data/buses.csv', bus_labels)
    data['routes'] = load_data('data/routes.csv', route_labels)
    data['calendar'] = load_calendar_data()
    data = add_daily_data(data)

    # fix bus exclusions
    update_exclusions(data['buses'])

    # warning if any of the buses have a route excluded that isn't listed in the routes
    check_route_exclusions(data)

    # return the parsed data
    return data
