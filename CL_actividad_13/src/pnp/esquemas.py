# Actividad 13 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Esquemas de Pydantic: que entra a los endpoints de grafos y que sale de ellos.
# La validacion del grafo vive aqui, asi los algoritmos pueden suponer que la
# entrada ya es correcta.

from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, model_validator

# El agente viajero exacto crece como (n - 1)!: con 15 nodos tarda menos de un segundo,
# pero con 20 serian horas. Arriba de este numero el endpoint /grafos/tsp no corre.
MAX_NODOS_TSP_EXACTO = 15


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

class SolicitudSintetico(BaseModel):
    nodos: int = Field(..., ge=3, le=26, description="Numero de nodos (A, B, C, ...)", examples=[10])
    densidad: float = Field(
        1.0, ge=0, le=1,
        description="Probabilidad de unir cada par de nodos ademas del ciclo base. 1 (por defecto) = grafo completo.",
    )
    peso_min: int = Field(1, ge=0)
    peso_max: int = Field(100, ge=0)
    semilla: Optional[int] = Field(
        None, description="Misma semilla, mismo grafo. Si no se manda, se elige una al azar y se regresa.",
    )

    @model_validator(mode="after")
    def validar_pesos(self):
        if self.peso_min > self.peso_max:
            raise ValueError(f"peso_min ({self.peso_min}) es mayor que peso_max ({self.peso_max}).")
        return self


class SolicitudGrafo(BaseModel):
    """Grafo ponderado como lista de adyacencia: grafo[nodo] = [[vecino, peso], ...]"""
    grafo: Dict[str, List[Tuple[str, float]]] = Field(
        ..., description="Lista de adyacencia con pesos: nodo -> [[vecino, peso], ...]",
    )
    origen: str = Field(..., examples=["A"])

    @model_validator(mode="after")
    def validar_grafo(self):
        if not self.grafo:
            raise ValueError("El grafo no tiene nodos.")
        for nodo, aristas in self.grafo.items():
            for vecino, peso in aristas:
                if vecino not in self.grafo:
                    raise ValueError(f"La arista {nodo} -> {vecino} apunta a un nodo que no esta en el grafo.")
                if peso < 0:
                    raise ValueError(f"La arista {nodo} -> {vecino} tiene peso negativo ({peso}).")
        if self.origen not in self.grafo:
            raise ValueError(f"El origen '{self.origen}' no es un nodo del grafo.")
        return self


class SolicitudDijkstra(SolicitudGrafo):
    destino: str = Field(..., examples=["J"])

    @model_validator(mode="after")
    def validar_destino(self):
        if self.destino not in self.grafo:
            raise ValueError(f"El destino '{self.destino}' no es un nodo del grafo.")
        return self


class SolicitudTSP(SolicitudGrafo):
    """El recorrido sale del origen, pasa una vez por cada nodo y regresa al origen."""


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

class GrafoSintetico(BaseModel):
    semilla: int
    nodos: int
    aristas: int = Field(..., description="Aristas no dirigidas (cada una aparece dos veces en la lista)")
    densidad: float
    grafo: Dict[str, List[Tuple[str, int]]]


class ResultadoGrafo(BaseModel):
    algoritmo: str
    clase: str = Field(..., description="Clase del problema o del metodo: P, NP-dificil o heuristica")
    complejidad: str = Field(..., description="Complejidad temporal del algoritmo")
    origen: str
    destino: Optional[str] = Field(None, description="Solo en Dijkstra; en el agente viajero es el mismo origen")
    solucion: bool
    ruta: List[str]
    costo: Optional[float] = Field(..., description="Costo del camino encontrado (null si no hay solucion)")
    nodos_recorridos: int
    tiempo_ms: float = Field(..., description="Tiempo de ejecucion del algoritmo, en milisegundos")
    memoria_kb: float = Field(..., description="Pico de memoria reservada durante la ejecucion, en KB")
