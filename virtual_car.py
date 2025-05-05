import time
import random
import sys
import os
import select
import requests
import multiprocessing
from dotenv import load_dotenv
from find_route import Route

#----------------------------------------------------------------
# FUNCIONES                                                     |
#----------------------------------------------------------------

#----------------------------------------------------------------
# TOKEN                                                         |
#----------------------------------------------------------------

def obtain_token(url, username, password):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'scope': '',
        'client_id': '',
        'client_secret': '',
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json().get('access_token')  # Ajusta esto si el token se encuentra en otra clave del JSON

#-----------------------------+
#       ROUTE EXECUTION       |
#-----------------------------+

def execute_route(car: dict, route: dict, token: str):
    battery = car['car']['battery']
    desc_battery = 0

    for point in route['route']:
        time.sleep(0.5)
        desc_battery += 1
        print(point)
        update_location(car, point, token)
        if (desc_battery == 20):
            battery -= 1
            desc_battery = 0
            update_battery(car, battery, token)


#-----------------------------+
#       UPDATE METHODS        |
#-----------------------------+
def update_location(car: dict, point: tuple, token: str):
    global api_host
    latitude  = point['latitude']
    longitude = point['longitude']
    edge = car['edgedevice']['name']
    location = {
        "latitude": latitude,
        "longitude": longitude
    }
    url = api_host+f'/api/v1/edge/location/{edge}'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    success = False
    while success is False:
        try:
            response = requests.patch(url, headers=headers, json=location)
            response.raise_for_status()
            if response.status_code == 200:
                car['edgedevice']['latitude']  = latitude
                car['edgedevice']['longitude'] = longitude
                success = True
        except requests.RequestException as error:
            print(f"Error: {error}")

        time.sleep(2)


def update_battery(car: dict, battery: int, token: str):
    global api_host
    licenseplate = car['car']['licenseplate']
    url = api_host+f'/api/v1/car/{licenseplate}'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    body = {
        'battery': battery
    }
    success = False
    while success is False:
        try:
            response = requests.patch(url, headers=headers, json=body)
            response.raise_for_status()
            if response.status_code == 200:
                car['car']['battery'] = battery
                success = True
        except requests.RequestException as error:
            print(f"Error: {error}")
        time.sleep(2)

#-----------------------------+
#       CAR SIMULATION        |
#-----------------------------+
def run_car(car: dict, q: multiprocessing.Queue, route: Route, token: str):
    """
    Run the car autonomously around the city.
    """
    while True:
        latitude  = int(car['edgedevice']['latitude'])
        longitude = int(car['edgedevice']['longitude'])
        dest_lat  = latitude
        dest_long = longitude
        while dest_lat == latitude and dest_long == longitude:
            dest_lat, dest_long = route.get_random_node()
        print(f'dest_lat: {dest_lat}, dest_long: {dest_long}')
        car_route = route.find_route(latitude, longitude, dest_lat, dest_long)
        execute_route(car, car_route, token)
        print(f"""Finished route for car {car['car']['licenseplate']}""")



if __name__ == '__main__':
    load_dotenv()
    api_host = os.getenv('API_HOST')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    token_url = '/api/v1/login/access-token'

    route = Route()

    token = obtain_token(api_host+token_url, username, password)
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    result = requests.get(api_host+'/api/v1/car')
    cars = result.json()

    q = []
    p = []
    ctx = multiprocessing.get_context('fork')
    for car in cars['data']:
        q_aux = ctx.Queue()
        p_aux = ctx.Process(target=run_car, args=(car, q_aux, route, token,))
        p_aux.start()
        q.append(q_aux)
        p.append(p_aux)