# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Busqueda voraz (Greedy Best-First Search).
#
# Criterio de seleccion: de la lista abierta siempre se saca el nodo con menor h(n),
# es decir, el que "parece" estar mas cerca del destino. g(n) (lo ya recorrido) no se
# toma en cuenta. Empates:
#   1. menor peso de la arista por la que se llego al nodo (valor)
#   2. orden alfabetico del nombre del nodo (orden)
#
# Un nodo se queda con el primer padre que lo descubre: greedy no reconsidera una
# decision ya tomada, aunque despues aparezca un camino mas barato.

import heapq
import time

from busqueda.utilidades import reconstruir_ruta


def greedy_search(grafo, origen, destino, limite_nodos, h):
    inicio = time.perf_counter()

    # lista abierta: (h(n), peso de la arista que lo trajo, nodo)
    abierta = [(h[origen], 0, origen)]
    padre = {origen: None}          # nodos ya descubiertos y quien los descubrio
    cerrados = set()                # nodos ya visitados (expandidos)
    orden_visita = []
    operaciones = 0
    max_memoria = len(abierta)
    encontrado = False

    while abierta and len(orden_visita) < limite_nodos:
        _, _, nodo = heapq.heappop(abierta)
        operaciones += 1
        cerrados.add(nodo)
        orden_visita.append(nodo)

        if nodo == destino:
            encontrado = True
            break

        for vecino, peso in grafo[nodo]:
            operaciones += 1
            if vecino not in padre:         # solo se agrega la primera vez que se descubre
                padre[vecino] = nodo
                heapq.heappush(abierta, (h[vecino], peso, vecino))

        max_memoria = max(max_memoria, len(abierta) + len(cerrados))

    return {
        "solucion": encontrado,
        "ruta": reconstruir_ruta(padre, destino) if encontrado else [],
        "orden_visita": orden_visita,
        "operaciones": operaciones,
        "max_memoria": max_memoria,
        "tiempo_ms": (time.perf_counter() - inicio) * 1000,
    }
