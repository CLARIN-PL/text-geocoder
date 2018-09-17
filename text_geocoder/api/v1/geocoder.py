from geopy import Nominatim, GeoNames


def find_latitude_and_longitude(locations):

    geolocator = Nominatim(user_agent="ws_clarin_geolocation")

    geo_name = GeoNames(username='clarinpl')

    for l in locations:
        if l['attr'] == 'country_nam':
            position = geolocator.geocode({'country': l['base']}, language='pl')

        elif l['attr'] == 'city_nam':
            position = geolocator.geocode({'city': l['base']}, language='pl')

        elif l['attr'] == 'road_nam':
            position = geolocator.geocode({'street': l['base']}, language='pl')

        else:
            position = geolocator.geocode(l['base'], language='pl')

        if position is None:
            position = geo_name.geocode(l['base'])

        if position is not None:
            l['latitude'] = position.latitude
            l['longitude'] = position.longitude
            l['address'] = position.address

    return locations
