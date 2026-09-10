# Actividad 6. Angel Rugerio Jimenez. #201720
# Evaluador de cadenas para AFD y AFN expuesto como servicio web con FastAPI.

from collections import deque
from typing import Dict, List, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Actividad 6 - Evaluador de AFD y AFN",
    description="Servicio web que evalua cadenas sobre automatas finitos "
                "deterministas (AFD) y no deterministas (AFN, con transiciones lambda).",
    version="1.0.0",
)

# Llaves que se aceptan como la transicion vacia (lambda / epsilon) en un AFN.
# Se dejan fuera abreviaturas de una letra como "l" o "e" porque esas letras si
# pueden ser simbolos reales del alfabeto (el AFD del ejercicio 1 usa 'e').
SIMBOLOS_LAMBDA = {"", "lambda", "λ", "epsilon", "ε"}

LAMBDA = "λ"


# ---------------------------------------------------------------------------
# Modelos de entrada
# ---------------------------------------------------------------------------

class AFD(BaseModel):
    """AFD: cada celda de la tabla de transicion apunta a UN solo estado."""
    estado_inicial: str = Field(..., examples=["q0"])
    estados_finales: List[str] = Field(..., examples=[["q2"]])
    # tabla_transicion[estado][simbolo] = estado_destino
    tabla_transicion: Dict[str, Dict[str, str]] = Field(
        ..., examples=[{"q0": {"a": "q1", "b": "q0"},
                        "q1": {"a": "q1", "b": "q2"},
                        "q2": {"a": "q2", "b": "q2"}}]
    )
    cadenas: List[str] = Field(default_factory=list, examples=[["ab", "ba", ""]])


class AFN(BaseModel):
    """AFN: cada celda de la tabla apunta a un CONJUNTO de estados.

    Se acepta tanto una lista (["q1", "q2"]) como un solo estado ("q1").
    La columna de transiciones lambda se escribe con la llave "" o "λ".
    """
    estado_inicial: str = Field(..., examples=["q0"])
    estados_finales: List[str] = Field(..., examples=[["q2"]])
    # tabla_transicion[estado][simbolo] = [estados_destino]
    tabla_transicion: Dict[str, Dict[str, Union[str, List[str]]]] = Field(
        ..., examples=[{"q0": {"a": ["q0", "q1"], "b": ["q0"]},
                        "q1": {"b": ["q2"]},
                        "q2": {}}]
    )
    cadenas: List[str] = Field(default_factory=list, examples=[["aab", "ba", ""]])


# ---------------------------------------------------------------------------
# Utilidades comunes
# ---------------------------------------------------------------------------

def es_lambda(simbolo: str) -> bool:
    """Indica si la llave de la tabla representa la transicion vacia."""
    return simbolo in SIMBOLOS_LAMBDA


def mostrar(cadena: str) -> str:
    """La cadena vacia se muestra como lambda para que la notacion se lea bien."""
    return cadena if cadena != "" else LAMBDA


def conjunto(estados) -> str:
    """Formatea un conjunto de estados como {q0, q1}."""
    return "{" + ", ".join(sorted(estados)) + "}" if estados else "{}"


def normalizar_destinos(destino: Union[str, List[str]]) -> List[str]:
    """Un destino puede venir como cadena o como lista; siempre se regresa lista."""
    if isinstance(destino, str):
        return [destino] if destino else []
    return list(destino)


def describir(tabla: Dict[str, Dict[str, Union[str, List[str]]]]):
    """Obtiene estados totales y alfabeto a partir de la tabla de transicion.

    Los estados salen unicamente de la tabla (renglones y destinos), nunca del
    estado inicial ni de los finales: asi validar() puede detectar un estado mal
    escrito en lugar de agregarlo silenciosamente al automata.
    """
    estados = set(tabla.keys())
    alfabeto = set()

    for fila in tabla.values():
        for simbolo, destino in fila.items():
            estados.update(normalizar_destinos(destino))
            if not es_lambda(simbolo):
                alfabeto.add(simbolo)  # lambda no forma parte del alfabeto

    return sorted(estados), sorted(alfabeto)


def validar(estados: List[str], estado_inicial: str, estados_finales: List[str]) -> None:
    """Comprueba que el estado inicial y los finales existan en el automata."""
    if estado_inicial not in estados:
        raise HTTPException(
            status_code=400,
            detail=f"El estado inicial '{estado_inicial}' no aparece en el automata.",
        )
    faltantes = [q for q in estados_finales if q not in estados]
    if faltantes:
        raise HTTPException(
            status_code=400,
            detail=f"Estados finales que no aparecen en el automata: {faltantes}",
        )


# ---------------------------------------------------------------------------
# Evaluacion de un AFD
# ---------------------------------------------------------------------------

def evaluar_cadena_afd(automata: AFD, cadena: str) -> dict:
    """Recorre la cadena simbolo por simbolo: delta(q, a) siempre da un estado."""
    tabla = automata.tabla_transicion
    actual = automata.estado_inicial

    pasos: List[dict] = []
    # notacion de configuraciones (q, cadena_restante) unidas con el simbolo |-
    configuraciones = [f"({actual}, {mostrar(cadena)})"]
    motivo = None

    for i, simbolo in enumerate(cadena):
        destino = tabla.get(actual, {}).get(simbolo)

        if destino is None:
            motivo = (f"No existe la transicion delta({actual}, {simbolo}); "
                      f"el AFD se detiene en el simbolo {i + 1} de la cadena "
                      f"(la cadena cae en el estado trampa implicito).")
            break

        pasos.append({
            "paso": i + 1,
            "estado_origen": actual,
            "simbolo": simbolo,
            "estado_destino": destino,
            "notacion": f"δ({actual}, {simbolo}) = {destino}",
        })
        actual = destino
        configuraciones.append(f"({actual}, {mostrar(cadena[i + 1:])})")

    consumio_todo = motivo is None
    aceptada = consumio_todo and actual in automata.estados_finales

    if motivo is None:
        motivo = (f"La cadena se consumio por completo y termino en '{actual}', "
                  f"que {'SI' if aceptada else 'NO'} es un estado final.")

    return {
        "cadena": mostrar(cadena),
        "aceptada": aceptada,
        "estado_final_alcanzado": actual if consumio_todo else None,
        "notacion_transicion": {
            "pasos": [p["notacion"] for p in pasos],
            "configuraciones": " ⊢ ".join(configuraciones),
            "funcion_extendida": (f"δ*({automata.estado_inicial}, {mostrar(cadena)}) = {actual}"
                                  if consumio_todo else
                                  f"δ*({automata.estado_inicial}, {mostrar(cadena)}) = indefinida"),
            "recorrido": automata.estado_inicial + "".join(
                f" --{p['simbolo']}--> {p['estado_destino']}" for p in pasos
            ),
        },
        "detalle_pasos": pasos,
        "motivo": motivo,
    }


@app.post("/afd/evaluar", summary="Evalua cadenas sobre un AFD")
def evaluar_afd(automata: AFD):
    estados, alfabeto = describir(automata.tabla_transicion)
    validar(estados, automata.estado_inicial, automata.estados_finales)

    resultados = [evaluar_cadena_afd(automata, c) for c in automata.cadenas]

    return {
        "tipo": "AFD",
        "definicion_formal": "M = (Q, Σ, δ, q0, F)",
        "estados_totales": estados,
        "numero_de_estados": len(estados),
        "alfabeto": alfabeto,
        "estado_inicial": automata.estado_inicial,
        "estados_finales": sorted(automata.estados_finales),
        "tabla_transicion": automata.tabla_transicion,
        "resultados": resultados,
        "resumen": {
            "cadenas_evaluadas": len(resultados),
            "aceptadas": [r["cadena"] for r in resultados if r["aceptada"]],
            "rechazadas": [r["cadena"] for r in resultados if not r["aceptada"]],
        },
    }


# ---------------------------------------------------------------------------
# Evaluacion de un AFN (incluye transiciones lambda)
# ---------------------------------------------------------------------------

def mover(tabla, estado: str, simbolo: str) -> List[str]:
    """delta(estado, simbolo) para un AFN: regresa el conjunto de destinos."""
    fila = tabla.get(estado, {})
    destinos = set()
    for llave, destino in fila.items():
        coincide = es_lambda(llave) if simbolo == "" else (llave == simbolo)
        if coincide:
            destinos.update(normalizar_destinos(destino))
    return sorted(destinos)


def cerradura_lambda(tabla, estados) -> List[str]:
    """Cerradura-lambda: todo lo alcanzable sin consumir simbolos."""
    pendientes = deque(estados)
    alcanzados = set(estados)
    while pendientes:
        q = pendientes.popleft()
        for destino in mover(tabla, q, ""):
            if destino not in alcanzados:
                alcanzados.add(destino)
                pendientes.append(destino)
    return sorted(alcanzados)


def camino_aceptacion(automata: AFN, cadena: str):
    """Busca (BFS) un camino concreto que acepte la cadena, para poder mostrarlo."""
    tabla = automata.tabla_transicion
    finales = set(automata.estados_finales)

    inicio = (automata.estado_inicial, 0)
    cola = deque([inicio])
    # (estado, indice) -> (estado_previo, indice_previo, simbolo_leido)
    previo = {inicio: None}

    while cola:
        estado, i = cola.popleft()

        if i == len(cadena) and estado in finales:
            camino = []
            actual = (estado, i)
            while previo[actual] is not None:
                anterior, simbolo = previo[actual]
                camino.append((anterior[0], simbolo, actual[0]))
                actual = anterior
            camino.reverse()
            return camino

        # transiciones lambda: avanzan de estado sin consumir simbolo
        for destino in mover(tabla, estado, ""):
            siguiente = (destino, i)
            if siguiente not in previo:
                previo[siguiente] = ((estado, i), LAMBDA)
                cola.append(siguiente)

        # transicion leyendo el siguiente simbolo de la cadena
        if i < len(cadena):
            for destino in mover(tabla, estado, cadena[i]):
                siguiente = (destino, i + 1)
                if siguiente not in previo:
                    previo[siguiente] = ((estado, i), cadena[i])
                    cola.append(siguiente)

    return None


def evaluar_cadena_afn(automata: AFN, cadena: str) -> dict:
    """Simula el AFN por conjuntos de estados (construccion de subconjuntos)."""
    tabla = automata.tabla_transicion
    finales = set(automata.estados_finales)

    actuales = cerradura_lambda(tabla, [automata.estado_inicial])

    pasos: List[dict] = []
    configuraciones = [f"({conjunto(actuales)}, {mostrar(cadena)})"]
    notacion_inicial = (f"cerradura-λ({conjunto([automata.estado_inicial])}) = {conjunto(actuales)}")

    for i, simbolo in enumerate(cadena):
        directos = sorted({d for q in actuales for d in mover(tabla, q, simbolo)})
        siguientes = cerradura_lambda(tabla, directos)

        pasos.append({
            "paso": i + 1,
            "estados_origen": actuales,
            "simbolo": simbolo,
            "estados_destino": siguientes,
            "notacion": (f"δ({conjunto(actuales)}, {simbolo}) = {conjunto(directos)}"
                         + (f"  →  cerradura-λ = {conjunto(siguientes)}"
                            if siguientes != directos else "")),
        })

        actuales = siguientes
        configuraciones.append(f"({conjunto(actuales)}, {mostrar(cadena[i + 1:])})")

        if not actuales:
            break

    alcanzados_finales = sorted(set(actuales) & finales)
    aceptada = bool(alcanzados_finales)

    if not actuales:
        motivo = ("El conjunto de estados alcanzables quedo vacio: ninguna rama del "
                  "AFN pudo seguir leyendo la cadena.")
    elif aceptada:
        motivo = (f"Al terminar la cadena el conjunto alcanzado es {conjunto(actuales)} y "
                  f"contiene el/los estado(s) final(es) {conjunto(alcanzados_finales)}, "
                  f"asi que existe al menos un camino de aceptacion.")
    else:
        motivo = (f"Al terminar la cadena el conjunto alcanzado es {conjunto(actuales)} y "
                  f"ninguno de esos estados es final.")

    camino = camino_aceptacion(automata, cadena) if aceptada else None
    if camino is not None:
        if camino:
            texto_camino = camino[0][0] + "".join(
                f" --{s}--> {destino}" for _, s, destino in camino
            )
        else:
            texto_camino = automata.estado_inicial
    else:
        texto_camino = None

    return {
        "cadena": mostrar(cadena),
        "aceptada": aceptada,
        "estados_alcanzados": actuales,
        "estados_finales_alcanzados": alcanzados_finales,
        "notacion_transicion": {
            "cerradura_inicial": notacion_inicial,
            "pasos": [p["notacion"] for p in pasos],
            "configuraciones": " ⊢ ".join(configuraciones),
            "funcion_extendida": (f"δ*({conjunto([automata.estado_inicial])}, "
                                  f"{mostrar(cadena)}) = {conjunto(actuales)}"),
            "camino_de_aceptacion": texto_camino,
        },
        "detalle_pasos": pasos,
        "motivo": motivo,
    }


@app.post("/afn/evaluar", summary="Evalua cadenas sobre un AFN (admite transiciones λ)")
def evaluar_afn(automata: AFN):
    estados, alfabeto = describir(automata.tabla_transicion)
    validar(estados, automata.estado_inicial, automata.estados_finales)

    tiene_lambda = any(
        es_lambda(simbolo)
        for fila in automata.tabla_transicion.values()
        for simbolo in fila
    )

    resultados = [evaluar_cadena_afn(automata, c) for c in automata.cadenas]

    return {
        "tipo": "AFN-λ" if tiene_lambda else "AFN",
        "definicion_formal": "M = (Q, Σ, δ, q0, F)  con  δ: Q × (Σ ∪ {λ}) → P(Q)",
        "estados_totales": estados,
        "numero_de_estados": len(estados),
        "alfabeto": alfabeto,
        "estado_inicial": automata.estado_inicial,
        "estados_finales": sorted(automata.estados_finales),
        "tiene_transiciones_lambda": tiene_lambda,
        "tabla_transicion": automata.tabla_transicion,
        "resultados": resultados,
        "resumen": {
            "cadenas_evaluadas": len(resultados),
            "aceptadas": [r["cadena"] for r in resultados if r["aceptada"]],
            "rechazadas": [r["cadena"] for r in resultados if not r["aceptada"]],
        },
    }


# ---------------------------------------------------------------------------
# Raiz: ayuda rapida del servicio
# ---------------------------------------------------------------------------

@app.get("/", summary="Informacion del servicio")
def read_root():
    return {
        "actividad": "Actividad 6 - Evaluador de cadenas para AFD y AFN",
        "autor": "Angel Rugerio Jimenez - 201720",
        "endpoints": {
            "POST /afd/evaluar": "Evalua cadenas sobre un AFD",
            "POST /afn/evaluar": "Evalua cadenas sobre un AFN (con o sin transiciones λ)",
        },
        "documentacion_interactiva": "/docs",
    }
