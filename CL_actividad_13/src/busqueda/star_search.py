# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Busqueda A* (A estrella).
#
# Funcion de valor: f(n) = g(n) + h(n)
#   g(n): costo real acumulado desde el origen (suma de pesos conocidos)
#   h(n): estimacion del costo que falta hasta el destino (heuristica.py)
# Siempre se expande el nodo con menor f(n); en empate, el de menor h(n) (el que
# parece estar mas cerca), y despues el orden alfabetico.
#
# A diferencia de greedy, si se encuentra un camino mas barato a un nodo que sigue en
# la lista abierta, se actualizan su g y su padre. La entrada vieja se queda en el
# heap y se ignora cuando sale (ya esta en cerrados).

import heapq
import math
import time

from busqueda.utilidades import reconstruir_ruta


def star_search(grafo, origen, destino, limite_nodos, h):
    inicio = time.perf_counter()

    g = {origen: 0}
    padre = {origen: None}
    # lista abierta: (f(n), h(n), nodo)
    abierta = [(g[origen] + h[origen], h[origen], origen)]
    cerrados = set()
    orden_visita = []
    operaciones = 0
    max_memoria = len(abierta)
    encontrado = False

    while abierta and len(orden_visita) < limite_nodos:
        _, _, nodo = heapq.heappop(abierta)
        operaciones += 1
        if nodo in cerrados:            # entrada vieja: ya se visito con un g menor
            continue
        cerrados.add(nodo)
        orden_visita.append(nodo)

        if nodo == destino:
            encontrado = True
            break

        for vecino, peso in grafo[nodo]:
            operaciones += 1
            # con h consistente, un nodo cerrado ya tiene su g minimo
            if vecino in cerrados:
                continue
            nuevo_g = g[nodo] + peso
            if nuevo_g < g.get(vecino, math.inf):
                g[vecino] = nuevo_g
                padre[vecino] = nodo
                heapq.heappush(abierta, (nuevo_g + h[vecino], h[vecino], vecino))

        max_memoria = max(max_memoria, len(abierta) + len(cerrados))

    return {
        "solucion": encontrado,
        "ruta": reconstruir_ruta(padre, destino) if encontrado else [],
        "orden_visita": orden_visita,
        "operaciones": operaciones,
        "max_memoria": max_memoria,
        "tiempo_ms": (time.perf_counter() - inicio) * 1000,
    }
