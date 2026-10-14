# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Funcion heuristica h(n): estimacion del costo que falta para llegar de n al destino.
# La usan los dos algoritmos (greedy solo con h, A* con g + h).
#
# Hay dos formas de calcularla:
#   1. Con coordenadas (x, y) de cada nodo -> distancia euclidiana al destino,
#      escalada por k para que quede en las mismas unidades que los pesos (o cruda,
#      si se pide escalar_heuristica = false). Las coordenadas de los grafos de la
#      actividad salen de las imagenes con medir_coordenadas.py.
#   2. Sin coordenadas -> h(n) = saltos(n, destino) * peso_minimo
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


def factor_de_escala(grafo, coordenadas):
    """k = min(peso(u, v) / distancia(u, v)) sobre todas las aristas del grafo.

    Las coordenadas estan en pixeles y los pesos en otras unidades: una arista de peso
    12 puede medir cientos de pixeles. k es el mayor factor con el que ninguna arista
    queda "mas corta" que su distancia escalada: k * distancia(u, v) <= peso(u, v).
    """
    k = math.inf
    for nodo, aristas in grafo.items():
        for vecino, peso in aristas:
            distancia = math.dist(coordenadas[nodo], coordenadas[vecino])
            if distancia > 0:           # dos nodos en el mismo punto no limitan a k
                k = min(k, peso / distancia)
    return k if k != math.inf else 0


def heuristica_euclidiana(grafo, coordenadas, destino, escalar=True):
    """h(n) = k * distancia en linea recta de n al destino.  Regresa (h, k).

    Con k = factor_de_escala(...) es consistente: para una arista u -> v, por la
    desigualdad del triangulo y porque k * distancia(u, v) <= c(u, v),
        h(u) <= k * distancia(u, v) + h(v) <= c(u, v) + h(v)
    y por lo tanto tambien admisible: A* regresa la ruta de menor costo.
    Con escalar=False, h(n) es la distancia en pixeles tal cual (k = None): puede
    sobreestimar el costo real y A* deja de garantizar el optimo.
    """
    k = factor_de_escala(grafo, coordenadas) if escalar else None
    destino_xy = coordenadas[destino]
    h = {}
    for nodo in grafo:
        distancia = math.dist(coordenadas[nodo], destino_xy)
        h[nodo] = k * distancia if escalar else distancia
    return h, k


def construir_heuristica(grafo, destino, coordenadas=None, escalar=True):
    """Regresa (h, descripcion, k): la tabla h[nodo], el nombre de la heuristica usada
    y el factor de escala (None si no aplica)."""
    if coordenadas is not None:
        h, k = heuristica_euclidiana(grafo, coordenadas, destino, escalar)
        if escalar:
            return h, f"distancia euclidiana x k (k = {k:.6g})", k
        return h, "distancia euclidiana cruda (pixeles, sin escalar)", None
    return heuristica_por_saltos(grafo, destino), "saltos al destino x peso minimo", None
