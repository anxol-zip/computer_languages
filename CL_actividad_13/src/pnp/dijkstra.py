# Actividad 13 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Algoritmo de Dijkstra: camino de menor costo entre dos nodos (clase P).
#
# Siempre se expande el nodo con menor distancia acumulada desde el origen. Con pesos
# no negativos, cuando un nodo sale de la lista abierta su distancia ya es la minima,
# asi que en cuanto sale el destino se puede parar. Es A* con h(n) = 0.

import heapq
import math

from busqueda.utilidades import reconstruir_ruta


def dijkstra(grafo, origen, destino):
    distancia = {origen: 0}
    padre = {origen: None}
    visitados = set()
    abierta = [(0, origen)]          # (distancia acumulada, nodo)

    while abierta:
        actual, nodo = heapq.heappop(abierta)
        if nodo in visitados:        # entrada vieja: ya salio con una distancia menor
            continue
        visitados.add(nodo)

        if nodo == destino:
            break

        for vecino, peso in grafo[nodo]:
            nueva = actual + peso
            if nueva < distancia.get(vecino, math.inf):
                distancia[vecino] = nueva
                padre[vecino] = nodo
                heapq.heappush(abierta, (nueva, vecino))

    encontrado = destino in visitados
    return {
        "solucion": encontrado,
        "ruta": reconstruir_ruta(padre, destino) if encontrado else [],
        "costo": distancia[destino] if encontrado else None,
        "nodos_recorridos": len(visitados),
    }
