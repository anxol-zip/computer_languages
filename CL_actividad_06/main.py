# Actividad 6 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
# Axel Garcia Arellano   #201251
#
# Evaluador de cadenas para un AFD y un AFN, expuesto como servicio web con FastAPI.
# Cada evaluador tiene su propio endpoint: /afd/evaluar y /afn/evaluar.

from typing import Dict, List, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Actividad 6 - Evaluador de AFD y AFN",
    description="Servicio web que evalua cadenas sobre automatas finitos deterministas (AFD) "
                "y no deterministas (AFN, con transiciones vacias).",
    version="1.0.0",
)

EPSILON = "ε"

# Llaves que se aceptan como la transicion vacia en un AFN. A proposito no se admiten
# abreviaturas de una sola letra como "e", porque esa letra si puede ser un simbolo
# real del alfabeto (el AFD del Reporte 1 usa 'e').
SIMBOLOS_EPSILON = {"", "ε", "epsilon", "λ", "lambda"}


# ---------------------------------------------------------------------------
# Modelos de entrada
# ---------------------------------------------------------------------------

class AFD(BaseModel):
    """AFD: δ: Q x Σ -> Q, o sea cada celda de la tabla apunta a UN solo estado."""
    estado_inicial: str = Field(..., examples=["q0"])
    estados_finales: List[str] = Field(..., examples=[["q2"]])
    # tabla_transicion[estado][simbolo] = estado_destino
    tabla_transicion: Dict[str, Dict[str, str]] = Field(
        ..., examples=[{"q0": {"a": "q1", "b": "q0"},
                        "q1": {"a": "q1", "b": "q2"},
                        "q2": {"a": "q2", "b": "q2"}}]
    )
    cadenas: List[str] = Field(default_factory=list, examples=[["ab", "ba"]])


class AFN(BaseModel):
    """AFN: Δ: Q x (Σ U {ε}) -> P(Q), o sea cada celda apunta a un CONJUNTO de estados.

    Se acepta tanto una lista (["q1", "q2"]) como un solo estado ("q1"). La columna
    de transiciones vacias se escribe con la llave "" o "ε".
    """
    estado_inicial: str = Field(..., examples=["q0"])
    estados_finales: List[str] = Field(..., examples=[["q2"]])
    # tabla_transicion[estado][simbolo] = [estados_destino]
    tabla_transicion: Dict[str, Dict[str, Union[str, List[str]]]] = Field(
        ..., examples=[{"q0": {"a": ["q0", "q1"], "b": ["q0"]},
                        "q1": {"b": ["q2"]},
                        "q2": {}}]
    )
    cadenas: List[str] = Field(default_factory=list, examples=[["aab", "ba"]])


# ---------------------------------------------------------------------------
# Utilidades comunes a los dos evaluadores
# ---------------------------------------------------------------------------

def es_epsilon(simbolo: str) -> bool:
    """Indica si la llave de la tabla representa la transicion vacia."""
    return simbolo in SIMBOLOS_EPSILON


def mostrar(cadena: str) -> str:
    """La cadena vacia se muestra como ε para que la notacion se lea bien."""
    return cadena if cadena != "" else EPSILON


def conjunto(estados) -> str:
    """Formatea un conjunto de estados como {q0, q1}."""
    return "{" + ", ".join(sorted(estados)) + "}" if estados else "{}"


def normalizar_destinos(destino: Union[str, List[str]]) -> List[str]:
    """Un destino puede venir como cadena o como lista; siempre se regresa lista."""
    if isinstance(destino, str):
        return [destino] if destino else []
    return list(destino)


def describir(tabla) -> tuple:
    """Saca Q y Σ de la propia tabla de transicion.

    Los estados salen unicamente de la tabla (renglones y destinos), nunca del estado
    inicial ni de los finales: asi validar() puede detectar un estado mal escrito en
    lugar de agregarlo en silencio al automata.
    """
    estados = set(tabla.keys())
    alfabeto = set()

    for fila in tabla.values():
        for simbolo, destino in fila.items():
            estados.update(normalizar_destinos(destino))
            if not es_epsilon(simbolo):
                alfabeto.add(simbolo)  # ε no forma parte del alfabeto

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
# Evaluador de AFD
# ---------------------------------------------------------------------------

def evaluar_cadena_afd(automata: AFD, cadena: str) -> dict:
    """Recorre la cadena simbolo por simbolo: δ(q, a) siempre da un solo estado."""
    tabla = automata.tabla_transicion
    actual = automata.estado_inicial

    pasos = []
    recorrido = actual
    motivo = None

    for i, simbolo in enumerate(cadena):
        destino = tabla.get(actual, {}).get(simbolo)

        if destino is None:
            motivo = (f"No existe la transicion δ({actual}, {simbolo}): el AFD se detiene en el "
                      f"simbolo {i + 1} de la cadena (equivale a caer en un estado trampa).")
            break

        pasos.append(f"δ({actual}, {simbolo}) = {destino}")
        recorrido += f" --{simbolo}--> {destino}"
        actual = destino

    consumio_todo = motivo is None
    aceptada = consumio_todo and actual in automata.estados_finales

    if consumio_todo:
        motivo = (f"La cadena se consumio por completo y termino en '{actual}', "
                  f"que {'SI' if aceptada else 'NO'} es un estado final.")

    return {
        "cadena": mostrar(cadena),
        "aceptada": aceptada,
        "estado_final_alcanzado": actual if consumio_todo else None,
        "notacion_transicion": {
            "pasos": pasos,
            "recorrido": recorrido,
        },
        "motivo": motivo,
    }


@app.post("/afd/evaluar", summary="Evalua cadenas sobre un AFD")
def evaluar_afd(automata: AFD):
    estados, alfabeto = describir(automata.tabla_transicion)
    validar(estados, automata.estado_inicial, automata.estados_finales)

    resultados = [evaluar_cadena_afd(automata, c) for c in automata.cadenas]

    return {
        "tipo": "AFD",
        "definicion_formal": "A = (Q, Σ, δ, s, F)  con  δ: Q × Σ → Q",
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
# Evaluador de AFN
# ---------------------------------------------------------------------------

def mover(tabla, estado: str, simbolo: str) -> List[str]:
    """Δ(estado, simbolo): el conjunto de destinos. Con simbolo "" son las ε-transiciones."""
    destinos = set()
    for llave, destino in tabla.get(estado, {}).items():
        coincide = es_epsilon(llave) if simbolo == "" else (llave == simbolo)
        if coincide:
            destinos.update(normalizar_destinos(destino))
    return sorted(destinos)


def cerradura_epsilon(tabla, estados) -> List[str]:
    """Todo lo alcanzable desde `estados` con cero o mas ε-transiciones."""
    pila, alcanzados = list(estados), set(estados)
    while pila:
        q = pila.pop()
        for destino in mover(tabla, q, ""):
            if destino not in alcanzados:
                alcanzados.add(destino)
                pila.append(destino)
    return sorted(alcanzados)


def buscar_camino(tabla, finales, estado: str, cadena: str, i: int, visitados):
    """Busca a profundidad UN recorrido concreto que acepte la cadena.

    Regresa la lista de tripletas (origen, simbolo, destino), o None si esa rama muere.
    """
    if i == len(cadena) and estado in finales:
        return []
    if (estado, i) in visitados:
        return None
    visitados.add((estado, i))

    # primero las ε-transiciones (no consumen simbolo) y luego el simbolo en turno
    opciones = [(EPSILON, destino, i) for destino in mover(tabla, estado, "")]
    if i < len(cadena):
        opciones += [(cadena[i], destino, i + 1) for destino in mover(tabla, estado, cadena[i])]

    for simbolo, destino, siguiente in opciones:
        resto = buscar_camino(tabla, finales, destino, cadena, siguiente, visitados)
        if resto is not None:
            return [(estado, simbolo, destino)] + resto
    return None


def evaluar_cadena_afn(automata: AFN, cadena: str) -> dict:
    """Simula el AFN rastreando la configuracion: el conjunto de estados activos."""
    tabla = automata.tabla_transicion
    finales = set(automata.estados_finales)

    actuales = cerradura_epsilon(tabla, [automata.estado_inicial])
    pasos = []

    for simbolo in cadena:
        directos = sorted({d for q in actuales for d in mover(tabla, q, simbolo)})
        siguientes = cerradura_epsilon(tabla, directos)

        paso = f"Δ({conjunto(actuales)}, {simbolo}) = {conjunto(directos)}"
        if siguientes != directos:
            paso += f"  →  cerradura-ε = {conjunto(siguientes)}"
        pasos.append(paso)

        actuales = siguientes
        if not actuales:
            break  # todas las ramas murieron

    alcanzados_finales = sorted(set(actuales) & finales)
    aceptada = bool(alcanzados_finales)

    if not actuales:
        motivo = ("El conjunto de estados alcanzables quedo vacio (Φ): ninguna rama del AFN "
                  "pudo seguir leyendo la cadena.")
    elif aceptada:
        motivo = (f"La configuracion final es {conjunto(actuales)} y contiene "
                  f"{conjunto(alcanzados_finales)} de F, asi que existe al menos un recorrido "
                  f"que acepta la cadena.")
    else:
        motivo = (f"La configuracion final es {conjunto(actuales)} y ninguno de esos "
                  f"estados es final.")

    camino = None
    if aceptada:
        tripletas = buscar_camino(tabla, finales, automata.estado_inicial, cadena, 0, set())
        camino = automata.estado_inicial + "".join(
            f" --{simbolo}--> {destino}" for _, simbolo, destino in tripletas
        )

    return {
        "cadena": mostrar(cadena),
        "aceptada": aceptada,
        "configuracion_final": actuales,
        "estados_finales_alcanzados": alcanzados_finales,
        "notacion_transicion": {
            "pasos": pasos,
            "camino_de_aceptacion": camino,
        },
        "motivo": motivo,
    }


@app.post("/afn/evaluar", summary="Evalua cadenas sobre un AFN (admite transiciones ε)")
def evaluar_afn(automata: AFN):
    estados, alfabeto = describir(automata.tabla_transicion)
    validar(estados, automata.estado_inicial, automata.estados_finales)

    tiene_epsilon = any(
        es_epsilon(simbolo)
        for fila in automata.tabla_transicion.values()
        for simbolo in fila
    )

    resultados = [evaluar_cadena_afn(automata, c) for c in automata.cadenas]

    return {
        "tipo": "AFN-ε" if tiene_epsilon else "AFN",
        "definicion_formal": "A = (Q, Σ, Δ, s, F)  con  Δ: Q × (Σ ∪ {ε}) → P(Q)",
        "estados_totales": estados,
        "numero_de_estados": len(estados),
        "alfabeto": alfabeto,
        "estado_inicial": automata.estado_inicial,
        "estados_finales": sorted(automata.estados_finales),
        "tiene_transiciones_epsilon": tiene_epsilon,
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
        "equipo": ["Angel Rugerio Jimenez - 201720", "Axel Garcia Arellano - 201251"],
        "endpoints": {
            "POST /afd/evaluar": "Evalua cadenas sobre un AFD",
            "POST /afn/evaluar": "Evalua cadenas sobre un AFN (con o sin transiciones ε)",
        },
        "documentacion_interactiva": "/docs",
    }
