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

def refresh_map(
    search_clicks,
    reset_clicks,
    address_value,
    diagonal_value,
):
    if not ctx.triggered_id:
        return (
            default_markers(),
            [],
            [],
            "",
        )
    action = ctx.triggered_id
    if action == "reset-btn":
        return (
            default_markers(),
            [],
            [],
            "Filtros resetados.",
        )

    if not address_value or not address_value.strip():
        return (
            default_markers(),
            [],
            [],
            "Digite um endereço válido.",
        )

    if diagonal_value is None:
        diagonal_value = 5

    coordinates = geocode_user_address(address_value.strip())
    if (
        coordinates is None
        or coordinates[0] is None
        or coordinates[1] is None
    ):
        return (
            default_markers(),
            [],
            [],
            "Endereço não encontrado.",
        )

    latitude, longitude = coordinates
    found_places, area_limits = search_by_diagonal(
        SEARCH_TREE,
        latitude,
        longitude,
        float(diagonal_value),
    )
    marker_group = [
        build_marker(
            latitude,
            longitude,
            "Endereço buscado",
            address_value,
        )
    ]

    for item in found_places:
        marker_group.append(
            build_marker(
                item["lat"],
                item["lon"],
                item["name"],
                f'{item["address"]} | {item["distance_km"]} km',
            )
        )
    highlighted_area = dl.Rectangle(
        bounds=area_limits,
        pathOptions={
            "color": "red",
            "weight": 3,
        },
    )
    return (
        marker_group,
        [highlighted_area],
        found_places,
        f"{len(found_places)} bares encontrados.",
    )

if __name__ == "__main__":
    app.run(debug=True)