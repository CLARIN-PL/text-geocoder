from geopy import Nominatim, GeoNames

from text_geocoder.api.v1.ccl_parser import attributes

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


class Strategy:

    def __call__(self, messenger):
        pass

    def __str__(self):
        return "Trying " + self.__class__.__name__ \
          + " algorithm"

    def apply_location(self, a, loc):
        if loc is not None:
            a['latitude'] = loc.latitude
            a['longitude'] = loc.longitude
            a['address'] = loc.address


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


class AnnotationData(Result, Messenger):

    def __init__(self, data):
        self.data = data

    def __str__(self): return str(self.data)


class ResolveStreet(Strategy):
    def __call__(self, messenger):
        a, scope = messenger
        result = AnnotationData([])  # Dummy data
        if a['chan'] == attributes['n82']['street']:
            cities = []
            house_numbers = []

            for ann in scope['ann']:
                if ann['chan'] == attributes['n82']['city']:
                    cities.append(ann['base'])
                if ann['chan'] == attributes['n82']['house_number']:
                    house_numbers.append(ann['base'])

            if len(cities) == 1 and len(house_numbers) == 1:
                street = house_numbers[0] + ' ' + a['base']
                loc = nominatim.geocode({'city': cities[0], 'street': street}, language='pl')
                if not loc:
                    street = house_numbers[0] + ' ' + a['orth']
                    loc = nominatim.geocode({'city': cities[0], 'street': street}, language='pl')
                if not loc:
                    result.set_successful(0)
                else:
                    self.apply_location(a, loc)
                    result.set_successful(1)
        result.set_successful(0)
        return result


class ResolveCity(Strategy):
    def __call__(self, messenger):
        a, scope = messenger
        result = AnnotationData([])  # Dummy data
        if a['chan'] == attributes['n82']['city']:
            loc = nominatim.geocode({'city': a['base']}, language='pl')
            if not loc:
                loc = nominatim.geocode({'city': a['orth']}, language='pl')

            if not loc:
                result.set_successful(0)
            else:
                self.apply_location(a, loc)
                result.set_successful(1)
        else:
            result.set_successful(0)

        return result


class ResolveCountry(Strategy):
    def __call__(self, messenger):
        a, scope = messenger
        result = AnnotationData([])  # Dummy data
        if a['chan'] == attributes['n82']['city']:
            loc = nominatim.geocode({'country': a['base']}, language='pl')
            if not loc:
                loc = nominatim.geocode({'country': a['orth']}, language='pl')

            if not loc:
                result.set_successful(0)
            else:
                self.apply_location(a, loc)
                result.set_successful(1)
        else:
            result.set_successful(0)
        return result


class ResolveLocation(Strategy):
    def __call__(self, messenger):
        a, scope = messenger

        if a['chan'] != 'nam_num_house':
            loc = nominatim.geocode(a['base'], language='pl')
            if not loc:
                loc = nominatim.geocode(a['orth'], language='pl')

            self.apply_location(a, loc)

        result = AnnotationData([])
        result.set_successful(1)
        return result

