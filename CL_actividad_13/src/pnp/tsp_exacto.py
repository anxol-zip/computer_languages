# Actividad 13 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Agente viajero exacto (NP-dificil).
#
# Busca el recorrido mas barato que sale del origen, pasa UNA vez por cada nodo y
# regresa al origen. Prueba todos los ordenes posibles con backtracking (busqueda en
# profundidad): cada llamada a explorar() es un nodo del arbol de busqueda.
#
# Poda: si el costo de un recorrido a medias ya iguala o supera al mejor recorrido
# completo encontrado, esa rama se abandona. No cambia la respuesta (sigue siendo la
# optima), solo evita terminar recorridos que ya no pueden ganar. En el peor caso se
# siguen revisando (n - 1)! ordenes.


def tsp_exacto(grafo, origen):
    n = len(grafo)
    pesos = {nodo: dict(aristas) for nodo, aristas in grafo.items()}

    mejor_costo = None
    mejor_ruta = []
    nodos_recorridos = 0
    ruta = [origen]
    en_ruta = {origen}

    def explorar(nodo, costo):
        nonlocal mejor_costo, mejor_ruta, nodos_recorridos
        nodos_recorridos += 1

        if mejor_costo is not None and costo >= mejor_costo:
            return                                      # poda

        if len(ruta) == n:                              # ya se visitaron todos: volver al origen
            if origen in pesos[nodo]:
                total = costo + pesos[nodo][origen]
                if mejor_costo is None or total < mejor_costo:
                    mejor_costo = total
                    mejor_ruta = ruta + [origen]
            return

        for vecino, peso in grafo[nodo]:
            if vecino not in en_ruta:
                ruta.append(vecino)
                en_ruta.add(vecino)
                explorar(vecino, costo + peso)
                ruta.pop()                              # backtracking: deshacer la eleccion
                en_ruta.remove(vecino)

    explorar(origen, 0)
    return {
        "solucion": mejor_costo is not None,
        "ruta": mejor_ruta,
        "costo": mejor_costo,
        "nodos_recorridos": nodos_recorridos,
    }
