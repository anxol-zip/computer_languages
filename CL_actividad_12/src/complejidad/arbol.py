# Actividad 11 - Lenguajes de Computacion (reutilizada en la Actividad 12)
# Angel Rugerio Jimenez  #201720
#
# Etapa 2: arbol de bloques. Lineas logicas -> arbol segun la sangria.
#
# El cuerpo de un for, while, if o def son sus hijos. Cada nodo ademas guarda los
# resultados que le escribe el analizador (etapa 3) y que lee el reporte (etapa 4).

import re

from complejidad.escaner import LineaLogica
from complejidad.notacion import UNO

PALABRAS_COMPUESTAS = {"def", "class", "for", "while", "if", "elif", "else",
                       "try", "except", "finally", "with"}


class Nodo:
    def __init__(self, linea: LineaLogica, texto: str | None = None):
        self.linea = linea
        self.texto = linea.texto if texto is None else texto
        self.tipo = clasificar(self.texto)
        self.hijos = []
        # solo para los def (los llena el analizador)
        self.nombre = None      # nombre de la funcion
        self.recursion = ""     # explicacion del tipo de recursion, si la hay
        # resultados del analisis
        self.propio = None      # costo de UNA ejecucion de la linea
        self.veces = UNO        # cuantas veces se ejecuta
        self.acumulado = None   # propio x veces: lo que aporta a la suma
        self.cuenta = True      # False si no entra a la suma (rama no ejecutada)
        self.anotar = True
        self.comentario = ""
        self.nota = ""


def clasificar(texto: str) -> str:
    if texto.startswith("@"):
        return "decorador"
    if re.fullmatch(r"[rRbBuUfF]*(\"\"\"|'''|\"|')+", texto):
        return "cadena"     # docstring o cadena suelta: no es una operacion
    palabra = re.match(r"(?:async\s+)?(\w+)", texto)
    if palabra:
        p = palabra.group(1)
        if p in PALABRAS_COMPUESTAS or p in {"return", "break", "continue", "pass"}:
            return p
        if p in {"import", "from"}:
            return "import"
    return "simple"


def dos_puntos(texto: str) -> int:
    """Posicion del ':' que cierra el encabezado (fuera de parentesis), o -1."""
    profundidad = 0
    for i, c in enumerate(texto):
        if c in "([{":
            profundidad += 1
        elif c in ")]}":
            profundidad -= 1
        elif c == ":" and profundidad == 0:
            return i
    return -1


def construir_arbol(logicas: list) -> Nodo:
    raiz = Nodo(LineaLogica(-1, -1, -1, ""))
    raiz.tipo = "raiz"
    pila = [raiz]

    for linea in logicas:
        while pila[-1].linea.sangria >= linea.sangria:
            pila.pop()
        nodo = Nodo(linea)
        pila[-1].hijos.append(nodo)

        if nodo.tipo in PALABRAS_COMPUESTAS:
            pos = dos_puntos(nodo.texto)
            cuerpo = nodo.texto[pos + 1:].strip() if pos >= 0 else ""
            if cuerpo:
                # una sola linea, p. ej.  if n < 0: return None
                nodo.texto = nodo.texto[:pos + 1]
                nodo.hijos.append(Nodo(linea, cuerpo))
            else:
                pila.append(nodo)
    return raiz


# ---------------------------------------------------------------------------
# Consultas sobre el arbol (las usan el analizador y el reporte)
# ---------------------------------------------------------------------------

def agrupar(hijos: list) -> list:
    """Junta los if / elif / else consecutivos en una lista (una cadena condicional)."""
    grupos, cadena = [], None
    for nodo in hijos:
        if nodo.tipo == "if":
            cadena = [nodo]
            grupos.append(cadena)
        elif nodo.tipo in {"elif", "else"} and cadena is not None:
            cadena.append(nodo)
            if nodo.tipo == "else":
                cadena = None
        else:
            cadena = None
            grupos.append(nodo)
    return grupos


def recorrer(nodo: Nodo, entrar_a_funciones: bool = False):
    """Todos los descendientes de un nodo, sin meterse a funciones anidadas."""
    for hijo in nodo.hijos:
        yield hijo
        if hijo.tipo != "def" or entrar_a_funciones:
            yield from recorrer(hijo, entrar_a_funciones)


def texto_del_cuerpo(nodo: Nodo) -> str:
    return " ".join(n.texto for n in recorrer(nodo))


def contados(nodo: Nodo) -> list:
    """Los descendientes que entran a la suma (con costo calculado)."""
    return [n for n in recorrer(nodo) if n.cuenta and n.acumulado is not None]
