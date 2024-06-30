from ..config.db import conn

def trobar_seguent_node(ruta, posicio_actual):
    """
    Troba el següent node en la ruta donada la posició actual.
    
    PRE: ruta és una llista de nodes que formen el camí.
         posicio_actual és el node actual en la ruta.
    POST: retorna el següent node en la ruta si existeix, en cas contrari retorna None.
    """
    try:
        index_actual = ruta.index(posicio_actual)
        return ruta[index_actual + 1] if index_actual + 1 < len(ruta) else None
    except ValueError:
        raise ValueError("La posició actual no es troba a la ruta.")

def main(ruta, posicio_actual):
    """
    Funció main que comprova si el següent node en la ruta té presència de vianants.
    
    PRE: ruta és una llista de nodes que formen el camí.
         posicio_actual és el node actual en la ruta.
    POST: retorna l'atribut vianants del següent node en la ruta, en cas contrari retorna False.
    """
    nodes_vianants_dict = { (node["coordenades"]["longitud"], node["coordenades"]["latitud"]): node['vianants'] for node in conn['cloud']['carrer'].find({"vianants": True}) }
    
    seguent_node = trobar_seguent_node(ruta, posicio_actual)
    if seguent_node is None:
        return False
    
    seguent_node_coords = (seguent_node['longitud'], seguent_node['latitud'])
    
    return nodes_vianants_dict.get(seguent_node_coords, False)

if __name__ == '__main__':
    main()
