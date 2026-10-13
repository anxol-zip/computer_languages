# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Esquemas de Pydantic: que entra a los endpoints de busqueda y que sale de ellos.
# Toda la validacion del grafo vive aqui, asi greedy_search.py y star_search.py
# pueden suponer que la entrada ya es correcta.

import math
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, model_validator

# Porcentaje de nodos que se pueden visitar si no se manda limite_nodos
PORCENTAJE_LIMITE = 0.8

GRAFO_EJEMPLO = {
    "A": [["B", 15], ["C", 22], ["D", 10]], "B": [["E", 35], ["F", 18]],
    "C": [["E", 20], ["G", 45]], "D": [["F", 28], ["G", 30]],
    "E": [["H", 12], ["I", 25]], "F": [["H", 40], ["I", 15]],
    "G": [["I", 10], ["J", 50]], "H": [["J", 14]], "I": [["J", 8]], "J": [],
}


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

class SolicitudBusqueda(BaseModel):
    """Grafo dirigido y ponderado como lista de adyacencia, mas el problema a resolver.

    grafo[nodo] = [[vecino, peso], ...]  (el mismo formato del archivo de la actividad)
    """
    grafo: Dict[str, List[Tuple[str, float]]] = Field(
        ..., description="Lista de adyacencia con pesos: nodo -> [[vecino, peso], ...]",
        examples=[GRAFO_EJEMPLO],
    )
    origen: str = Field(..., examples=["A"])
    destino: str = Field(..., examples=["J"])
    limite_nodos: Optional[int] = Field(
        None, ge=1,
        description="Maximo de nodos a visitar. Si no se manda, es el 80% de los nodos del grafo.",
    )
    coordenadas: Optional[Dict[str, Tuple[float, float]]] = Field(
        None,
        description="Opcional: posicion (x, y) de cada nodo. Si se manda, h(n) es la distancia "
                    "euclidiana al destino; si no, h(n) se calcula con saltos (ver README).",
    )

    @model_validator(mode="after")
    def validar_grafo(self):
        if not self.grafo:
            raise ValueError("El grafo no tiene nodos.")

        # cada vecino debe ser tambien un nodo del grafo, y ningun peso negativo
        # (A* solo garantiza el optimo con costos >= 0)
        for nodo, aristas in self.grafo.items():
            for vecino, peso in aristas:
                if vecino not in self.grafo:
                    raise ValueError(f"La arista {nodo} -> {vecino} apunta a un nodo que no esta en el grafo.")
                if peso < 0:
                    raise ValueError(f"La arista {nodo} -> {vecino} tiene peso negativo ({peso}).")

        for campo, nodo in (("origen", self.origen), ("destino", self.destino)):
            if nodo not in self.grafo:
                raise ValueError(f"El {campo} '{nodo}' no es un nodo del grafo.")

        total = len(self.grafo)
        if self.limite_nodos is None:
            self.limite_nodos = max(1, math.ceil(PORCENTAJE_LIMITE * total))
        elif self.limite_nodos > total:
            raise ValueError(f"limite_nodos ({self.limite_nodos}) es mayor que el numero de nodos ({total}).")

        if self.coordenadas is not None:
            faltantes = [nodo for nodo in self.grafo if nodo not in self.coordenadas]
            if faltantes:
                raise ValueError(f"Faltan coordenadas para los nodos: {', '.join(faltantes)}.")
        return self


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

class ComplejidadTiempo(BaseModel):
    cota: str = Field(..., description="Complejidad temporal asintotica del algoritmo")
    V: int = Field(..., description="Numero de nodos del grafo")
    E: int = Field(..., description="Numero de aristas del grafo")
    operaciones: int = Field(..., description="Operaciones contadas: extracciones de la lista abierta + aristas revisadas")
    tiempo_ms: float = Field(..., description="Tiempo medido de la busqueda, en milisegundos")


class ComplejidadEspacio(BaseModel):
    cota: str = Field(..., description="Complejidad espacial asintotica del algoritmo")
    max_nodos_en_memoria: int = Field(..., description="Maximo de entradas guardadas a la vez en las listas abierta y cerrada")


class ResultadoBusqueda(BaseModel):
    algoritmo: str
    origen: str
    destino: str
    heuristica: str
    limite_nodos: int
    nodos_visitados: int
    solucion: bool
    ruta: List[str]
    costo: Optional[float] = Field(..., description="Suma de los pesos de la ruta (null si no hay solucion)")
    orden_visita: List[str] = Field(..., description="Nodos en el orden en que se visitaron (expandieron)")
    T_n: ComplejidadTiempo = Field(..., serialization_alias="T(n)")
    S_n: ComplejidadEspacio = Field(..., serialization_alias="S(n)")
