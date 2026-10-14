# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Ejemplos precargados para la documentacion interactiva (/docs): las 9 pruebas de la
# actividad (3 por grafo), cada una con las 3 heuristicas. En Swagger aparecen en el
# menu "Examples" de cada endpoint y se ejecutan con "Try it out" -> "Execute".
#
# Los grafos y las coordenadas se leen de grafos/ en la raiz del proyecto (con uv sync
# el proyecto queda instalado en modo editable, asi que esa ruta existe).

import json
from pathlib import Path

GRAFOS = Path(__file__).resolve().parents[2] / "grafos"

# (nodos del grafo, origen, destino) -- distintos origenes y destinos en cada grafo
CASOS = [
    (10, "A", "J"), (10, "B", "H"), (10, "D", "I"),
    (25, "A", "Y"), (25, "D", "W"), (25, "B", "V"),
    (50, "A", "AA"), (50, "E", "AX"), (50, "D", "AM"),
]


def cargar(nombre):
    return json.loads((GRAFOS / nombre).read_text(encoding="utf-8"))


def construir_ejemplos():
    ejemplos = {}
    for n, origen, destino in CASOS:
        grafo = cargar(f"grafo_{n}.json")
        coordenadas = cargar(f"coordenadas_{n}.json")
        base = {"grafo": grafo, "origen": origen, "destino": destino}
        heuristicas = {
            "saltos": base,
            "euclidiana": {**base, "coordenadas": coordenadas},
            "euclidiana cruda": {**base, "coordenadas": coordenadas, "escalar_heuristica": False},
        }
        for heuristica, valor in heuristicas.items():
            ejemplos[f"grafo_{n} {origen}-{destino} {heuristica}"] = {
                "summary": f"Grafo de {n} nodos: {origen} -> {destino} (heuristica: {heuristica})",
                "value": valor,
            }
    return ejemplos


EJEMPLOS = construir_ejemplos()
