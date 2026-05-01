import math
from typing import List
from kd_tree import KDTree, KDNode, Point

EARTH_RADIUS = 6371.0

def calculate_distance(
    lat_a: float,
    lon_a: float,
    lat_b: float,
    lon_b: float,
) -> float:
    lat_a = math.radians(lat_a)
    lon_a = math.radians(lon_a)
    lat_b = math.radians(lat_b)
    lon_b = math.radians(lon_b)
    delta_lat = lat_b - lat_a
    delta_lon = lon_b - lon_a
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_a)
        * math.cos(lat_b)
        * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )
    return EARTH_RADIUS * c