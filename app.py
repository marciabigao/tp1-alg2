import csv
from dash import Dash, html, dcc, dash_table, ctx
from dash.dependencies import Input, Output, State
import dash_leaflet as dl
from kd_tree import Point, KDTree
from search import search_by_diagonal
from geocode import geocode_user_address

CSV_PATH = "data/butecos_geocoded.csv"
MAP_CENTER = (-19.9167, -43.9345)

def read_locations():
    locations = []

    with open(
        CSV_PATH,
        newline="",
        encoding="utf-8",
    ) as file:
        csv_reader = csv.DictReader(file)

        for entry in csv_reader:
            latitude = entry["lat"].strip()
            longitude = entry["lon"].strip()

            if (
                not latitude
                or not longitude
                or latitude == "None"
                or longitude == "None"
            ):
                continue

            location = Point(
                name=entry["name"].strip(),
                address=entry["address"].strip(),
                lat=float(latitude),
                lon=float(longitude),
            )
            locations.append(location)
    return locations

LOCATIONS = read_locations()
SEARCH_TREE = KDTree(LOCATIONS)

def build_marker(latitude, longitude, heading, details=""):
    popup_items = [html.B(heading)]

    if details:
        popup_items += [
            html.Br(),
            details,
        ]

    return dl.Marker(
        position=[latitude, longitude],
        children=[dl.Popup(popup_items)],
    )

def default_markers():
    markers_list = []

    for place in LOCATIONS:
        markers_list.append(
            build_marker(
                place.lat,
                place.lon,
                place.name,
                place.address,
            )
        )
    return markers_list

app = Dash(__name__)