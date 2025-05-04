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

def obtener_token(url, username, password):
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

#----------------------------------------------------------------
# BUSQUEDA DE RUTAS/VIAGES                                      |
#----------------------------------------------------------------

def search_viatge():
    global ip, port, matricula, token
    api_url = f'http://{ip}:{port}/viatge/?matricula={matricula}'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        viatge = requests.get(api_url, headers=headers)
        if viatge.status_code == 200:
            print('Viatge assignat')
            viatge = viatge.json()
        else:
            print('Viatge no asignat')
            return None
    except requests.RequestException as error:
        print(f"Error: {error}")
    return viatge


def search_parking():
    global ip, port, matricula, token
    api_url = f'http://{ip}:{port}/rutes/parking/?matricula={matricula}'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        parking = requests.get(api_url, headers=headers)
        if parking.status_code == 200:
            print('Parking assignat')
            parking = parking.json()
        else:
            print('Parking no asignat')
            return None
    except requests.RequestException as error:
        print(f"Error: {error}")
    return parking

def search_taller():
    global ip, port, matricula, token
    api_url = f'http://{ip}:{port}/rutes/taller/?matricula={matricula}'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        taller = requests.get(api_url, headers=headers)
        if taller.status_code == 200:
            print('Taller assignat')
            taller = taller.json()
        else:
            print('Taller no asignat')
            return None
    except requests.RequestException as error:
        print(f"Error: {error}")
    return taller

#----------------------------------------------------------------
# EJECUCION DE RUTAS                                            |
#----------------------------------------------------------------

def ejecutar_ruta(ruta, battery, free_travel, averia, viatge_pendent):
    desc_bateria = 0
    for punto in ruta:
        time.sleep(0.5)
        rand_num = random.randint(1,1000)
        if ((rand_num == 1) and (averia == False)):
            averia = True
            break
        if(free_travel == True and viatge_pendent==None):
            viatge = search_viatge()
            if viatge is not None:
                if (not(viatge['lliure'])):
                    viatge_pendent = viatge
                    break
        desc_bateria += 1
        if (desc_bateria == 20):
            battery -= 1
            desc_bateria = 0
        update_pos(punto)
        update_battery(battery)

def ejecutar_ruta_parking(ruta, battery):
    desc_bateria = 0
    for punto in ruta:
        time.sleep(0.5)
        desc_bateria += 1
        if (desc_bateria == 20):
            battery -= 1
            desc_bateria = 0
        update_pos(punto)
        update_battery(battery)

def ejecutar_ruta_taller(ruta):
    for punto in ruta:
        time.sleep(0.5)
        update_pos(punto)

#----------------------------------------------------------------
# UPDATES DE VARIABLES                                          |
#----------------------------------------------------------------

def update_pos(punto):
    global ip, port, matricula, stop, token
    x, y = punto
    location_data = {
        "longitud": x,
        "latitud": y
    }
    api_url = f'http://{ip}:{port}/cotxe/{matricula}/update_location'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    while True:
        try:
            response = requests.put(api_url, headers=headers, json=location_data)
            if response.status_code == 200:
                response_data = response.json()
                ip = response_data["controller"]
                stop = response_data["stop"]
                update_stop(stop)
                if response_data["stop"] == False:
                    break
                print('Ubicación del vehículo actualizada correctamente')
            else:
                print(f"Error al actualizar la ubicación del vehículo: {response.status_code}")
                print(response.json())
        except requests.RequestException as error:
            print(f"Error: {error}")
        
        time.sleep(2)

def update_battery(battery):
    global ip, port, matricula, token
    battery_data = {"bateria": battery}
    api_url = f'http://{ip}:{port}/cotxe/{matricula}/update_battery'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.put(api_url, headers=headers, json=battery_data)
        if response.status_code == 200:
            print('Batería del vehículo actualizada correctamente')
        else:
            print(f"Error al actualizar la batería del vehículo: {response.status_code}")
            print(response.json())
    except requests.RequestException as error:
        print(f"Error: {error}")

def update_averia(averia):
    global ip, port, matricula, token
    averia_data = {"averia": averia}
    api_url = f'http://{ip}:{port}/cotxe/{matricula}/update_averia'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.put(api_url, headers=headers, json=averia_data)
        if response.status_code == 200:
            print('Averia del vehículo actualizada correctamente')
        else:
            print(f"Error al actualizar la averia del vehículo: {response.status_code}")
            print(response.json())
    except requests.RequestException as error:
        print(f"Error: {error}")

def update_onboard(onboard):
    global ip, port, matricula, token
    onboard_data = {"onboard": onboard}
    api_url = f'http://{ip}:{port}/cotxe/{matricula}/update_onboard'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.put(api_url, headers=headers, json=onboard_data)
        if response.status_code == 200:
            print('Onboard del vehículo actualizada correctamente')
        else:
            print(f"Error al actualizar la onboard del vehículo: {response.status_code}")
            print(response.json())
    except requests.RequestException as error:
        print(f"Error: {error}")

def update_stop(stop):
    global ip, port, matricula, token
    stop_data = {"stop": stop}
    api_url = f'http://{ip}:{port}/cotxe/{matricula}/update_stop'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.put(api_url, headers=headers, json=stop_data)
        if response.status_code == 200:
            print('Stop del vehículo actualizada correctamente')
        else:
            print(f"Error al actualizar la stop del vehículo: {response.status_code}")
            print(response.json())
    except requests.RequestException as error:
        print(f"Error: {error}")    

def update_state(state):
    global ip, port, matricula, token 
    disponible = (state == 0)
    disponible_data = {"disponible": disponible}
    api_url = f'http://{ip}:{port}/cotxe/{matricula}/update_state?state={disponible}'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.put(api_url, headers=headers, json=disponible_data)
        if response.status_code == 200:
            print('Estado del vehículo actualizado correctamente')
        else:
            print(f"Error al actualizar el estado del vehículo: {response.status_code}")
            print(response.json())
    except requests.RequestException as error:
        print(f"Error: {error}")


#----------------------------------------------------------------
# CONFIRMACIONES                                                |
#----------------------------------------------------------------

def conf_client():
    global ip, port, matricula, token
    while True:
        api_url = f'http://{ip}:{port}/cotxes/?matricula={matricula}'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        try:
            respuesta = requests.get(api_url, headers=headers)
            respuesta.raise_for_status()
            coche_info = respuesta.json()
            onboard = coche_info['onboard']
            if (onboard):
                break
        except requests.RequestException as error:
            print(f"Error: {error}")
            return False 
        time.sleep(1)  

def conf_viatge():
    global ip, port, matricula, token
    while True:
        api_url = f'http://{ip}:{port}/cotxes/?matricula={matricula}'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        try:
            respuesta = requests.get(api_url, headers=headers)
            respuesta.raise_for_status()
            coche_info = respuesta.json()
            onboard = coche_info['onboard']
            if (not(onboard)):
                break
        except requests.RequestException as error:
            print(f"Error: {error}")
            return False 
        time.sleep(1)      

#----------------------------------------------------------------
# SIMULACIONES                                                  |
#----------------------------------------------------------------       

def parking_cargando(battery):
    while battery < 100:
        time.sleep(0.5)  
        battery += 1
        update_battery(battery)

def taller_arreglando(battery, averia):
   time.sleep(20)
   battery = 100
   update_battery(battery)
   averia = False
   update_averia(averia)

#----------------------------------------------------------------
# FINALIZACION                                                  |
#----------------------------------------------------------------

def viatge_completat():
    global ip, port, matricula, token
    api_url = f'http://{ip}:{port}/viatge/?matricula={matricula}'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    try:
        requests.delete(api_url, headers=headers)
        print('Se ha eliminado el viaje')
    except requests.RequestException as error:
        print(f"Error: {error}")


def run_car(car: dict, q: multiprocessing.Queue, route: Route, token: str):
    """
    Run the car autonomously around the city.
    """
    global api_host
    latitude  = int(car['edgedevice']['latitude'])
    longitude = int(car['edgedevice']['longitude'])
    edge_name = car['edgedevice']['name']
    license   = car['car']['licenseplate']
    print(edge_name)


load_dotenv()
api_host = os.getenv('API_HOST')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

if __name__ == '__main__':
    token_url = '/api/v1/login/access-token'

    route = Route()

    token = obtener_token(api_host+token_url, username, password)
    headers = {
        'accept': 'application/json',
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


while True:
    if (state == states[0]) and (battery > 20) and (averia == False):
        viatge = search_viatge()
        if viatge is not None:
            if (viatge['lliure']):
                free_travel = True
                ruta1 = viatge['ruta1']
                coordenadas_ruta1 = [(ubicacion['longitud'], ubicacion['latitud']) for ubicacion in ruta1]
                ejecutar_ruta(coordenadas_ruta1, battery, free_travel, averia, viatge_pendent)
                if(averia == False):
                    if(viatge_pendent == None):
                        ruta2 = viatge['ruta2']
                        coordenadas_ruta2 = [(ubicacion['longitud'], ubicacion['latitud']) for ubicacion in ruta2]
                        ejecutar_ruta(coordenadas_ruta2, battery, free_travel, averia, viatge_pendent)
                    if(viatge_pendent != None):
                        viatge = viatge_pendent
                        viatge_pendent = {}
                    free_travel = False
            if ((not(viatge['lliure'])) and (battery > 20) and (averia == False)):
                free_travel = False
                update_state(2)
                state = states[2]
                ruta1 = viatge['ruta1']
                coordenadas_ruta1 = [(ubicacion['longitud'], ubicacion['latitud']) for ubicacion in ruta1]
                ejecutar_ruta(coordenadas_ruta1, battery, free_travel, averia, viatge_pendent)
                if(averia == False):
                    conf_client()
                    ruta2 = viatge['ruta2']
                    coordenadas_ruta2 = [(ubicacion['longitud'], ubicacion['latitud']) for ubicacion in ruta2]
                    ejecutar_ruta(coordenadas_ruta2, battery, free_travel, averia, viatge_pendent)
                    if(averia == False):
                        conf_viatge()
                        viatge_completat()
                        update_state(0)
                        state = states[0]
    elif ((state == state[0]) and (battery <= 20) and (averia == False)):
        ruta_parking = search_parking()
        update_state(2)
        state = states[2]
        coordenadas_ruta_parking = [(ubicacion['longitud'], ubicacion['latitud']) for ubicacion in ruta_parking]
        ejecutar_ruta_parking(coordenadas_ruta_parking, battery)
        parking_cargando(battery)
        update_state(0)
        state = states[0]
    elif (averia == True):
        ruta_taller = search_taller()
        update_state(3)
        state = states[3]
        onboard = False
        update_onboard(onboard)
        update_averia(averia)
        coordenadas_ruta_taller = [(ubicacion['longitud'], ubicacion['latitud']) for ubicacion in ruta_taller]
        ejecutar_ruta_taller(coordenadas_ruta_taller)
        taller_arreglando(battery, averia)
        update_averia(averia)
        update_state(0)
        state = states[0]
        viatge_completat()



