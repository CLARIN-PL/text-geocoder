import pickle

from geopy import Nominatim, GeoNames

from text_geocoder.api.v1.ccl_parser import attributes
from text_geocoder.extensions import redis_store

nominatim = Nominatim(user_agent="ws_clarin_geolocation")
geo_name = GeoNames(username='clarinpl')


def find_latitude_and_longitude(annotations):

    solutions = []
    ChainLink(solutions, ResolveStreet())
    ChainLink(solutions, ResolveCity())
    ChainLink(solutions, ResolveCountry())
    ChainLink(solutions, ResolveLocation())

    for ann in annotations:
        for a in ann['ann']:
            item = a, ann
            solutions[0](item)

    return annotations


# Carry the information into the strategy:
class Messenger:
    pass


# The Result object carries the result data and
# whether the strategy was successful:
class Result:
    def __init__(self):
        self.succeeded = 0

    def is_successful(self):
        return self.succeeded

    def set_successful(self, succeeded):
        self.succeeded = succeeded


class ResultData(Result, Messenger):

    def __init__(self, data):
        self.data = data

    def __str__(self): return str(self.data)


class Strategy:

    def __init__(self):
        self.result = ResultData([])

    def __call__(self, messenger):
        pass

    def __str__(self):
        return "Trying " + self.__class__.__name__ \
          + " algorithm"

    def get_from_cache(self, a):
        key = a['orth'] + '_' + a['base'] + '_' + a['chan']
        val = redis_store.get(key)
        if val:
            self.result.set_successful(1)
            print('Found in store')
            print(val)
            return val

        return None

    def save_to_cache(self, a, loc):
        key = a['orth'] + '_' + a['base'] + '_' + a['chan']
        dump = pickle.dump(loc)
        redis_store.set(key, dump)

    def apply_location(self, a, loc):
        if loc is not None:
            item = {'latitude': loc.latitude,
                    'longitude': loc.longitude,
                    'address':  loc.address}

            self.save_to_cache(a, loc)
            a['locations'].append(item)


# Manage the movement through the chain and
# find a successful result:
class ChainLink:
    def __init__(self, chain, strategy):
        self.strategy = strategy
        self.chain = chain
        self.chain.append(self)

    def next(self):
        # Where this link is in the chain:
        location = self.chain.index(self)
        if not self.end():
            return self.chain[location + 1]

    def end(self):
        return (self.chain.index(self) + 1 >=
                len(self.chain))

    def __call__(self, messenger):
        r = self.strategy(messenger)
        if r.is_successful() or self.end():
            return r
        return self.next()(messenger)


class ResolveStreet(Strategy):
    def __call__(self, messenger):
        a, scope = messenger

        cached = self.get_from_cache(a)
        if cached is not None:
            return self.result

        if a['chan'] == attributes['n82']['street']:
            cities = []
            house_numbers = []

            for ann in scope['ann']:
                if ann['chan'] == attributes['n82']['city']:
                    cities.append(ann['base'])
                if ann['chan'] == attributes['n82']['house_number']:
                    house_numbers.append(ann['base'])

            for c in cities:
                for hn in house_numbers:
                    street = hn + ' ' + a['base']
                    loc = nominatim.geocode({'city': c, 'street': street}, language='pl')
                    if not loc:
                        street = hn + ' ' + a['orth']
                        loc = nominatim.geocode({'city': c, 'street': street}, language='pl')
                    if loc:
                        self.apply_location(a, loc)
                        self.result.set_successful(1)
        self.result.set_successful(0)
        return self.result


class ResolveCity(Strategy):
    def __call__(self, messenger):
        a, scope = messenger

        cached = self.get_from_cache(a)
        if cached is not None:
            return self.result

        if a['chan'] == attributes['n82']['city']:
            loc = nominatim.geocode({'city': a['base']}, language='pl')
            if not loc:
                loc = nominatim.geocode({'city': a['orth']}, language='pl')

            if loc:
                self.apply_location(a, loc)
                self.result.set_successful(1)

        self.result.set_successful(0)
        return self.result


class ResolveCountry(Strategy):
    def __call__(self, messenger):
        a, scope = messenger

        cached = self.get_from_cache(a)
        if cached is not None:
            return self.result

        if a['chan'] == attributes['n82']['city']:
            loc = nominatim.geocode({'country': a['base']}, language='pl')
            if not loc:
                loc = nominatim.geocode({'country': a['orth']}, language='pl')

            if loc:
                self.apply_location(a, loc)
                self.result.set_successful(1)

        self.result.set_successful(0)
        return self.result


class ResolveLocation(Strategy):
    def __call__(self, messenger):
        a, scope = messenger

        cached = self.get_from_cache(a)
        if cached is not None:
            return self.result

        if a['chan'] != 'nam_num' and a['chan'] != 'nam_num_house':
            loc = nominatim.geocode(a['base'], language='pl')
            if not loc:
                loc = nominatim.geocode(a['orth'], language='pl')

            self.apply_location(a, loc)

        self.result.set_successful(1)
        return self.result

