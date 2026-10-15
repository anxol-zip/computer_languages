# Actividad 13 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Generador de grafos sinteticos: no dirigidos, ponderados y con pesos enteros al azar.
#
#   1. Se acomodan los nodos en un orden aleatorio y se unen en un ciclo
#      (A -> ... -> A). Asi el grafo siempre es conexo y el agente viajero siempre
#      tiene al menos un recorrido valido.
#   2. Cada par de nodos que todavia no esta unido recibe una arista con
#      probabilidad = densidad. Con densidad 1 el grafo es completo.
#
# La misma semilla da siempre el mismo grafo, para poder repetir las pruebas.

import random
import string


def nombres_de_nodos(n):
    """A, B, C, ... (hasta 26 nodos)."""
    return list(string.ascii_uppercase[:n])


def generar_grafo(nodos, densidad, peso_min, peso_max, semilla):
    azar = random.Random(semilla)
    nombres = nombres_de_nodos(nodos)
    pesos = {nodo: {} for nodo in nombres}

    def unir(u, v):
        peso = azar.randint(peso_min, peso_max)
        pesos[u][v] = peso          # no dirigido: la arista vale en los dos sentidos
        pesos[v][u] = peso

    # 1. ciclo que pasa por todos los nodos
    orden = nombres[:]
    azar.shuffle(orden)
    for i in range(nodos):
        unir(orden[i], orden[(i + 1) % nodos])

    # 2. aristas extra segun la densidad
    for i, u in enumerate(nombres):
        for v in nombres[i + 1:]:
            if v not in pesos[u] and azar.random() < densidad:
                unir(u, v)

    # mismo formato de lista de adyacencia que la Actividad 12: {"A": [["B", 15], ...]}
    grafo = {nodo: [[vecino, pesos[nodo][vecino]] for vecino in sorted(pesos[nodo])] for nodo in nombres}
    aristas = sum(len(vecinos) for vecinos in pesos.values()) // 2
    return grafo, aristas
