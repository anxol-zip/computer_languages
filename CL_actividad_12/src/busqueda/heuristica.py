# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Funcion heuristica h(n): estimacion del costo que falta para llegar de n al destino.
# La usan los dos algoritmos (greedy solo con h, A* con g + h).
#
# Hay dos formas de calcularla:
#   1. Con coordenadas (x, y) de cada nodo -> distancia euclidiana al destino.
#   2. Sin coordenadas (el caso de los grafos de la actividad, que solo traen pesos)
#      -> h(n) = saltos(n, destino) * peso_minimo
#      donde saltos(n, destino) es el menor numero de aristas entre n y el destino,
#      calculado con una BFS hacia atras desde el destino.

import math
from collections import deque

INFINITO = math.inf


def distancia_en_saltos(grafo, destino):
    """BFS sobre las aristas invertidas, empezando en el destino.

    Regresa {nodo: numero minimo de aristas de nodo al destino}. Un nodo que no tiene
    ningun camino al destino no aparece en el diccionario.
    """
    # grafo invertido: para cada nodo, quienes llegan a el
    entrantes = {nodo: [] for nodo in grafo}
    for nodo, aristas in grafo.items():
        for vecino, _ in aristas:
            entrantes[vecino].append(nodo)

    saltos = {destino: 0}
    cola = deque([destino])
    while cola:
        actual = cola.popleft()
        for anterior in entrantes[actual]:
            if anterior not in saltos:      # se marca al encolar: nunca entra dos veces
                saltos[anterior] = saltos[actual] + 1
                cola.append(anterior)
    return saltos


def heuristica_por_saltos(grafo, destino):
    """h(n) = saltos(n, destino) * peso minimo de todo el grafo.

    Es admisible: un camino de k aristas cuesta al menos k * peso_minimo, asi que h
    nunca sobreestima. Tambien es consistente: en una arista n -> m, saltos(n) <= saltos(m) + 1,
    entonces h(n) <= h(m) + peso_minimo <= h(m) + c(n, m).
    """
    pesos = [peso for aristas in grafo.values() for _, peso in aristas]
    peso_minimo = min(pesos) if pesos else 0
    saltos = distancia_en_saltos(grafo, destino)
    # sin camino al destino -> h = infinito (se explora al final, si es que se explora)
    return {nodo: saltos[nodo] * peso_minimo if nodo in saltos else INFINITO for nodo in grafo}


def heuristica_euclidiana(coordenadas, destino):
    """h(n) = distancia en linea recta de n al destino."""
    xd, yd = coordenadas[destino]
    return {nodo: math.sqrt((x - xd) ** 2 + (y - yd) ** 2) for nodo, (x, y) in coordenadas.items()}


def construir_heuristica(grafo, destino, coordenadas=None):
    """Regresa (h, descripcion): la tabla h[nodo] y el nombre de la heuristica usada."""
    if coordenadas is not None:
        return heuristica_euclidiana(coordenadas, destino), "distancia euclidiana"
    return heuristica_por_saltos(grafo, destino), "saltos al destino x peso minimo"
