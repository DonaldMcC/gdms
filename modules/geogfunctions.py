# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): http://github.com/DonaldMcC/gdms
#
# Demo Sites (Pythonanywhere)
#   http://netdecisionmaking.com/nds/
#   http://netdecisionmaking.com/gdmsdemo/
#
# License Code: MIT
# License Content: Creative Commons Attribution 3.0
#
# Also visit: www.web2py.com
# or Groups: http://groups.google.com/group/web2py
# For details on the web framework used for this development
#
# With thanks to Guido, Massimo and many other that make this sort of thing
# much easier than it used to be
#
# This file largely based on
#
# http://stackoverflow.com/questions/238260/how-to-calculate-the-bounding-box-for-a-given-lat-lng-location

import math
from plugin_location_picker import IS_GEOLOCATION


def getbbox(coord, localrange):
    """ 
    >>> getbbox("Point 56.1, -3.0", 100)
    (55.19961041787985, -4.614338821845118, 57.00038958212015, -1.3856611781548822)

    """
    pt_lat, pt_long = IS_GEOLOCATION.parse_geopoint(coord)
    # pt_lat = 56.100
    # pt_long = -3.0
    minlat, minlong, maxlat, maxlong = boundingBox(pt_lat, pt_long, localrange)

    return minlat, minlong, maxlat, maxlong


def deg2rad(degrees):
    return math.pi*degrees/180.0


def rad2deg(radians):
    return 180.0*radians/math.pi

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]


def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    # Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt((An*An + Bn*Bn)/(Ad*Ad + Bd*Bd))


# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def boundingBox(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)

    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius

    return rad2deg(latMin), rad2deg(lonMin), rad2deg(latMax), rad2deg(lonMax)


def _test():
    import doctest
    doctest.testmod()
        
if __name__ == '__main__':
    # Can run with -v option if you want to confirm tests were run
    _test()
