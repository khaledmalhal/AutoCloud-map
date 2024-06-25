from collections import defaultdict
import heapq
import json
import math

def llegir_fitxer(connexions_nodes) -> dict:
    """
    Llegeix un fitxer JSON amb les connexions entre nodes i crea una llista d'adjacència.
    
    PRE: connexions_nodes és el camí al fitxer JSON que conté les connexions.
    POST: retorna una llista d'adjacència que representa el graf.
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
    Calcula el pes heurístic per una aresta del graf.
    
    PRE: distancia és la distància entre dos nodes.
         temps és el temps de viatge entre dos nodes.
         w_distancia és el pes de la distància en la heurística.
         w_temps és el pes del temps en la heurística.
    POST: retorna el valor heurístic calculat.
    """
    MAX_DISTANCIA, MAX_TEMPS = 250000, 10800
    return (w_distancia * (distancia / MAX_DISTANCIA) + w_temps * (temps / MAX_TEMPS))

def obtenir_coordenades(id_node, coordenades_nodes):
    """
    Obté les coordenades d'un node donat el seu ID.
    
    PRE: id_node és l'identificador del node.
         coordenades_nodes és un diccionari amb les coordenades dels nodes.
    POST: retorna les coordenades del node si existeixen, en cas contrari (None, None).
    """
    return coordenades_nodes.get(id_node, (None, None))

def distancia(coord1, coord2):
    """
    Calcula la distància euclidiana entre dues coordenades.
    
    PRE: coord1 i coord2 són tuples amb la longitud i latitud de les coordenades.
    POST: retorna la distància euclidiana entre coord1 i coord2.
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    return math.sqrt((lon2 - lon1)**2 + (lat2 - lat1)**2)

def trobar_node_mes_proper(coordenades_objectiu, coordenades_nodes):
    """
    Troba el node més proper a unes coordenades donades.
    
    PRE: coordenades_objectiu és una tupla amb la longitud i latitud de les coordenades objectiu.
         coordenades_nodes és un diccionari amb les coordenades dels nodes.
    POST: retorna l'ID del node més proper a les coordenades objectiu.
    """
    return min(coordenades_nodes, key=lambda id_node: distancia(coordenades_objectiu, coordenades_nodes[id_node]))

def cerca_cost_uniforme(llista_adjacencia: dict, origen: str, desti: str):
    """
    Realitza una cerca de cost uniforme per trobar el camí més curt entre dos nodes.
    
    PRE: llista_adjacencia és un diccionari que representa el graf.
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
    
    PRE: info_nodes és el camí al fitxer JSON que conté la informació dels nodes.
    POST: retorna un diccionari amb les coordenades dels nodes.
    """
    with open(info_nodes, 'r') as f:
        return {str(entrada['id_node']): (entrada['coordenades']['longitud'], entrada['coordenades']['latitud']) for entrada in json.load(f)}

def main(lat_origen, long_origen, lat_desti, long_desti, preu_km, consum_kWh, capacitat_bateria_kWh):
    """
    Funció principal que calcula la ruta òptima entre dos punts.
    
    PRE: lat_origen i long_origen són les coordenades de l'origen.
         lat_desti i long_desti són les coordenades del destí.
         preu_km és el cost per quilòmetre.
         consum_kWh és el consum per quilòmetre.
         capacitat_bateria_kWh és la capacitat de la bateria del vehicle.
    POST: retorna un diccionari amb la informació de la ruta òptima.
    """
    connexions_nodes, info_nodes = "/code/app/calcul_rutes/inputs/connexio_nodes.json", "/code/app/calcul_rutes/inputs/info_nodes.json"
    
    llista_adjacencia = llegir_fitxer(connexions_nodes)
    coordenades_nodes = carregar_coordenades(info_nodes)
    
    node_origen = trobar_node_mes_proper((long_origen, lat_origen), coordenades_nodes)
    node_desti = trobar_node_mes_proper((long_desti, lat_desti), coordenades_nodes)
    
    cami_optim, cost_total, dist_total, temps_total = cerca_cost_uniforme(llista_adjacencia, node_origen, node_desti)
    
    if not cami_optim or cost_total == float('inf'):
        raise ValueError("No s'ha trobat una ruta òptima o supera l'autonomia del vehicle elèctric-autònom.")
    
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
    main()
