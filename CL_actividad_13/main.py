# Actividad 13 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Punto de entrada del servicio. Aqui no hay logica: solo se crea la app de FastAPI
# y se le conectan los endpoints de cada modulo de src/:
#   - automatas    (Actividad 6):  POST /afd/evaluar, POST /afn/evaluar
#   - complejidad  (Actividad 11): POST /complejidad/peor-caso, POST /complejidad/mejor-caso
#   - busqueda     (Actividad 12): POST /search/greedy, POST /search/star
#   - pnp          (Actividad 13): POST /grafos/sintetico, /grafos/dijkstra, /grafos/tsp, /grafos/tsp-voraz
#
# Se levanta con  uv run fastapi dev  o con  uv run main.py

from fastapi import FastAPI

import automatas
from busqueda.rutas import router as rutas_busqueda
from complejidad.rutas import router as rutas_complejidad
from pnp.rutas import router as rutas_pnp

app = FastAPI(
    title="Actividad 13 - Algoritmos P, NP y con heuristica",
    description="Servicio web que evalua cadenas sobre automatas finitos (AFD y AFN), analiza "
                "la complejidad de un programa en Python (Big-O y Big-Omega), busca rutas con "
                "Greedy y A*, y resuelve Dijkstra y el agente viajero (exacto y voraz) sobre "
                "grafos ponderados.",
    version="4.0.0",
)

app.include_router(automatas.router)
app.include_router(rutas_complejidad)
app.include_router(rutas_busqueda)
app.include_router(rutas_pnp)


@app.get("/", summary="Informacion del servicio")
def read_root():
    return {
        "actividad": "Actividad 13 - Algoritmos P, NP y con heuristica",
        "autor": "Angel Rugerio Jimenez - 201720",
        "endpoints": {
            "POST /afd/evaluar": "Evalua cadenas sobre un AFD (Actividad 6)",
            "POST /afn/evaluar": "Evalua cadenas sobre un AFN, con o sin transiciones ε (Actividad 6)",
            "POST /complejidad/peor-caso": "Anota un programa .py con su complejidad Big-O (Actividad 11)",
            "POST /complejidad/mejor-caso": "Anota un programa .py con su complejidad Big-Omega (Actividad 11)",
            "POST /search/greedy": "Busqueda voraz: expande el nodo con menor h(n) (Actividad 12)",
            "POST /search/star": "Busqueda A*: expande el nodo con menor f(n) = g(n) + h(n) (Actividad 12)",
            "POST /grafos/sintetico": "Genera un grafo ponderado aleatorio (Actividad 13)",
            "POST /grafos/dijkstra": "Camino mas corto entre dos nodos, clase P (Actividad 13)",
            "POST /grafos/tsp": "Agente viajero exacto, NP-dificil (Actividad 13)",
            "POST /grafos/tsp-voraz": "Agente viajero con heuristica voraz (Actividad 13)",
        },
        "documentacion_interactiva": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000)
