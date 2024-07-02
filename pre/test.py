import json

# Ruta del archivo de entrada y de salida
input_file = 'info_nodos.txt'
output_file = 'info_nodos.json'

# Leer el archivo de entrada
with open(input_file, 'r') as file:
    lines = file.readlines()

# Procesar las líneas y convertirlas a una estructura de datos
nodes = []
for line in lines:
    parts = line.strip().split('], [')
    node_id = parts[0].strip('[')
    coordinates = parts[1].strip('[]').split(',')
    address = parts[2].strip('[]')
    status = parts[3].strip('[]')
    
    node = {
        "node_id": int(node_id),
        "coordinates": {
            "longitude": float(coordinates[0]),
            "latitude": float(coordinates[1])
        },
        "address": address,
        "status": status
    }
    nodes.append(node)

# Escribir la estructura de datos en un archivo JSON
with open(output_file, 'w') as file:
    json.dump(nodes, file, indent=4)

print(f"Datos guardados en {output_file}")
