# Actividad 13 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Agente viajero con heuristica voraz: vecino mas cercano.
#
# Criterio de seleccion: desde el nodo actual, ir siempre al vecino no visitado con la
# arista mas barata (empate: orden alfabetico). La eleccion no se reconsidera. Al
# visitar todos los nodos se regresa al origen.
#
# Es rapido, pero no garantiza el optimo, y en un grafo que no es completo se puede
# quedar atorado: un nodo sin vecinos libres, o el ultimo nodo sin arista de regreso.


def tsp_voraz(grafo, origen):
    n = len(grafo)
    pesos = {nodo: dict(aristas) for nodo, aristas in grafo.items()}

    ruta = [origen]
    visitados = {origen}
    costo = 0
    nodo = origen

    while len(ruta) < n:
        candidatos = [(peso, vecino) for vecino, peso in grafo[nodo] if vecino not in visitados]
        if not candidatos:
            break                                       # atorado: no hay a donde seguir
        peso, nodo = min(candidatos)
        ruta.append(nodo)
        visitados.add(nodo)
        costo += peso

    completo = len(ruta) == n and origen in pesos[nodo]
    if completo:
        costo += pesos[nodo][origen]
        ruta.append(origen)

    return {
        "solucion": completo,
        "ruta": ruta,                                   # si no hay solucion, hasta donde llego
        "costo": costo if completo else None,
        "nodos_recorridos": len(visitados),
    }
