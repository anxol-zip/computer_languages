# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Endpoints de busqueda informada:
#   - POST /search/greedy  -> greedy_search.py
#   - POST /search/star    -> star_search.py
# Los dos reciben el mismo esquema (SolicitudBusqueda) y regresan el mismo (ResultadoBusqueda).

from typing import Annotated

from fastapi import APIRouter, Body

from busqueda.ejemplos import EJEMPLOS
from busqueda.esquemas import (
    ComplejidadEspacio,
    ComplejidadTiempo,
    ResultadoBusqueda,
    SolicitudBusqueda,
)
from busqueda.greedy_search import greedy_search
from busqueda.heuristica import construir_heuristica
from busqueda.star_search import star_search
from busqueda.utilidades import costo_de_ruta

router = APIRouter(prefix="/search", tags=["Busqueda informada (Actividad 12)"])

# cuerpo de la solicitud, con las 27 pruebas de la actividad como ejemplos en /docs
Solicitud = Annotated[SolicitudBusqueda, Body(openapi_examples=EJEMPLOS)]


def armar_resultado(solicitud, algoritmo, nombre_heuristica, k, crudo, cota_t, cota_s):
    """Convierte lo que regresa el algoritmo al esquema de salida."""
    grafo = solicitud.grafo
    return ResultadoBusqueda(
        algoritmo=algoritmo,
        origen=solicitud.origen,
        destino=solicitud.destino,
        heuristica=nombre_heuristica,
        factor_escala=k,
        limite_nodos=solicitud.limite_nodos,
        nodos_visitados=len(crudo["orden_visita"]),
        solucion=crudo["solucion"],
        ruta=crudo["ruta"],
        costo=costo_de_ruta(grafo, crudo["ruta"]) if crudo["solucion"] else None,
        orden_visita=crudo["orden_visita"],
        T_n=ComplejidadTiempo(
            cota=cota_t,
            V=len(grafo),
            E=sum(len(aristas) for aristas in grafo.values()),
            operaciones=crudo["operaciones"],
            tiempo_ms=round(crudo["tiempo_ms"], 4),
        ),
        S_n=ComplejidadEspacio(cota=cota_s, max_nodos_en_memoria=crudo["max_memoria"]),
    )


@router.post("/greedy", response_model=ResultadoBusqueda, summary="Busqueda voraz (Greedy Best-First)")
def busqueda_greedy(solicitud: Solicitud):
    """Expande siempre el nodo con menor h(n). Rapida, pero no garantiza la ruta de menor costo."""
    h, nombre_heuristica, k = construir_heuristica(solicitud.grafo, solicitud.destino,
                                                   solicitud.coordenadas, solicitud.escalar_heuristica)
    crudo = greedy_search(solicitud.grafo, solicitud.origen, solicitud.destino, solicitud.limite_nodos, h)
    # cada nodo entra una sola vez al heap
    return armar_resultado(solicitud, "Greedy Best-First Search", nombre_heuristica, k, crudo,
                           cota_t="O((V + E) log V)", cota_s="O(V)")


@router.post("/star", response_model=ResultadoBusqueda, summary="Busqueda A* (f = g + h)")
def busqueda_star(solicitud: Solicitud):
    """Expande siempre el nodo con menor f(n) = g(n) + h(n). Con h admisible y consistente,
    la ruta que regresa es la de menor costo."""
    h, nombre_heuristica, k = construir_heuristica(solicitud.grafo, solicitud.destino,
                                                   solicitud.coordenadas, solicitud.escalar_heuristica)
    crudo = star_search(solicitud.grafo, solicitud.origen, solicitud.destino, solicitud.limite_nodos, h)
    # un nodo puede volver a entrar al heap cada vez que mejora su g (una vez por arista entrante)
    return armar_resultado(solicitud, "A*", nombre_heuristica, k, crudo,
                           cota_t="O((V + E) log V)", cota_s="O(V + E)")
