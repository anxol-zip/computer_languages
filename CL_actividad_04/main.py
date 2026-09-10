from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Definicion del objeto que sera leuido como parametro para las funciones de lenguajes

class Lenguaje(BaseModel):
    L: List[str]
    M: List[str]

# 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/cadenas/concatenar/{x}/{y}")
def concatenar_cadenas(x: str, y: str):
    return {"resultado": x + y}


@app.get("/cadenas/invertir/{x}")
def invertir_cadena(x: str):
    return {"resultado": x[::-1]}


@app.get("/cadenas/potencia/{x}")
def potencia_cadena(x: str, k: int):
    if k <= 0:
        return {"respuesta": ""}  # Si la potencia es cero o negativa
    return {"respuesta": x * k}

@app.post("/lenguajes/union")
def union_lenguajes(parametro: Lenguaje):
    #Convirtiendo L y M a conjuntos para realizar la union
    L= set(parametro.L)
    M= set(parametro.M)
    return {
        "Operacion": "Union de lenguajes",
        "L": L,
        "M": M,
        "resultado": list(L.union(M))
        }

@app.post("/lenguajes/interseccion")
def interseccion_lenguajes(parametro: Lenguaje):
    #Convirtiendo L y M a conjuntos para realizar la interseccion
    L= set(parametro.L)
    M= set(parametro.M)
    return {
        "Operacion": "Interseccion de lenguajes",
        "L": L,
        "M": M,
        "resultado": list(L.intersection(M))
        }

@app.post("/lenguajes/diferencia")
def diferencia_lenguajes(parametro: Lenguaje):
    #Convirtiendo L y M a conjuntos para realizar la diferencia
    L= set(parametro.L)
    M= set(parametro.M)
    return {
        "Operacion": "Diferencia de lenguajes",
        "L": L,
        "M": M,
        "resultado": list(L.difference(M))
        }


@app.post("/lenguajes/concatenacion")
def concatenacion_lenguajes(parametro: Lenguaje):
    #Convirtiendo L y M a conjuntos para realizar la concatenacion
    L = set(parametro.L)
    M = set(parametro.M)
    C = {x + y for x in L for y in M}
    return {
        "Operacion": "Concatenacion de lenguajes",
        "L": L,
        "M": M,
        "resultado": C
        }