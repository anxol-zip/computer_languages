# Actividad 3. Angel Rugerio Jiménez. #201720 31/08/2026

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import itertools  

app = FastAPI()

class Lenguaje(BaseModel):
    L: List[str] = []
    M: List[str] = []
    sigma: List[str] = []
    k: int = 0

# Función: read_root (Raíz)
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Función: reat_item (Leer item)
@app.get("/items/{item_id}")
def reat_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

# Función: concatenar_cadenas
@app.get("/Cadenas/concatenar/{x}/{y}")
def concatenar_cadenas(x: str, y :str):
    return {"resultado": x + y}

# Función: unir_cadenas 
@app.get("/Cadenas/unir/{x}/{y}")
def unir_cadenas(x: str, y: str):
    return {"resultado": [x, y]} # La unión de cadenas genera un conjunto con ambas cadenas

# Función: potencia_cadenas
@app.get("/Cadenas/potencia/{x}/{n}")
def potencia_cadenas(x: str, n: int):
    return {"resultado": x * n} # Repite la cadena 'n' veces

# Función: union_lenguajes
@app.post("/lenguajes/union")
def union_lenguajes(parametro: Lenguaje):
    L = set(parametro.L)
    M = set(parametro.M)
    return {
        "Operacion": "Union de lenguajes",
        "L": L,
        "M": M,
        "resultado": L.union(M)
    }

# Función: interseccion_lenguajes
@app.post("/lenguajes/interseccion")
def interseccion_lenguajes(parametro: Lenguaje):
    L = set(parametro.L)
    M = set(parametro.M)
    return {
        "Operacion": "interseccion de lenguajes",
        "L": L,
        "M": M,
        "resultado": L.intersection(M) 
    }

# Función: diferencia_lenguajes 
@app.post("/lenguajes/diferencia")
def diferencia_lenguajes(parametro: Lenguaje):
    L = set(parametro.L)
    M = set(parametro.M)
    return {
        "Operacion": "Diferencia de lenguajes",
        "L": L,
        "M": M,
        "resultado": L.difference(M) 
    }

# Función: concatenar_lenguajes
@app.post("/lenguajes/concatenar")
def concatenar_lenguajes(parametro: Lenguaje):
    L = set(parametro.L)
    M = set(parametro.M)
    C = {x+y for x in L for y in M}
    return {
        "Operacion": "concatenacion de lenguajes", 
        "L": L,
        "M": M,
        "resultado": C
    }

def generar_universo(sigma: set, k: int) -> set:
    universo = set() 
    for longitud in range(1, k+1):
        for combinacion in itertools.product(sigma, repeat = longitud): 
            universo.add("".join(combinacion))
    return universo

# Función: complemento_lenguajes
@app.post("/lenguajes/complemento")
def complemento_lenguajes(parametro: Lenguaje):
    universo = generar_universo(parametro.sigma, parametro.k)
    return{
        "Operacion": "Complemento de lenguaje",
        "L": parametro.L,
        "sigma": set(parametro.sigma),
        "k": parametro.k,
        "resultado": universo.difference(set(parametro.L))
    }

# Función: kleene_lenguajes (Clausura de Kleene)
@app.post("/lenguajes/kleene")
def kleene_lenguajes(parametro: Lenguaje):
    L = set(parametro.L)
    resultado = {""} # La clausura de Kleene siempre incluye la cadena vacía (lambda/épsilon)
    actual = {""}
    
    # Dado que la clausura es infinita, iteramos hasta la longitud límite 'k' indicada en el parámetro
    for _ in range(parametro.k):
        siguiente = {x + y for x in actual for y in L}
        resultado.update(siguiente)
        actual = siguiente
        
    return {
        "Operacion": "Clausura de Kleene",
        "L": L,
        "k": parametro.k,
        "resultado": resultado
    }