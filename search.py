import math
from typing import List
from kd_tree import KDTree, KDNode, Point

EARTH_RADIUS = 6371.0

#calcula a distância entre dois pontos geográficos usando a fórmula de haversine.
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

#realiza uma busca ortogonal na kd-tree retornando todos os pontos dentro de um retângulo definido
def range_search(
    kd_tree: KDTree,
    lower_lat: float,
    upper_lat: float,
    lower_lon: float,
    upper_lon: float,
) -> List[Point]:
    collected = []

    def traverse(node: KDNode | None):
        if node is None:
            return
        current_point = node.point
        if (
            lower_lat <= current_point.lat <= upper_lat
            and lower_lon <= current_point.lon <= upper_lon
        ):
            collected.append(current_point)
        if node.axis == 0:
            if lower_lat <= current_point.lat:
                traverse(node.left)
            if current_point.lat <= upper_lat:
                traverse(node.right)
        else:
            if lower_lon <= current_point.lon:
                traverse(node.left)
            if current_point.lon <= upper_lon:
                traverse(node.right)

    traverse(kd_tree.root)
    return collected

#calcula os limites de um retângulo centrado em um ponto a partir do tamanho da diagonal em quilômetros
def compute_rectangle(
    center_latitude: float,
    center_longitude: float,
    diagonal_size_km: float,
):
    half_length = diagonal_size_km / (2 * math.sqrt(2))
    lat_offset = half_length / 111.0
    cosine_lat = math.cos(
        math.radians(center_latitude)
    )

    if abs(cosine_lat) < 1e-8:
        lon_offset = 0
    else:
        lon_offset = half_length / (111.0 * cosine_lat)
    return (
        center_latitude - lat_offset,
        center_latitude + lat_offset,
        center_longitude - lon_offset,
        center_longitude + lon_offset,
    )

#executa a busca por bares dentro da região definida pela diagonal, ordenando os resultados por distância
#e retornando também os limites da área para visualização no mapa
def search_by_diagonal(
    kd_tree: KDTree,
    center_latitude: float,
    center_longitude: float,
    diagonal_size_km: float,
):
    (
        lower_lat,
        upper_lat,
        lower_lon,
        upper_lon,
    ) = compute_rectangle(
        center_latitude,
        center_longitude,
        diagonal_size_km,
    )
    candidates = range_search(
        kd_tree,
        lower_lat,
        upper_lat,
        lower_lon,
        upper_lon,
    )
    results = []

    for point in candidates:
        results.append(
            {
                "name": point.name,
                "address": point.address,
                "lat": point.lat,
                "lon": point.lon,
                "distance_km": round(
                    calculate_distance(
                        center_latitude,
                        center_longitude,
                        point.lat,
                        point.lon,
                    ),
                    2,
                ),
            }
        )

    results.sort(
        key=lambda item: item["distance_km"]
    )

    area_bounds = [
        [lower_lat, lower_lon],
        [upper_lat, upper_lon],
    ]

    return results, area_bounds