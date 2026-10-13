# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Comprobacion de que A* regresa la ruta de menor costo: para cada par (origen, destino)
# de los tres grafos se compara el costo de /search/star contra el de Dijkstra
# (A* con h = 0, que siempre es optimo). Tambien cuenta en cuantos pares greedy se
# queda con una ruta mas cara. Se usa limite_nodos = total de nodos para que el
# limite no corte ninguna busqueda.
#
#     uv run python verificar_optimo.py

import heapq
import json
import math
from pathlib import Path

from fastapi.testclient import TestClient

from main import app

GRAFOS = Path(__file__).parent / "grafos"
cliente = TestClient(app)


def dijkstra(grafo, origen, destino):
    distancia = {origen: 0}
    abierta = [(0, origen)]
    while abierta:
        d, nodo = heapq.heappop(abierta)
        if d > distancia[nodo]:
            continue
        for vecino, peso in grafo[nodo]:
            if d + peso < distancia.get(vecino, math.inf):
                distancia[vecino] = d + peso
                heapq.heappush(abierta, (distancia[vecino], vecino))
    return distancia.get(destino)


for archivo in sorted(GRAFOS.glob("*.json")):
    grafo = json.loads(archivo.read_text(encoding="utf-8"))
    pares = star_ok = greedy_caro = 0
    for origen in grafo:
        for destino in grafo:
            if origen == destino:
                continue
            optimo = dijkstra(grafo, origen, destino)
            if optimo is None:      # sin camino: no hay costo que comparar
                continue
            solicitud = {"grafo": grafo, "origen": origen, "destino": destino, "limite_nodos": len(grafo)}
            star = cliente.post("/search/star", json=solicitud).json()
            greedy = cliente.post("/search/greedy", json=solicitud).json()
            pares += 1
            star_ok += star["costo"] == optimo
            greedy_caro += greedy["costo"] > optimo
    print(f"{archivo.stem}: {pares} pares con camino | A* optimo en {star_ok}/{pares} "
          f"| greedy mas caro que el optimo en {greedy_caro}/{pares}")
