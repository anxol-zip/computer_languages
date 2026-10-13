# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Punto de entrada del servicio. Aqui no hay logica: solo se crea la app de FastAPI
# y se le conectan los endpoints de src/busqueda/:
#   POST /search/greedy, POST /search/star
#
# Se levanta con  uv run fastapi dev  o con  uv run main.py

from fastapi import FastAPI

from busqueda.rutas import router as rutas_busqueda

app = FastAPI(
    title="Actividad 12 - Busqueda informada en grafos",
    description="Servicio web que busca una ruta entre dos nodos de un grafo dirigido y "
                "ponderado con busqueda voraz (Greedy Best-First Search) y con A*, y reporta "
                "nodos visitados, ruta, T(n) y S(n) de cada busqueda.",
    version="1.0.0",
)

app.include_router(rutas_busqueda)


@app.get("/", summary="Informacion del servicio")
def read_root():
    return {
        "actividad": "Actividad 12 - Busqueda informada en grafos",
        "autor": "Angel Rugerio Jimenez - 201720",
        "endpoints": {
            "POST /search/greedy": "Busqueda voraz: expande el nodo con menor h(n)",
            "POST /search/star": "Busqueda A*: expande el nodo con menor f(n) = g(n) + h(n)",
        },
        "documentacion_interactiva": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000)
