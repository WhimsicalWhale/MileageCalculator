import unittest
import datetime
import copy
from program import *

class test_program(unittest.TestCase):
    routes = [
        {
            'name': 'red',
            'avg_daily_mileage': 10,
            'can_double': True
        },
        {
            'name': 'blue',
            'avg_daily_mileage': 12,
            'can_double': True
        },
        {
            'name': 'green',
            'avg_daily_mileage': 14,
            'can_double': True
        },
        {
            'name': 'evening',
            'avg_daily_mileage': 6,
            'can_double': True
        }
    ]

    buses = [
        {
            'name': 'one',
            'current_mileage': 0,
            'desired_mileage': 100,
            'target_mileage': 10,
            'excluded': [],
            'should_run': True
        },
        {
            'name': 'two',
            'current_mileage': 0,
            'desired_mileage': 200,
            'target_mileage': 20,
            'excluded': [],
            'should_run': True
        },
        {
            'name': 'three',
            'current_mileage': 100,
            'desired_mileage': 250,
            'target_mileage': 15,
            'excluded': [],
            'should_run': True
        },
        {
            'name': 'four',
            'current_mileage': 200,
            'desired_mileage': 250,
            'target_mileage': 5,
            'excluded': [],
            'should_run': True
        }
    ]
    
    def test_days_til_end_no_weekends_holidays(self):
        today = datetime.datetime.now()
        start_day = today - datetime.timedelta(days=5)
        end_day = today + datetime.timedelta(days=5)
        calendar = {
            "start_day": '{:02d}/{:02d}/{:04d}'.format(start_day.month, start_day.day, start_day.year),
            "end_day": '{:02d}/{:02d}/{:04d}'.format(end_day.month, end_day.day, end_day.year),
            "run_on_weekends": True,
            "holidays": []
        }
        total_days = days_til_end(calendar)
        assert total_days == 4
    
    def test_days_til_end_no_weekends_one_holiday(self):
        today = datetime.datetime.now()
        start_day = today - datetime.timedelta(days=5)
        end_day = today + datetime.timedelta(days=5)
        holiday = today + datetime.timedelta(days=2)
        calendar = {
            "start_day": '{:02d}/{:02d}/{:04d}'.format(start_day.month, start_day.day, start_day.year),
            "end_day": '{:02d}/{:02d}/{:04d}'.format(end_day.month, end_day.day, end_day.year),
            "run_on_weekends": True,
            "holidays": [
                '{:02d}/{:02d}/{:04d}'.format(holiday.month, holiday.day, holiday.year)
            ]
        }
        total_days = days_til_end(calendar)
        assert total_days == 3
    
    def test_days_til_end_no_weekends_multiple_holiday(self):
        today = datetime.datetime.now()
        start_day = today - datetime.timedelta(days=5)
        end_day = today + datetime.timedelta(days=7)
        holiday1 = today + datetime.timedelta(days=2)
        holiday2 = today + datetime.timedelta(days=3)
        calendar = {
            "start_day": '{:02d}/{:02d}/{:04d}'.format(start_day.month, start_day.day, start_day.year),
            "end_day": '{:02d}/{:02d}/{:04d}'.format(end_day.month, end_day.day, end_day.year),
            "run_on_weekends": True,
            "holidays": [
                '{:02d}/{:02d}/{:04d}'.format(holiday1.month, holiday1.day, holiday1.year),
                '{:02d}/{:02d}/{:04d}'.format(holiday2.month, holiday2.day, holiday2.year)
            ]
        }
        total_days = days_til_end(calendar)
        assert total_days == 4
    
    def test_days_til_end_weekends_no_holiday(self):
        today = datetime.datetime.now()
        start_day = today - datetime.timedelta(days=1) # yesterday
        end_day = today + datetime.timedelta(days=7) # one week
        calendar = {
            "start_day": '{:02d}/{:02d}/{:04d}'.format(start_day.month, start_day.day, start_day.year),
            "end_day": '{:02d}/{:02d}/{:04d}'.format(end_day.month, end_day.day, end_day.year),
            "run_on_weekends": False,
            "holidays": []
        }
        total_days = days_til_end(calendar)
        assert total_days == 4

        end_day = today + datetime.timedelta(days=14) # two weeks
        calendar['end_day'] = '{:02d}/{:02d}/{:04d}'.format(end_day.month, end_day.day, end_day.year)
        total_days = days_til_end(calendar)
        assert total_days == 9
    
    def test_days_til_end_weekends_holiday(self):
        today = datetime.datetime.now()
        start_day = today - datetime.timedelta(days=1) # yesterday
        end_day = today + datetime.timedelta(days=14) # two weeks
        # make sure it isn't a weekend that's already excluded
        holiday = next_not_weekend(today)
        calendar = {
            "start_day": '{:02d}/{:02d}/{:04d}'.format(start_day.month, start_day.day, start_day.year),
            "end_day": '{:02d}/{:02d}/{:04d}'.format(end_day.month, end_day.day, end_day.year),
            "run_on_weekends": False,
            "holidays": [
                '{:02d}/{:02d}/{:04d}'.format(holiday.month, holiday.day, holiday.year)
            ]
        }
        total_days = days_til_end(calendar)
        assert total_days == 8
    
    def test_days_til_end_ran_on_holiday(self):
        today = datetime.datetime.now()
        start_day = today - datetime.timedelta(days=5)
        end_day = today + datetime.timedelta(days=7)
        holiday1 = today
        holiday2 = today + datetime.timedelta(days=2)
        calendar = {
            "start_day": '{:02d}/{:02d}/{:04d}'.format(start_day.month, start_day.day, start_day.year),
            "end_day": '{:02d}/{:02d}/{:04d}'.format(end_day.month, end_day.day, end_day.year),
            "run_on_weekends": True,
            "holidays": [
                '{:02d}/{:02d}/{:04d}'.format(holiday1.month, holiday1.day, holiday1.year),
                '{:02d}/{:02d}/{:04d}'.format(holiday2.month, holiday2.day, holiday2.year)
            ]
        }
        total_days = days_til_end(calendar)
        assert total_days == 4
    
    def test_days_til_end_ran_on_weekend(self):
        today = datetime.datetime.now()
        today = next_weekend(today)
        start_day = today - datetime.timedelta(days=1) # yesterday
        end_day = today + datetime.timedelta(days=7) # one week
        calendar = {
            "start_day": '{:02d}/{:02d}/{:04d}'.format(start_day.month, start_day.day, start_day.year),
            "end_day": '{:02d}/{:02d}/{:04d}'.format(end_day.month, end_day.day, end_day.year),
            "run_on_weekends": False,
            "holidays": []
        }
        total_days = days_til_end(calendar)
        assert total_days == 5

        end_day = today + datetime.timedelta(days=14) # two weeks
        calendar['end_day'] = '{:02d}/{:02d}/{:04d}'.format(end_day.month, end_day.day, end_day.year)
        total_days = days_til_end(calendar)
        assert total_days == 10
    
    def test_get_expected_mileage(self):
        bus = {
            'routes': [
                { 'avg_daily_mileage': 12 }
            ]
        }
        assert get_expected_mileage(bus) == 12

        bus['routes'].append({ 'avg_daily_mileage': 4 })
        assert get_expected_mileage(bus) == 16
    
    def test_merge_pair(self):
        first_merge = copy.deepcopy(self.routes)
        merge_pair(first_merge, 'red')

        assert len(first_merge) == 3
        for route in first_merge:
            if route['name'] == 'fake':
                assert route['avg_daily_mileage'] == 16
            elif route['name'] == 'blue':
                assert route['avg_daily_mileage'] == 12
            elif route['name'] == 'green':
                assert route['avg_daily_mileage'] == 14
            else:
                assert False
        
        second_merge = copy.deepcopy(self.routes)
        merge_pair(second_merge, 'blue')

        assert len(second_merge) == 3
        for route in second_merge:
            if route['name'] == 'fake':
                assert route['avg_daily_mileage'] == 18
            elif route['name'] == 'red':
                assert route['avg_daily_mileage'] == 10
            elif route['name'] == 'green':
                assert route['avg_daily_mileage'] == 14
            else:
                assert False
        
        third_merge = copy.deepcopy(self.routes)
        merge_pair(third_merge, 'green')

        assert len(third_merge) == 3
        for route in third_merge:
            if route['name'] == 'fake':
                assert route['avg_daily_mileage'] == 20
            elif route['name'] == 'red':
                assert route['avg_daily_mileage'] == 10
            elif route['name'] == 'blue':
                assert route['avg_daily_mileage'] == 12
            else:
                assert False
        
        fourth_merge = copy.deepcopy(self.routes)
        merge_pair(fourth_merge, None)

        assert len(fourth_merge) == 4
        for route in fourth_merge:
            if route['name'] == 'red':
                assert route['avg_daily_mileage'] == 10
            elif route['name'] == 'blue':
                assert route['avg_daily_mileage'] == 12
            elif route['name'] == 'green':
                assert route['avg_daily_mileage'] == 14
            elif route['name'] == 'evening':
                assert route['avg_daily_mileage'] == 6
            else:
                assert False
    
    def test_split_pair(self):
        for route in self.routes:
            if route['name'] != 'evening':
                result = split_pair(self.routes, route['name'])
                assert len(result) == 2
                assert result[0]['name'] == 'evening'
                assert result[1]['name'] == route['name']
    
    def test_all_evening_pairings(self):
        result = all_evening_pairings(self.routes)
        assert len(result) == 3
        for route in self.routes:
            if route['name'] != 'evening':
                assert route['name'] in result

        nRoutes = copy.deepcopy(self.routes)
        nRoutes[0]['can_double'] = False
        result = all_evening_pairings(nRoutes)
        assert len(result) == 2
        for route in self.routes:
            if route['name'] != 'evening' and route['name'] != 'red':
                assert route['name'] in result
        
        nRoutes[1]['can_double'] = False
        result = all_evening_pairings(nRoutes)
        assert len(result) == 1
        assert result[0] == 'green'
    
    def test_add_routes_basic_none_evening(self):
        nBuses = copy.deepcopy(self.buses)
        add_routes_basic(nBuses, self.routes, None)
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'red'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'green'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'blue'
            elif bus['name'] == 'four':
                assert bus['routes'][0]['name'] == 'evening'
            else:
                assert False
    
    def test_add_routes_basic_red_evening(self):
        nBuses = copy.deepcopy(self.buses)
        add_routes_basic(nBuses, self.routes, 'red')
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'blue'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'evening'
                assert bus['routes'][1]['name'] == 'red'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'green'
            elif bus['name'] == 'four':
                assert len(bus['routes']) == 0
            else:
                assert False
    
    def test_add_routes_basic_blue_evening(self):
        nBuses = copy.deepcopy(self.buses)
        add_routes_basic(nBuses, self.routes, 'blue')
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'red'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'evening'
                assert bus['routes'][1]['name'] == 'blue'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'green'
            elif bus['name'] == 'four':
                assert len(bus['routes']) == 0
            else:
                assert False
    
    def test_add_routes_basic_green_evening(self):
        nBuses = copy.deepcopy(self.buses)
        add_routes_basic(nBuses, self.routes, 'green')
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'red'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'evening'
                assert bus['routes'][1]['name'] == 'green'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'blue'
            elif bus['name'] == 'four':
                assert len(bus['routes']) == 0
            else:
                assert False
    
    def test_add_routes_one(self):
        nBuses = copy.deepcopy(self.buses)
        add_routes(nBuses, self.routes)
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'red'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'evening'
                assert bus['routes'][1]['name'] == 'blue'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'green'
            elif bus['name'] == 'four':
                assert len(bus['routes']) == 0
    
    def test_add_routes_two(self):
        nBuses = copy.deepcopy(self.buses)
        nBuses[3] = {
            'name': 'four',
            'current_mileage': 200,
            'desired_mileage': 300,
            'target_mileage': 11,
            'excluded': []
        }
        add_routes(nBuses, self.routes)
        for bus in nBuses:
            if bus['name'] == 'one':
                assert len(bus['routes']) == 0
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'evening'
                assert bus['routes'][1]['name'] == 'blue'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'green'
            elif bus['name'] == 'four':
                assert bus['routes'][0]['name'] == 'red'
    
    def test_add_routes_with_exclusions(self):
        nBuses = copy.deepcopy(self.buses)
        nBuses[0]['excluded'].append('red')
        add_routes(nBuses, self.routes)
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'blue'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'evening'
                assert bus['routes'][1]['name'] == 'red'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'green'
            elif bus['name'] == 'four':
                assert len(bus['routes']) == 0
            else:
                assert False
    
        nBuses = copy.deepcopy(self.buses)
        nBuses[1]['excluded'].append('evening')
        nBuses[1]['excluded'].append('fake')
        add_routes(nBuses, self.routes)
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'red'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'green'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'blue'
            elif bus['name'] == 'four':
                assert bus['routes'][0]['name'] == 'evening'
            else:
                assert False
    
    def test_will_exceed_desired_mileage(self):
        nBuses = [
            {
                'name': 'one',
                'current_mileage': 90,
                'desired_mileage': 100,
                'target_mileage': 1,
                'excluded': [],
                'should_run': True
            },
            {
                'name': 'two',
                'current_mileage': 190,
                'desired_mileage': 200,
                'target_mileage': 1,
                'excluded': [],
                'should_run': True
            },
            {
                'name': 'three',
                'current_mileage': 225,
                'desired_mileage': 250,
                'target_mileage': 2,
                'excluded': [],
                'should_run': True
            },
            {
                'name': 'four',
                'current_mileage': 200,
                'desired_mileage': 250,
                'target_mileage': 5,
                'excluded': [],
                'should_run': True
            }
        ]
        add_routes(nBuses, self.routes)
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'red'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'evening'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'blue'
            elif bus['name'] == 'four':
                assert bus['routes'][0]['name'] == 'green'
            else:
                assert False
    
    def test_has_exceeded_desired_mileage(self):
        nBuses = [
            {
                'name': 'one',
                'current_mileage': 120,
                'desired_mileage': 100,
                'target_mileage': -2,
                'excluded': [],
                'should_run': True
            },
            {
                'name': 'two',
                'current_mileage': 200,
                'desired_mileage': 200,
                'target_mileage': 0,
                'excluded': [],
                'should_run': True
            },
            {
                'name': 'three',
                'current_mileage': 300,
                'desired_mileage': 250,
                'target_mileage': -5,
                'excluded': [],
                'should_run': True
            },
            {
                'name': 'four',
                'current_mileage': 200,
                'desired_mileage': 250,
                'target_mileage': 5,
                'excluded': [],
                'should_run': True
            }
        ]
        add_routes(nBuses, self.routes)
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'blue'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'green'
            elif bus['name'] == 'three':
                assert len(bus['routes']) == 0
            elif bus['name'] == 'four':
                assert bus['routes'][0]['name'] == 'evening'
                assert bus['routes'][1]['name'] == 'red'
            else:
                assert False
    
    def test_not_enough_buses(self):
        nBuses = copy.deepcopy(self.buses)
        nRoutes = copy.deepcopy(self.routes)
        nRoutes.append({
            'name': 'yellow',
            'avg_daily_mileage': 8,
            'can_double': True
        })
        nRoutes.append({
            'name': 'white',
            'avg_daily_mileage': 10,
            'can_double': True
        })
        add_routes(nBuses, nRoutes)
        for bus in nBuses:
            if bus['name'] == 'one':
                assert bus['routes'][0]['name'] == 'red'
            elif bus['name'] == 'two':
                assert bus['routes'][0]['name'] == 'evening'
                assert bus['routes'][1]['name'] == 'blue'
            elif bus['name'] == 'three':
                assert bus['routes'][0]['name'] == 'green'
            elif bus['name'] == 'four':
                assert bus['routes'][0]['name'] == 'white'
            else:
                assert False

    def test_process_not_assigned_everything_assigned(self):
        nBuses = copy.deepcopy(self.buses)
        add_routes(nBuses, self.routes)
        result = process_not_assigned(nBuses, self.routes)
        assert len(result) == 0
    
    def test_process_not_assigned_one_not_assigned(self):
        nBuses = copy.deepcopy(self.buses)
        nRoutes = copy.deepcopy(self.routes)
        nRoutes.append({
            'name': 'yellow',
            'avg_daily_mileage': 8,
            'can_double': True
        })
        nRoutes.append({
            'name': 'white',
            'avg_daily_mileage': 10,
            'can_double': True
        })
        add_routes(nBuses, nRoutes)
        result = process_not_assigned(nBuses, nRoutes)
        assert len(result) == 1
        assert result[0] == 'yellow'
    
    def test_bus_should_run(self):
        nBuses = copy.deepcopy(self.buses)



# any helper functions to be used in unit tests
def next_not_weekend(day):
    next_day = day + datetime.timedelta(days=1)
    while next_day.weekday() >= 5:
        next_day = next_day + datetime.timedelta(days=1)
    return next_day

def next_weekend(day):
    next_day = day + datetime.timedelta(days=1)
    while next_day.weekday() < 5:
        next_day = next_day + datetime.timedelta(days=1)
    return next_day
