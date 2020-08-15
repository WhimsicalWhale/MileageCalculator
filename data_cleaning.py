# this is just reading in the data from the csv files and parsing them to the format I want to deal with
import re

def parse_field(field, label):
    if label == 'name':
        # take whatever string they put in
        return field
    elif label in ['desired_mileage', 'avg_daily_mileage']:
        # must be a number
        if field.isdigit():
            field = float(field)
        else:
            raise Exception("Expecting a whole number, instead got {}".format(field))
    elif label in ['can_double', 'available_evening', 'weekends']:
        # parse it into a boolean
        if field.lower() in ['true', 't']:
            field = True
        elif field.lower() in ['false', 'f']:
            field = False
        else:
            raise Exception("Expecting a True/False value, instead got {}".format(field))
    elif label == 'excluded':
        if field == '':
            field = []
        elif '-' in field:
            field = field.split('-')
        else:
            field = [field]
    elif label == 'date':
        if re.match(r'\d\d\/\d\d\/20\d\d$', field) == None:
            raise Exception("Dates must be in MM/DD/YYYY format, got {} instead".format(field))
    return field

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
    daily_data = load_data('data/daily.csv', ['bus_name','curr_mileage','should_run'])
    for i in range(len(data['buses'])):
        for daily in daily_data:
            if data['buses'][i]['name'] == daily['bus_name']:
                # update current_mileage and should_run
                data['buses'][i]['current_mileage'] = daily['curr_mileage']
                data['buses'][i]['should_run'] = daily['should_run']
    return data

def update_exclusions(buses):
    for bus in buses:
        if 'evening' in bus['excluded']:
            bus['excluded'].append('fake')    

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

    # return the parsed data
    return data
