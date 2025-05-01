import json
import requests
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

num = 1
len_elements = 0

def cargar_datos(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("El archivo no se encontró.")
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON.")
    return None

def obtener_direccion(lat, lon, access_token, session, cache):
    global num, len_elements
    if (lat, lon) in cache:
        return cache[(lat, lon)]
    
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lon},{lat}.json"
    params = {'access_token': access_token}

    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        datos = response.json()
        if datos['features']:
            direccion = datos['features'][0]['place_name']
            cache[(lat, lon)] = direccion
            num = num + 1
            print('Processed the element %d of %d' % (num, len_elements), end='\r')
            return direccion
        else:
            return "No se encontró ninguna dirección para las coordenadas dadas."
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 429:
            time.sleep(30)  # Pausa durante 5 segundos
            return obtener_direccion(lat, lon, access_token, session, cache)  # Reintentar la solicitud
        else:
            return f"Error en la solicitud: {e}"
            
def procesar_nodo(element, access_token, session, cache):
    nodo_id = element['id']
    lat = element['lat']
    lon = element['lon']
    direccion = obtener_direccion(lat, lon, access_token, session, cache)
    return {"node_id": nodo_id,
            "coordinates": {
                "longitude": lon,
                "latitude": lat
            },
            "address": direccion,
            "status": "disponible"}

def guardar_info_nodos(info_nodos, archivo):
    with open(archivo, 'w', encoding='utf-8') as file:
        json.dump(info_nodos, file, indent=2)

def main():
    global len_elements
    load_dotenv()
    archivo_json = 'Vilanova3.json'
    archivo_salida = 'info_nodos.json'
    access_token = os.getenv("MAPBOX_ACCESS_TOKEN")
    
    data = cargar_datos(archivo_json)
    if not data:
        return

    cache = {}

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)

    info_nodos = []

    len_elements = len(data['elements'])

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(procesar_nodo, element, access_token, session, cache) for element in data['elements'] if element['type'] == 'node']
        for future in as_completed(futures):
            info_nodos.append(future.result())

    guardar_info_nodos(info_nodos, archivo_salida)

if __name__ == "__main__":
    main()

