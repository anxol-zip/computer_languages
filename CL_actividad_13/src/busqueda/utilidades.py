# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Funciones que comparten greedy_search.py y star_search.py.


def reconstruir_ruta(padre, destino):
    """Sigue los padres desde el destino hasta el origen (padre None) y la voltea."""
    ruta = []
    nodo = destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = padre[nodo]
    ruta.reverse()
    return ruta


def costo_de_ruta(grafo, ruta):
    """Suma de los pesos de las aristas de la ruta."""
    costo = 0
    for actual, siguiente in zip(ruta, ruta[1:]):
        costo += dict(grafo[actual])[siguiente]
    return costo
