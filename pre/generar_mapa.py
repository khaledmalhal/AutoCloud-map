import json

def cargar_coordenadas(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print("Datos cargados del archivo:", data)
            return data['coordenadas']
    except FileNotFoundError:
        print("El archivo no se encontró.")
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON.")
    return []

def generar_html(coordenadas, archivo_salida):
    if not coordenadas:
        print("La lista de coordenadas está vacía.")
        return
    
    inicio = coordenadas[0]
    fin = coordenadas[-1]
    print(f"Inicio: {inicio}, Fin: {fin}")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mapa con Ruta y Instrucciones</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://api.mapbox.com/mapbox-gl-js/v2.6.1/mapbox-gl.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v2.6.1/mapbox-gl.css" rel="stylesheet">
    <style>
        body {{ margin: 0; padding: 0; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
        #instructions {{ position: absolute; top: 10px; right: 10px; background: white; padding: 10px; z-index: 100; }}
    </style>
</head>
<body>
<div id="map"></div>
<script>
    mapboxgl.accessToken = 'pk.eyJ1IjoiYWpidiIsImEiOiJjbHdmNTRscnoxbGgxMmlwYThqZDJmNmo2In0.Fxyr0FGk196DaN6v7Z71Zg';
    const map = new mapboxgl.Map({{
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [{inicio[0]}, {inicio[1]}], // Coordenadas del centro del mapa
        zoom: 12 // Nivel de zoom inicial
    }});

    // Añadir una capa de ruta a partir de la geometría de la ruta
    const rutaGeoJSON = {{
        "type": "Feature",
        "properties": {{}},
        "geometry": {{
            "type": "LineString",
            "coordinates": {json.dumps(coordenadas)}
        }}
    }};

    map.on('load', function () {{
        // Añadir la ruta
        map.addLayer({{
            "id": "ruta",
            "type": "line",
            "source": {{
                "type": "geojson",
                "data": rutaGeoJSON
            }},
            "layout": {{
                "line-join": "round",
                "line-cap": "round"
            }},
            "paint": {{
                "line-color": "#888",
                "line-width": 6
            }}
        }});
    }});
</script>
</body>
</html>"""

    with open(archivo_salida, 'w', encoding='utf-8') as file:
        file.write(html_content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python generar_mapa.py <archivo_coordenadas> <archivo_salida>")
    else:
        archivo_coordenadas = sys.argv[1]
        archivo_salida = sys.argv[2]
        coordenadas = cargar_coordenadas(archivo_coordenadas)
        print("Coordenadas cargadas:", coordenadas)
        generar_html(coordenadas, archivo_salida)
