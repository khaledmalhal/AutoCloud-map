from pathlib import Path
import json
import random
import time

def alternar_vianants(nodes):
    """
    Alterna l'estat de la bandera 'vianants' per a cada node a la llista de nodes.

    PRE: nodes és una llista de diccionaris, cada diccionari representa un node amb una clau 'vianants'.
    POST: modifica els diccionaris in situ canviant el valor de 'vianants' de True a False i viceversa.
    """
    for node in nodes:
        node['vianants'] = not node.get('vianants', False)

def main():
    """
    Funció main que alterna les banderes de vianants per a un subconjunt de nodes al fitxer JSON.

    PRE: L'arxiu 'inputs/info_nodes.json' ha d'existir i tenir una llista de nodes amb la clau 'vianants'.
    POST: Modifica el fitxer 'inputs/info_nodes.json' cada 10 segons alternant l'estat de 'vianants' per a un subconjunt de nodes.
    """
    ruta_entrada = Path('inputs/info_nodes.json')
    
    if not ruta_entrada.exists():
        print("L'arxiu info_nodes.json no existeix.")
        return
    
    with open(ruta_entrada, 'r') as f:
        nodes = json.load(f)
    
    if not isinstance(nodes, list):
        print("L'arxiu info_nodes.json no té l'estructura esperada.")
        return
    
    num_nodes_vianants = int(0.1 * len(nodes))
    
    while True:
        nodes_seleccionats = random.sample(nodes, num_nodes_vianants)
        
        for node in nodes_seleccionats:
            node['vianants'] = True
        
        alternar_vianants(nodes_seleccionats)
        
        with open(ruta_entrada, 'w') as f:
            json.dump(nodes, f, indent=2)
        
        print(f'S\'han alternat les banderes de vianants per a {num_nodes_vianants} nodes.')
        time.sleep(5)

if __name__ == '__main__':
    main()
