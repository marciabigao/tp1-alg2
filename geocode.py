import csv
import json
import time
import urllib.parse
import urllib.request
import urllib.error

SOURCE_FILE = "data/butecos_bh.csv"
RESULT_FILE = "data/butecos_geocoded.csv"
ADDRESS_CACHE_FILE = "data/address_cache.json"

#lê o arquivo de cache de endereços geocodificados e retorna um dicionário com os resultados salvos
def read_cache():
    try:
        with open(
            ADDRESS_CACHE_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)
    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):
        return {}

#salva no arquivo de cache os endereços e suas coordenadas já consultadas
def write_cache(cache_data):
    with open(
        ADDRESS_CACHE_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            cache_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

ADDRESS_CACHE = read_cache()

#consulta a API de geocodificação para obter latitude e longitude de um endereço,
#utilizando cache para evitar requisições repetidas
def fetch_coordinates(address: str):
    if address in ADDRESS_CACHE:
        saved_coords = ADDRESS_CACHE[address]
        return (
            saved_coords["lat"],
            saved_coords["lon"],
        )

    encoded_query = urllib.parse.quote(address)
    endpoint = (
        "https://nominatim.openstreetmap.org/search"
        f"?q={encoded_query}"
        "&format=json"
        "&limit=1"
    )

    req = urllib.request.Request(
        endpoint,
        headers={
            "User-Agent": "tp-geometria-ufmg"
        },
    )

    try:
        with urllib.request.urlopen(
            req,
            timeout=10,
        ) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

        if not payload:
            return None, None

        latitude = float(payload[0]["lat"])
        longitude = float(payload[0]["lon"])
        ADDRESS_CACHE[address] = {
            "lat": latitude,
            "lon": longitude,
        }
        write_cache(ADDRESS_CACHE)
        time.sleep(1)
        return latitude, longitude

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
    ):
        return None, None

#monta uma consulta completa adicionando localização padrão
#e delega a busca de coordenadas para a função de geocodificação
def geocode_user_address(address: str):
    full_query = (
        f"{address}, Belo Horizonte, Minas Gerais, Brasil"
    )
    return fetch_coordinates(full_query)

#lê o csv original de bares, geocodifica cada endereço e gera um novo arquivo csv com coordenadas
def generate_geocoded_csv():
    records = []

    with open(
        SOURCE_FILE,
        newline="",
        encoding="utf-8",
    ) as file:
        csv_reader = csv.DictReader(
            file,
            delimiter=";",
        )

        for entry in csv_reader:
            place_name = entry["name"].strip()
            place_address = entry["address"].strip()

            print("Geocodificando:", place_name)

            latitude, longitude = fetch_coordinates(
                place_address
            )
            records.append(
                {
                    "name": place_name,
                    "address": place_address,
                    "lat": latitude,
                    "lon": longitude,
                }
            )
    with open(
        RESULT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        csv_writer = csv.DictWriter(
            file,
            fieldnames=[
                "name",
                "address",
                "lat",
                "lon",
            ],
        )

        csv_writer.writeheader()
        csv_writer.writerows(records)

if __name__ == "__main__":
    generate_geocoded_csv()