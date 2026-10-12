# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Punto de entrada del servicio. Aqui no hay logica: solo se crea la app de FastAPI
# y se le conectan los endpoints de cada modulo de src/:
#   - automatas    (Actividad 6):  POST /afd/evaluar, POST /afn/evaluar
#   - complejidad  (Actividad 11): POST /complejidad/peor-caso, POST /complejidad/mejor-caso
#
# Se levanta con  uv run fastapi dev  o con  uv run main.py

from fastapi import FastAPI

import automatas
from complejidad.rutas import router as rutas_complejidad

app = FastAPI(
    title="Actividad 11 - Analizador de Complejidad",
    description="Servicio web que evalua cadenas sobre automatas finitos deterministas (AFD) "
                "y no deterministas (AFN, con transiciones vacias), y que analiza la "
                "complejidad de un programa en Python en el peor caso (Big-O) y en el "
                "mejor caso (Big-Omega).",
    version="2.0.0",
)

app.include_router(automatas.router)
app.include_router(rutas_complejidad)


@app.get("/", summary="Informacion del servicio")
def read_root():
    return {
        "actividad": "Actividad 11 - Analizador de Complejidad",
        "autor": "Angel Rugerio Jimenez - 201720",
        "endpoints": {
            "POST /afd/evaluar": "Evalua cadenas sobre un AFD",
            "POST /afn/evaluar": "Evalua cadenas sobre un AFN (con o sin transiciones ε)",
            "POST /complejidad/peor-caso": "Anota un programa .py con su complejidad Big-O",
            "POST /complejidad/mejor-caso": "Anota un programa .py con su complejidad Big-Omega",
        },
        "documentacion_interactiva": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000)
