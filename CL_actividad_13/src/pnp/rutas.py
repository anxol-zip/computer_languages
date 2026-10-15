# Actividad 13 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Endpoints de algoritmos P, NP y con heuristica:
#   - POST /grafos/sintetico  -> sintetico.py   (auxiliar: genera grafos de prueba)
#   - POST /grafos/dijkstra   -> dijkstra.py    (P)
#   - POST /grafos/tsp        -> tsp_exacto.py  (NP-dificil)
#   - POST /grafos/tsp-voraz  -> tsp_voraz.py   (heuristica voraz)
# Los tres algoritmos regresan el mismo esquema (ResultadoGrafo).

import random
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from pnp.dijkstra import dijkstra
from pnp.ejemplos import EJEMPLOS_DIJKSTRA, EJEMPLOS_SINTETICO, EJEMPLOS_TSP
from pnp.esquemas import (
    MAX_NODOS_TSP_EXACTO,
    GrafoSintetico,
    ResultadoGrafo,
    SolicitudDijkstra,
    SolicitudSintetico,
    SolicitudTSP,
)
from pnp.medicion import medir
from pnp.sintetico import generar_grafo
from pnp.tsp_exacto import tsp_exacto
from pnp.tsp_voraz import tsp_voraz

router = APIRouter(prefix="/grafos", tags=["Algoritmos P, NP y heuristica (Actividad 13)"])


def armar_resultado(algoritmo, clase, complejidad, origen, destino, medicion):
    crudo, tiempo_ms, memoria_kb = medicion
    return ResultadoGrafo(
        algoritmo=algoritmo,
        clase=clase,
        complejidad=complejidad,
        origen=origen,
        destino=destino,
        solucion=crudo["solucion"],
        ruta=crudo["ruta"],
        costo=crudo["costo"],
        nodos_recorridos=crudo["nodos_recorridos"],
        tiempo_ms=round(tiempo_ms, 4),
        memoria_kb=round(memoria_kb, 2),
    )


@router.post("/sintetico", response_model=GrafoSintetico, summary="Genera un grafo ponderado aleatorio")
def grafo_sintetico(solicitud: Annotated[SolicitudSintetico, Body(openapi_examples=EJEMPLOS_SINTETICO)]):
    """Grafo no dirigido con pesos enteros al azar. Siempre contiene un ciclo que pasa por
    todos los nodos, asi que el agente viajero siempre tiene solucion. La respuesta
    (campo `grafo`) se puede mandar tal cual a los demas endpoints."""
    semilla = solicitud.semilla if solicitud.semilla is not None else random.randrange(1_000_000)
    grafo, aristas = generar_grafo(solicitud.nodos, solicitud.densidad,
                                   solicitud.peso_min, solicitud.peso_max, semilla)
    return GrafoSintetico(semilla=semilla, nodos=solicitud.nodos, aristas=aristas,
                          densidad=solicitud.densidad, grafo=grafo)


@router.post("/dijkstra", response_model=ResultadoGrafo, summary="Dijkstra: camino mas corto (P)")
def camino_dijkstra(solicitud: Annotated[SolicitudDijkstra, Body(openapi_examples=EJEMPLOS_DIJKSTRA)]):
    """Camino de menor costo entre origen y destino."""
    medicion = medir(dijkstra, solicitud.grafo, solicitud.origen, solicitud.destino)
    return armar_resultado("Dijkstra", "P", "O((V + E) log V)",
                           solicitud.origen, solicitud.destino, medicion)


@router.post("/tsp", response_model=ResultadoGrafo, summary="Agente viajero exacto (NP-dificil)")
def agente_viajero(solicitud: Annotated[SolicitudTSP, Body(openapi_examples=EJEMPLOS_TSP)]):
    """Recorrido de menor costo que visita todos los nodos y regresa al origen. Prueba
    todos los ordenes (con poda), asi que solo acepta grafos de hasta 15 nodos."""
    n = len(solicitud.grafo)
    if n > MAX_NODOS_TSP_EXACTO:
        raise HTTPException(
            status_code=422,
            detail=f"El agente viajero exacto revisa hasta (n - 1)! recorridos: con {n} nodos "
                   f"serian {n - 1}! ordenes. Usa a lo mas {MAX_NODOS_TSP_EXACTO} nodos, o /grafos/tsp-voraz.",
        )
    medicion = medir(tsp_exacto, solicitud.grafo, solicitud.origen)
    return armar_resultado("Agente viajero exacto (backtracking con poda)", "NP-dificil", "O(n!)",
                           solicitud.origen, None, medicion)


@router.post("/tsp-voraz", response_model=ResultadoGrafo, summary="Agente viajero con heuristica voraz")
def agente_viajero_voraz(solicitud: Annotated[SolicitudTSP, Body(openapi_examples=EJEMPLOS_TSP)]):
    """Vecino mas cercano: desde cada nodo va a la arista mas barata hacia un nodo no
    visitado. Rapido, pero no garantiza el optimo y puede quedarse atorado."""
    medicion = medir(tsp_voraz, solicitud.grafo, solicitud.origen)
    return armar_resultado("Agente viajero voraz (vecino mas cercano)", "Heuristica (tiempo polinomico)",
                           "O(V + E)", solicitud.origen, None, medicion)
