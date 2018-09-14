from geopy import Nominatim, GeoNames


def main():

    geolocator = Nominatim(user_agent="specify_your_app_name_here")

    geo_name = GeoNames(username='clarinpl')

    location = geolocator.geocode('Zielonej gorze', language='pl')

    geo_l = geo_name.geocode('Zielona góra')

    print(location.address)
    print((location.latitude, location.longitude))

    print(geo_l.address)
    print((geo_l.latitude, geo_l.longitude))


if __name__ == "__main__":
    # execute only if run as a script
    main()
