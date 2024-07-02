# Projecte de Rutes i Prevenció d'Accidents

Aquest repositori conté dos scripts principals, `find_route.py` i `prevent_accident.py`, que tenen com a objectiu trobar rutes òptimes i prevenir accidents respectivament. A continuació es descriuen en detall cada un dels scripts.

## find_route.py

Aquest script s'encarrega de trobar la ruta òptima entre dos punts en una xarxa de nodes. Utilitza l'algoritme A* per trobar el camí més curt tenint en compte la distància i el temps.

### Funcionalitats

- **Llegeix les connexions entre nodes des d'un fitxer JSON.**
- **Calcula el valor heurístic utilitzant distància i temps.**
- **Troba les coordenades d'un node donat el seu ID.**
- **Calcula la distància euclidiana entre dues coordenades.**
- **Implementa l'algoritme A* per trobar la ruta òptima.**
- **Genera informació detallada sobre la ruta trobada, incloent cost, consum i bateria necessària.**

### Ús

1. **Execució**:
    ```bash
    python find_route.py
    ```

2. **Funcions principals**:
    - `llegir_fitxer(connexions_nodes)`: Llegeix les connexions entre nodes des d'un fitxer JSON i retorna un diccionari de llista d'adjacència.
    - `heuristic_graf(distancia, temps, w_distancia, w_temps)`: Calcula el valor heurístic donat una distància i temps amb els seus pesos respectius.
    - `obtenir_coordenades(_id, coordenades_nodes)`: Obté les coordenades d'un node donat el seu ID.
    - `distancia(coord1, coord2)`: Calcula la distància euclidiana entre dues coordenades.
    - `a_star(inici, final, connexions, coordenades_nodes)`: Implementa l'algoritme A* per trobar la ruta òptima.

## prevent_accident.py

Aquest script comprova si el següent node en una ruta específica té presència de vianants, amb l'objectiu de prevenir accidents.

### Funcionalitats

- **Troba el següent node en una ruta donada la posició actual.**
- **Comprova si hi ha presència de vianants en el següent node.**

### Ús

1. **Execució**:
    ```bash
    python prevent_accident.py
    ```

2. **Funcions principals**:
    - `trobar_seguent_node(ruta, posicio_actual)`: Troba el següent node en la ruta donada la posició actual.
    - `main(ruta, posicio_actual)`: Funció principal que comprova si el següent node en la ruta té presència de vianants.

## Fitxers de Configuració

- `connexio_nodes.json`: Conté informació de les connexions entre nodes amb distàncies i temps associats.
- `info_nodes.json`: Conté informació addicional sobre els nodes, incloent coordenades i presència de vianants.
