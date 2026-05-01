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

app.layout = html.Div(
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "20px",
        "fontFamily": "Arial",
    },
    children=[
        html.H1("Comida Di Buteco 2026"),
        html.Div(
            style={
                "display": "flex",
                "gap": "10px",
                "marginBottom": "20px",
                "flexWrap": "wrap",
            },
            children=[
                dcc.Input(
                    id="address-input",
                    type="text",
                    placeholder="Digite um endereço",
                    style={
                        "width": "350px",
                        "padding": "10px",
                    },
                ),
                dcc.Input(
                    id="diagonal-input",
                    type="number",
                    value=5,
                    min=1,
                    step=1,
                    style={
                        "width": "120px",
                        "padding": "10px",
                    },
                ),
                html.Button(
                    "Buscar",
                    id="search-btn",
                    n_clicks=0,
                ),
                html.Button(
                    "Reset",
                    id="reset-btn",
                    n_clicks=0,
                ),
            ],
        ),
        html.Div(
            id="status",
            style={
                "marginBottom": "15px",
                "fontWeight": "bold",
            },
        ),
        dl.Map(
            center=MAP_CENTER,
            zoom=12,
            style={
                "width": "100%",
                "height": "600px",
                "marginBottom": "20px",
            },
            children=[
                dl.TileLayer(),
                dl.LayerGroup(
                    id="markers-layer",
                    children=default_markers(),
                ),
                dl.LayerGroup(
                    id="rectangle-layer",
                ),
            ],
        ),
        dash_table.DataTable(
            id="results-table",
            columns=[
                {"name": "Nome", "id": "name"},
                {"name": "Endereço", "id": "address"},
                {"name": "Distância (km)", "id": "distance_km"},
            ],
            data=[],
            page_size=12,
            style_cell={
                "textAlign": "left",
                "padding": "8px",
                "whiteSpace": "normal",
            },
            style_header={
                "fontWeight": "bold",
            },
        ),
    ],
)

@app.callback(
    Output("markers-layer", "children"),
    Output("rectangle-layer", "children"),
    Output("results-table", "data"),
    Output("status", "children"),
    Input("search-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    State("address-input", "value"),
    State("diagonal-input", "value"),
)