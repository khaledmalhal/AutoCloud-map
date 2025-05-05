from collections import defaultdict
import heapq
import json
import math
import sys
import random

class Route():
    def __init__(self):
        self.connection_nodes, self.info_nodes = "inputs/connection_nodes.json", "inputs/info_nodes.json"
    
        self.nodes = []
        self.adjacent_list     = self.read_file(self.connection_nodes)
        self.coordinates_nodes = self.load_coordinates(self.info_nodes)

    def read_file(self, connexions_nodes) -> dict:
        """
        Llegeix un fitxer JSON que conté informació de les connexions entre nodes i retorna un diccionari de llista d'adjacència.
        
        PRE: connexions_nodes és el nom del fitxer que conté les connexions entre nodes.
        POST: retorna un diccionari que representa la llista d'adjacència dels nodes.
        """
        adjacent_list = defaultdict(list)
        with open(connexions_nodes, 'r') as f:
            dades = json.load(f)
            for entrada in dades:
                node1, node2 = str(entrada['node1']), str(entrada['node2'])
                distancia, temps = float(entrada['distance']), float(entrada['time'])
                pes_heuristic = self.heuristc_graph(distancia, temps, 0.5, 0.5)
                adjacent_list[node1].append((node2, pes_heuristic, distancia, temps))
        return adjacent_list

    def heuristc_graph(self, distancia, temps, w_distancia, w_temps):
        """
        Calcula el valor heurístic donat una distància i temps amb els seus pesos respectius.
        
        PRE: distancia i temps són valors numèrics de distància i temps respectivament.
            w_distancia i w_temps són els pesos per la distància i el temps respectivament.
        POST: retorna el valor heurístic calculat.
        """
        MAX_DISTANCIA, MAX_TEMPS = 250000, 10800
        return (w_distancia * (distancia / MAX_DISTANCIA) + w_temps * (temps / MAX_TEMPS))

    def obtain_coordinates(self, _id, coordinates_nodes):
        """
        Obté les coordenades d'un node donat el seu ID.
        
        PRE: _id és l'identificador del node.
            coordenades_nodes és un diccionari amb les coordenades dels nodes.
        POST: retorna una tupla amb la longitud i latitud del node.
        """
        return coordinates_nodes.get(_id, (None, None))

    def distance(self, coord1, coord2):
        """
        Calcula la distància euclidiana entre dues coordenades.
        
        PRE: coord1 i coord2 són tuples que contenen longitud i latitud.
        POST: retorna la distància euclidiana entre les dues coordenades.
        """
        lon1, lat1 = coord1
        lon2, lat2 = coord2
        return math.sqrt((lon2 - lon1)**2 + (lat2 - lat1)**2)

    def find_closest_node(self, dest_coordinates, coordinates_nodes):
        """
        Troba el node més proper a unes coordenades donades.
        
        PRE: coordenades_objectiu és una tupla amb longitud i latitud de l'objectiu.
            coordenades_nodes és un diccionari amb les coordenades dels nodes.
        POST: retorna l'ID del node més proper a les coordenades objectiu.
        """
        return min(coordinates_nodes, key=lambda _id: self.distance(dest_coordinates, coordinates_nodes[_id]))

    def uniform_cost_search(self, adjacent_list: dict, origin: str, dest: str):
        """
        Implementa l'algorisme de cerca de cost uniforme per trobar el camí òptim entre dos nodes.
        
        PRE: llista_adjacencia és un diccionari que representa la llista d'adjacència dels nodes.
            origen és l'ID del node d'origen.
            desti és l'ID del node de destí.
        POST: retorna el camí òptim, el cost total, la distància total i el temps total.
        """
        priority_queue = [(0, 0, 0, origin, [origin])]
        visitats = set()
        while priority_queue:
            cost, dist_total, temps_total, node, cami = heapq.heappop(priority_queue)
            if node == dest:
                return cami, cost, dist_total, temps_total
            if node not in visitats:
                visitats.add(node)
                for vei, pes, dist, temps in adjacent_list[node]:
                    if vei not in visitats:
                        heapq.heappush(priority_queue, (cost + pes, dist_total + dist, temps_total + temps, vei, cami + [vei]))
        return [], float('inf'), float('inf'), float('inf')

    def load_coordinates(self, info_nodes):
        """
        Carrega les coordenades dels nodes des d'un fitxer JSON.
        
        PRE: info_nodes és el nom del fitxer que conté la informació dels nodes.
        POST: retorna un diccionari amb les coordenades dels nodes.
        """
        with open(info_nodes, 'r') as f:
            obj = {str(entrada['node_id']): (entrada['coordinates']['longitude'], entrada['coordinates']['latitude']) for entrada in json.load(f)}
        self.nodes = list(obj.keys())
        return obj

    def get_random_node(self):
        """
        Obtain a random node from the dictionary 'self.coordinates_nodes'
        """
        rand = random.randint(0, len(self.nodes))
        return self.coordinates_nodes[self.nodes[rand]]

    def find_route(self, lat_origin, long_origin, lat_dest, long_dest):
        node_origin = self.find_closest_node((long_origin, lat_origin), self.coordinates_nodes)
        node_dest   = self.find_closest_node((long_dest, lat_dest), self.coordinates_nodes)
        print(f'node_origin: {node_origin}, node_dest: {node_dest}')

        optimal_route, cost_total, dist_total, time_total = self.uniform_cost_search(self.adjacent_list, node_origin, node_dest)
        if not optimal_route:
            raise ValueError("No optimal route has been found.")
        
        if cost_total == float('inf'):
            raise ValueError("The route exceeds the autonomy of the vehicle.")
        
        coordinates = [{"longitude": long_origin, "latitude": lat_origin}] + [
            {"longitude": lon, "latitude": lat} for node in optimal_route for lon, lat in [self.obtain_coordinates(node, self.coordinates_nodes)]
        ] + [{"longitude": long_dest, "latitude": lat_dest}]
        
        return {
            "route": coordinates,
            #"consumption": round(dist_total / 1000 * consum_kWh, 2),
            "distance": round(dist_total / 1000, 2),
            "time": round(time_total / 60, 2),
            #"necessary_battery": round(dist_total / 1000 * consum_kWh / capacitat_bateria_kWh * 100, 2)
        }

if __name__ == '__main__':
    route = Route()
    if len(sys.argv) != 8:
        exit(-1)
    lat_origin  = float(sys.argv[1])
    long_origin = float(sys.argv[2])
    lat_dest    = float(sys.argv[3])
    long_dest   = float(sys.argv[4])
    price_km    = float(sys.argv[5])
    consumption = float(sys.argv[6])
    capacity    = float(sys.argv[7])

    print(json.dumps(route.find_route(lat_origin, long_origin, lat_dest, long_dest, price_km, consumption, capacity), indent=4))
