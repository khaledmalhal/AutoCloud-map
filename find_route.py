from collections import defaultdict
import heapq
import json
import math
import sys

def llegir_fitxer(connexions_nodes) -> dict:
    """
    Llegeix un fitxer JSON que conté informació de les connexions entre nodes i retorna un diccionari de llista d'adjacència.
    
    PRE: connexions_nodes és el nom del fitxer que conté les connexions entre nodes.
    POST: retorna un diccionari que representa la llista d'adjacència dels nodes.
    """
    llista_adjacencia = defaultdict(list)
    with open(connexions_nodes, 'r') as f:
        dades = json.load(f)
        for entrada in dades:
            node1, node2 = str(entrada['node1']), str(entrada['node2'])
            distancia, temps = float(entrada['distancia']), float(entrada['temps'])
            pes_heuristic = heuristic_graf(distancia, temps, 0.5, 0.5)
            llista_adjacencia[node1].append((node2, pes_heuristic, distancia, temps))
    return llista_adjacencia

def heuristic_graf(distancia, temps, w_distancia, w_temps):
    """
    Calcula el valor heurístic donat una distància i temps amb els seus pesos respectius.
    
    PRE: distancia i temps són valors numèrics de distància i temps respectivament.
         w_distancia i w_temps són els pesos per la distància i el temps respectivament.
    POST: retorna el valor heurístic calculat.
    """
    MAX_DISTANCIA, MAX_TEMPS = 250000, 10800
    return (w_distancia * (distancia / MAX_DISTANCIA) + w_temps * (temps / MAX_TEMPS))

def obtenir_coordenades(_id, coordenades_nodes):
    """
    Obté les coordenades d'un node donat el seu ID.
    
    PRE: _id és l'identificador del node.
         coordenades_nodes és un diccionari amb les coordenades dels nodes.
    POST: retorna una tupla amb la longitud i latitud del node.
    """
    return coordenades_nodes.get(_id, (None, None))

def distancia(coord1, coord2):
    """
    Calcula la distància euclidiana entre dues coordenades.
    
    PRE: coord1 i coord2 són tuples que contenen longitud i latitud.
    POST: retorna la distància euclidiana entre les dues coordenades.
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    return math.sqrt((lon2 - lon1)**2 + (lat2 - lat1)**2)

def trobar_node_mes_proper(coordenades_objectiu, coordenades_nodes):
    """
    Troba el node més proper a unes coordenades donades.
    
    PRE: coordenades_objectiu és una tupla amb longitud i latitud de l'objectiu.
         coordenades_nodes és un diccionari amb les coordenades dels nodes.
    POST: retorna l'ID del node més proper a les coordenades objectiu.
    """
    return min(coordenades_nodes, key=lambda _id: distancia(coordenades_objectiu, coordenades_nodes[_id]))

def cerca_cost_uniforme(llista_adjacencia: dict, origen: str, desti: str):
    """
    Implementa l'algorisme de cerca de cost uniforme per trobar el camí òptim entre dos nodes.
    
    PRE: llista_adjacencia és un diccionari que representa la llista d'adjacència dels nodes.
         origen és l'ID del node d'origen.
         desti és l'ID del node de destí.
    POST: retorna el camí òptim, el cost total, la distància total i el temps total.
    """
    cua_prioritat = [(0, 0, 0, origen, [origen])]
    visitats = set()
    while cua_prioritat:
        cost, dist_total, temps_total, node, cami = heapq.heappop(cua_prioritat)
        if node == desti:
            return cami, cost, dist_total, temps_total
        if node not in visitats:
            visitats.add(node)
            for vei, pes, dist, temps in llista_adjacencia[node]:
                if vei not in visitats:
                    heapq.heappush(cua_prioritat, (cost + pes, dist_total + dist, temps_total + temps, vei, cami + [vei]))
    return [], float('inf'), float('inf'), float('inf')

def carregar_coordenades(info_nodes):
    """
    Carrega les coordenades dels nodes des d'un fitxer JSON.
    
    PRE: info_nodes és el nom del fitxer que conté la informació dels nodes.
    POST: retorna un diccionari amb les coordenades dels nodes.
    """
    with open(info_nodes, 'r') as f:
        return {str(entrada['_id']): (entrada['coordenades']['longitud'], entrada['coordenades']['latitud']) for entrada in json.load(f)}

def main(lat_origen, long_origen, lat_desti, long_desti, preu_km, consum_kWh, capacitat_bateria_kWh):
    """
    Funció principal que calcula la ruta òptima entre dos punts donats.
    
    PRE: lat_origen i long_origen són les coordenades de l'origen.
         lat_desti i long_desti són les coordenades del destí.
         preu_km és el preu per quilòmetre.
         consum_kWh és el consum en kWh per quilòmetre.
         capacitat_bateria_kWh és la capacitat de la bateria en kWh.
    POST: retorna un diccionari amb la informació de la ruta òptima.
    """
    connexions_nodes, info_nodes = "inputs/connexio_nodes.json", "inputs/info_nodes.json"
    
    llista_adjacencia = llegir_fitxer(connexions_nodes)
    coordenades_nodes = carregar_coordenades(info_nodes)
    
    node_origen = trobar_node_mes_proper((long_origen, lat_origen), coordenades_nodes)
    node_desti = trobar_node_mes_proper((long_desti, lat_desti), coordenades_nodes)
    
    cami_optim, cost_total, dist_total, temps_total = cerca_cost_uniforme(llista_adjacencia, node_origen, node_desti)
    
    if not cami_optim:
        raise ValueError("No s'ha trobat una ruta òptima.")
    
    if cost_total == float('inf'):
        raise ValueError("La ruta supera l'autonomia del vehicle elèctric-autònom.")
    
    coordenades = [{"longitud": long_origen, "latitud": lat_origen}] + [
        {"longitud": lon, "latitud": lat} for node in cami_optim for lon, lat in [obtenir_coordenades(node, coordenades_nodes)]
    ] + [{"longitud": long_desti, "latitud": lat_desti}]
    
    return {
        "ruta": coordenades,
        "preu_ruta": round(dist_total / 1000 * preu_km, 2),
        "consum": round(dist_total / 1000 * consum_kWh, 2),
        "distancia": round(dist_total / 1000, 2),
        "temps": round(temps_total / 60, 2),
        "bateria_necessaria": round(dist_total / 1000 * consum_kWh / capacitat_bateria_kWh * 100, 2)
    }

if __name__ == '__main__':
    if len(sys.argv) != 8:
        exit(-1)
    lat_origin  = float(sys.argv[1])
    long_origin = float(sys.argv[2])
    lat_dest    = float(sys.argv[3])
    long_dest   = float(sys.argv[4])
    price_km    = float(sys.argv[5])
    consumption = float(sys.argv[6])
    capacity    = float(sys.argv[7])

    print(json.dumps(main(lat_origin, long_origin, lat_dest, long_dest, price_km, consumption, capacity), indent=4))
