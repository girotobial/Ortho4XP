import functools
from math import acos, atan, cos, exp, floor, log, log2, pi, tan

import numpy as np
import pyproj

EARTH_RADIUS = 6378137
EARTH_CIRCUMFRENCE = 2 * EARTH_RADIUS * pi
METERS_PER_DEGREE_LATITUDE = EARTH_CIRCUMFRENCE / 360
DEGREES_LATITUDE_PER_METER = 1 / METERS_PER_DEGREE_LATITUDE


def meters_per_degree_longitude(lattitude: float) -> float:
    """The number of meters in one degree of longitude at a given lattitude

    Parameters
    ----------
    lattitude : float
        The lattitude at which to measure one degree of longitude

    Returns
    -------
    float
        Length of one degree of longitude in meters.
    """
    return round(METERS_PER_DEGREE_LATITUDE * cos(np.radians(lattitude)), 10)


def degrees_longitude_per_meter(lattitude: float) -> float:
    """The number of degrees of longitude that is equivilant to one meter

    Parameters
    ----------
    lattitude : float
        The lattitude at which to convert one meter into degrees of longitude

    Returns
    -------
    float
        One meter in degrees of longitude.
    """
    if lattitude == 90:
        return float("inf")
    return DEGREES_LATITUDE_PER_METER / cos(np.radians(lattitude))


def haversin(angle: float) -> float:
    """The haversine function

    Parameters
    ----------
    angle : float
        Angle in radians

    Returns
    -------
    float
        The haversine of the angle
    """
    return (1 - cos(angle)) * 0.5


def ahaversin(__haversin: float) -> float:
    """The inverse haversine function

    Parameters
    ----------
    __haversin : float

    Returns
    -------
    float
        The inverse haversine (measured in radians) of x
    """
    return acos(1 - 2 * __haversin)


def greatcircle_distance(
    start: tuple[float, float], end: tuple[float, float]
) -> float:
    """[summary]

    Parameters
    ----------
    start : Tuple[float, float]
        (longitude_a, latitude_a)
    end : Tuple[float, float]
        (longitude_b, latitude_b)

    Returns
    -------
    float
        The great circle distance between start and
        end over the earth's surface
    """
    start_radians = np.radians(start)
    end_radians = np.radians(end)

    start_lat = start_radians[1]
    start_long = start_radians[0]
    end_lat = end_radians[1]
    end_long = end_radians[0]

    longitude_difference = end_long - start_long
    lattitude_difference = end_lat - start_lat

    angle = haversin(lattitude_difference) + cos(start_lat) * cos(
        end_lat
    ) * haversin(longitude_difference)

    return EARTH_RADIUS * ahaversin(angle)


epsg = {key: pyproj.CRS(f"epsg:{key}") for key in ("4326", "3857")}


##############################################################################
def webmercator_pixel_size(lat, zoomlevel):
    return EARTH_CIRCUMFRENCE * cos(pi * lat / 180) / (2 ** (zoomlevel + 8))


def webmercator_zoomlevel(lat, pixel_size):
    return floor(
        log2((EARTH_CIRCUMFRENCE * cos(lat * pi / 180)) / pixel_size) - 8
    )


##############################################################################

##############################################################################
def transform(s_epsg, t_epsg, s_x, s_y):
    return pyproj.transform(epsg[s_epsg], epsg[t_epsg], s_x, s_y)


##############################################################################

##############################################################################
@functools.lru_cache(maxsize=2**16)
def gtile_to_wgs84(til_x, til_y, zoomlevel):
    """
    Returns the latitude and longitude of the top left corner of the tile
    (til_x,til_y) at zoom level zoomlevel, using Google's numbering of tiles
    (i.e. origin on top left of the earth map)
    """
    rat_x = til_x / (2 ** (zoomlevel - 1)) - 1
    rat_y = 1 - til_y / (2 ** (zoomlevel - 1))
    lon = rat_x * 180
    lat = 360 / pi * atan(exp(pi * rat_y)) - 90
    return (lat, lon)


##############################################################################

##############################################################################
def wgs84_to_gtile(lat, lon, zoomlevel):
    rat_x = lon / 180
    rat_y = log(tan((90 + lat) * pi / 360)) / pi
    pix_x = round((rat_x + 1) * (2 ** (zoomlevel + 7)))
    pix_y = round((1 - rat_y) * (2 ** (zoomlevel + 7)))
    til_x = pix_x // 256
    til_y = pix_y // 256
    return (til_x, til_y)


##############################################################################

##############################################################################
def wgs84_to_pix(lat, lon, zoomlevel):
    rat_x = lon / 180
    rat_y = log(tan((90 + lat) * pi / 360)) / pi
    pix_x = round((rat_x + 1) * (2 ** (zoomlevel + 7)))
    pix_y = round((1 - rat_y) * (2 ** (zoomlevel + 7)))
    return (pix_x, pix_y)


##############################################################################

##############################################################################
def pix_to_wgs84(pix_x, pix_y, zoomlevel):
    rat_x = pix_x / (2 ** (zoomlevel + 7)) - 1
    rat_y = 1 - pix_y / (2 ** (zoomlevel + 7))
    lon = rat_x * 180
    lat = 360 / pi * atan(exp(pi * rat_y)) - 90
    return (lat, lon)


##############################################################################

##############################################################################
def gtile_to_quadkey(til_x, til_y, zoomlevel):
    """
    Translates Google coding of tiles to Bing Quadkey coding.
    """
    quadkey = ""
    temp_x = til_x
    temp_y = til_y
    for step in range(1, zoomlevel + 1):
        size = 2 ** (zoomlevel - step)
        a = temp_x // size
        b = temp_y // size
        temp_x = temp_x - a * size
        temp_y = temp_y - b * size
        quadkey = quadkey + str(a + 2 * b)
    return quadkey


##############################################################################

##############################################################################
def wgs84_to_orthogrid(lat, lon, zoomlevel):
    ratio_x = lon / 180
    ratio_y = log(tan((90 + lat) * pi / 360)) / pi
    mult = 2 ** (zoomlevel - 5)
    til_x = int((ratio_x + 1) * mult) * 16
    til_y = int((1 - ratio_y) * mult) * 16
    return (til_x, til_y)


##############################################################################

##############################################################################
def st_coord(lat, lon, tex_x, tex_y, zoomlevel):
    """
    ST coordinates of a point in a texture
    """
    ratio_x = lon / 180
    ratio_y = log(tan((90 + lat) * pi / 360)) / pi
    mult = 2 ** (zoomlevel - 5)
    s = (ratio_x + 1) * mult - (tex_x // 16)
    t = 1 - ((1 - ratio_y) * mult - tex_y // 16)
    s = s if s >= 0 else 0
    s = s if s <= 1 else 1
    t = t if t >= 0 else 0
    t = t if t <= 1 else 1
    return (s, t)


##############################################################################


# FIXME: tile_pix_origin() + latlon_to_tile_relative_pix() could be similar to either
#      : wgs84_to_orthogrid() or st_coord(), I'm not sure
def tile_pix_origin(lat, lon, zl):
    tilxleft, tilytop = wgs84_to_gtile(lat + 1, lon, zl)
    latmax, lonmin = gtile_to_wgs84(tilxleft, tilytop, zl)
    return wgs84_to_pix(latmax, lonmin, zl)


def latlon_to_tile_relative_pix(tile_origin, lat, lon, zl):
    pix_x, pix_y = wgs84_to_pix(lat, lon, zl)
    return pix_x - tile_origin[0], pix_y - tile_origin[1]
