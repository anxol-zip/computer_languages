# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Analizador de complejidad linea por linea para programas en Python.
#
# Recibe el codigo fuente como texto y regresa el mismo programa con un comentario
# en cada linea indicando su complejidad, mas un bloque final con el resumen:
# la suma de las complejidades individuales y la de mayor grado.
#
# Funciona en dos modos:
#   - "peor":  notacion Big-O     (cota superior, peor caso)
#   - "mejor": notacion Big-Omega (cota inferior, mejor caso)
#
# Las reglas son las de la clase de notacion asintotica: una linea que no es ciclo,
# recursion ni llamada a otra funcion es O(1); un ciclo multiplica lo que tiene dentro;
# la complejidad total es la suma y se queda el termino dominante.

import re
from collections import Counter

# ---------------------------------------------------------------------------
# Representacion de una complejidad
# ---------------------------------------------------------------------------
#
# Cada complejidad se guarda como una tupla (e, k, j) que significa
#
#     (2^n)^e  *  n^k  *  (log n)^j
#
# Asi O(1) = (0, 0, 0), O(n) = (0, 1, 0), O(n log n) = (0, 1, 1), O(2^n) = (1, 0, 0).
# Multiplicar dos complejidades es sumar sus exponentes, y comparar tuplas en orden
# (e, k, j) es justo comparar tasas de crecimiento: cualquier exponencial le gana a
# cualquier polinomio, y cualquier n^k le gana a cualquier potencia de log n.

UNO = (0, 0, 0)
LOG_N = (0, 0, 1)
N = (0, 1, 0)
N_LOG_N = (0, 1, 1)
DOS_A_LA_N = (1, 0, 0)

SIMBOLOS = {"peor": "O", "mejor": "Ω"}


def multiplicar(a: tuple, b: tuple) -> tuple:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def termino(c: tuple) -> str:
    """Escribe la funcion de crecimiento sin la notacion: n^2, n log n, 2^n, 1."""
    partes = []
    if c[0] == 1:
        partes.append("2^n")
    elif c[0] > 1:
        partes.append(f"2^({c[0]}n)")
    if c[1] == 1:
        partes.append("n")
    elif c[1] > 1:
        partes.append(f"n^{c[1]}")
    if c[2] == 1:
        partes.append("log n")
    elif c[2] > 1:
        partes.append(f"log^{c[2]} n")
    return " ".join(partes) if partes else "1"


def notacion(c: tuple, modo: str) -> str:
    return f"{SIMBOLOS[modo]}({termino(c)})"


def polinomio(terminos: list) -> str:
    """Suma terminos iguales y los ordena de mayor a menor: [n, 1, n, 1] -> 2n + 2."""
    if not terminos:
        return "0"
    conteo = Counter(terminos)
    sumandos = []
    for c in sorted(conteo, reverse=True):
        veces = conteo[c]
        texto = termino(c)
        if texto == "1":
            sumandos.append(str(veces))
        elif veces == 1:
            sumandos.append(texto)
        elif texto.startswith("2^"):
            sumandos.append(f"{veces}({texto})")  # 2(2^n), no 22^n
        elif texto[0].isalpha():
            sumandos.append(f"{veces}{texto}" if texto[0] == "n" else f"{veces} {texto}")
        else:
            sumandos.append(f"{veces}{texto}")
    return " + ".join(sumandos)


# ---------------------------------------------------------------------------
# Patrones que reconoce el analizador
# ---------------------------------------------------------------------------

# Funciones y metodos de Python que NO son O(1). El resto de llamadas a funciones que
# no esten definidas en el mismo archivo se toman como O(1) (print, len, append, ...).
COSTOS_CONOCIDOS = [
    (re.compile(r"\bsorted\s*\(|\.sort\s*\("), N_LOG_N),
    (re.compile(r"\b(sum|max|min|any|all|list|tuple|set|reversed)\s*\("), N),
    (re.compile(r"\.(index|count|remove|insert|extend|copy|join|split)\s*\("), N),
    (re.compile(r"\.pop\s*\(\s*0\s*\)"), N),
    # una rebanada como lista[:medio] copia los elementos: O(n)
    (re.compile(r"\[[^\[\]]*:[^\[\]]*\]"), N),
]

# Una variable que se divide o se multiplica en cada vuelta hace que el while sea O(log n).
PATRON_LOGARITMICO = re.compile(
    r"//\s*2\b|/\s*2\b|>>\s*1\b|\*\s*2\b|\*=\s*[2-9]\b|//=|/=|>>=|<<="
)

# En recursion solo cuenta reducir el problema a la mitad (dividir), no multiplicar.
PATRON_MITAD = re.compile(r"//\s*2\b|/\s*2\b|>>\s*1\b|\[\s*:\s*\w+\s*\]|\[\s*\w+\s*:\s*\]")

PALABRAS_COMPUESTAS = {"def", "class", "for", "while", "if", "elif", "else",
                       "try", "except", "finally", "with"}

# Lineas que no son una operacion: no se anotan ni se suman.
SIN_COSTO = {"else", "try", "except", "finally", "pass", "decorador", "cadena"}


# ---------------------------------------------------------------------------
# 1. Escaner: lineas fisicas -> lineas logicas
# ---------------------------------------------------------------------------
#
# Es un automata sencillo: lee caracter por caracter y cambia de estado al entrar o
# salir de una cadena de texto. Sirve para dos cosas:
#   - quitar comentarios y el contenido de las cadenas, para que un "for" escrito
#     dentro de un print("...") no se confunda con un ciclo;
#   - juntar en una sola linea logica las instrucciones que ocupan varias lineas
#     (parentesis abiertos, cadenas triples, diagonal invertida al final).

class LineaLogica:
    def __init__(self, inicio: int, fin: int, sangria: int, texto: str):
        self.inicio = inicio    # primera linea fisica (indice desde 0)
        self.fin = fin          # ultima linea fisica: ahi se escribe el comentario
        self.sangria = sangria
        self.texto = texto      # codigo limpio: sin comentarios ni contenido de cadenas


def escanear(lineas: list) -> list:
    logicas = []
    comilla = None      # None = fuera de cadena; si no, el caracter que la abrio
    triple = False
    profundidad = 0     # parentesis, corchetes y llaves abiertos
    partes, inicio, sangria = [], None, 0

    for idx, linea in enumerate(lineas):
        if inicio is None:
            vacia = linea.strip() == "" or linea.strip().startswith("#")
            if vacia:
                continue
            inicio = idx
            expandida = linea.expandtabs()
            sangria = len(expandida) - len(expandida.lstrip())

        limpio, i = [], 0
        while i < len(linea):
            c = linea[i]
            if comilla:                                     # estado: dentro de cadena
                if c == "\\":
                    i += 2
                elif triple and linea.startswith(comilla * 3, i):
                    limpio.append(comilla * 3)
                    comilla, i = None, i + 3
                elif not triple and c == comilla:
                    limpio.append(c)
                    comilla, i = None, i + 1
                else:
                    i += 1
                continue
            if c == "#":                                    # estado: comentario
                break
            if c in "\"'":                                  # abre una cadena
                triple = linea.startswith(c * 3, i)
                limpio.append(c * 3 if triple else c)
                comilla, i = c, i + (3 if triple else 1)
                continue
            if c in "([{":
                profundidad += 1
            elif c in ")]}":
                profundidad -= 1
            limpio.append(c)
            i += 1

        if comilla and not triple:      # cadena simple sin cerrar: no sigue a la otra linea
            comilla = None

        texto = "".join(limpio).strip()
        diagonal = texto.endswith("\\")
        partes.append(texto.rstrip("\\").strip())

        if profundidad > 0 or comilla or diagonal:
            continue    # la instruccion sigue en la siguiente linea fisica

        logicas.append(LineaLogica(inicio, idx, sangria, " ".join(p for p in partes if p)))
        partes, inicio = [], None

    return logicas


# ---------------------------------------------------------------------------
# 2. Arbol de bloques segun la sangria
# ---------------------------------------------------------------------------

class Nodo:
    def __init__(self, linea: LineaLogica, texto: str = None):
        self.linea = linea
        self.texto = linea.texto if texto is None else texto
        self.tipo = clasificar(self.texto)
        self.hijos = []
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


# ---------------------------------------------------------------------------
# 3. Analisis de complejidad
# ---------------------------------------------------------------------------

class Analizador:
    def __init__(self, raiz: Nodo, modo: str):
        self.raiz = raiz
        self.modo = modo
        self.funciones = {}         # nombre -> nodo def
        self.costo_funciones = {}   # nombre -> complejidad total de la funcion
        self.en_proceso = set()     # para no ciclarse con recursion mutua
        for nodo in recorrer(raiz, entrar_a_funciones=True):
            if nodo.tipo == "def":
                nombre = re.match(r"(?:async\s+)?def\s+(\w+)", nodo.texto).group(1)
                nodo.nombre = nombre
                self.funciones[nombre] = nodo

    def simbolo(self, c: tuple) -> str:
        return notacion(c, self.modo)

    # ----- costo de una sola linea -----------------------------------------

    def costo_expresion(self, texto: str, funcion_actual: str) -> tuple:
        """Costo de evaluar una expresion UNA vez: O(1) salvo llamadas costosas."""
        costo = UNO
        for patron, c in COSTOS_CONOCIDOS:
            if patron.search(texto):
                costo = max(costo, c)

        # comprension de listas: [x for x in lista] recorre la lista
        anidadas = len(re.findall(r"\bfor\b", texto))
        if anidadas:
            costo = max(costo, (0, anidadas, 0))

        # llamada a otra funcion definida en el mismo archivo: cuesta lo que esa funcion
        for nombre in self.funciones:
            if nombre != funcion_actual and re.search(rf"\b{nombre}\s*\(", texto):
                costo = max(costo, self.costo_funcion(nombre))
        return costo

    # ----- ciclos -----------------------------------------------------------

    def tiene_salida(self, ciclo: Nodo) -> bool:
        """Hay un return en el cuerpo, o un break que rompe ESTE ciclo (no uno interno)."""
        def buscar(nodo, dentro_de_otro_ciclo):
            for hijo in nodo.hijos:
                if hijo.tipo == "def":
                    continue
                if hijo.tipo == "return":
                    return True
                if hijo.tipo == "break" and not dentro_de_otro_ciclo:
                    return True
                if buscar(hijo, dentro_de_otro_ciclo or hijo.tipo in {"for", "while"}):
                    return True
            return False
        return buscar(ciclo, False)

    def iteraciones(self, ciclo: Nodo) -> tuple:
        """Cuantas veces se repite el cuerpo del ciclo, y por que."""
        if self.modo == "mejor" and self.tiene_salida(ciclo):
            return UNO, "salida temprana: en el mejor caso termina en la 1a iteracion"

        texto = ciclo.texto
        if ciclo.tipo == "for":
            iterable = re.sub(r"^(?:async\s+)?for\s+.+?\s+in\s+", "", texto).rstrip(":").strip()
            rango = re.fullmatch(r"range\s*\((.*)\)", iterable)
            if rango:
                argumentos = [a.strip() for a in rango.group(1).split(",")]
                if all(re.fullmatch(r"-?\d+", a) for a in argumentos):
                    return UNO, "rango de tamano fijo: no depende de n"
                return N, ""
            return N, ""

        # while
        condicion = texto[len("while"):].rstrip(":").strip()
        if condicion in {"True", "1"}:
            return N, "ciclo sin condicion de paro explicita: se asume O(n)"
        if PATRON_LOGARITMICO.search(texto_del_cuerpo(ciclo) + " " + condicion):
            return LOG_N, "la variable de control se divide o multiplica en cada vuelta"
        return N, ""

    # ----- recursion --------------------------------------------------------

    def llamadas_por_camino(self, hijos: list, nombre: str) -> int:
        """Llamadas recursivas que se ejecutan en una misma pasada por la funcion.

        Dos llamadas en ramas distintas de un if (busqueda binaria recursiva) cuentan
        como una sola, porque solo una de las dos se ejecuta.
        """
        patron = re.compile(rf"\b{nombre}\s*\(")
        total = 0
        for grupo in agrupar(hijos):
            if isinstance(grupo, list):
                total += max(len(patron.findall(r.texto)) + self.llamadas_por_camino(r.hijos, nombre)
                             for r in grupo)
            elif grupo.tipo != "def":
                total += len(patron.findall(grupo.texto)) + self.llamadas_por_camino(grupo.hijos, nombre)
        return total

    def tipo_de_recursion(self, funcion: Nodo):
        llamadas = self.llamadas_por_camino(funcion.hijos, funcion.nombre)
        if llamadas == 0:
            return None, ""
        divide = PATRON_MITAD.search(texto_del_cuerpo(funcion)) is not None
        if llamadas == 1 and not divide:
            return "lineal", "1 llamada por nivel, el problema baja en una constante -> n llamadas"
        if llamadas == 1:
            return "logaritmica", "1 llamada por nivel sobre la mitad del problema -> log n llamadas"
        if not divide:
            return "exponencial", (f"{llamadas} llamadas por nivel, el problema baja en una "
                                   f"constante -> 2^n llamadas")
        return "divide", f"{llamadas} llamadas por nivel sobre mitades (divide y venceras) -> log n niveles"

    def aplicar_recursion(self, costo: tuple, recursion: str) -> tuple:
        """Costo total de una linea que se ejecuta en cada llamada de la recursion."""
        if recursion is None:
            return costo
        if recursion == "lineal":
            return multiplicar(costo, N)
        if recursion == "logaritmica":
            return multiplicar(costo, LOG_N)
        if recursion == "exponencial":
            return multiplicar(costo, DOS_A_LA_N)
        # divide y venceras con 2 mitades: el trabajo de cada nivel suma n en total
        if costo[0] == 0 and costo[1] == 0:
            return N                            # 1 + 2 + 4 + ... + n  =  O(n)
        if costo[0] == 0 and costo[1] == 1:
            return multiplicar(costo, LOG_N)    # n por nivel, log n niveles
        return costo                            # domina el primer nivel

    # ----- funciones --------------------------------------------------------

    def costo_funcion(self, nombre: str) -> tuple:
        if nombre in self.costo_funciones:
            return self.costo_funciones[nombre]
        if nombre in self.en_proceso:
            return UNO      # recursion mutua: no se modela
        self.analizar_funcion(self.funciones[nombre])
        return self.costo_funciones[nombre]

    def analizar_funcion(self, funcion: Nodo) -> None:
        if funcion.nombre in self.costo_funciones:
            return
        self.en_proceso.add(funcion.nombre)

        recursion, explicacion = self.tipo_de_recursion(funcion)
        funcion.recursion = explicacion
        contexto = {"funcion": funcion.nombre, "recursion": recursion, "salida": False}
        self.analizar_bloque(funcion.hijos, UNO, contexto)

        total = max((n.acumulado for n in contados(funcion)), default=UNO)
        self.costo_funciones[funcion.nombre] = total
        self.en_proceso.discard(funcion.nombre)

        funcion.cuenta = False      # definir la funcion no cuesta; ejecutarla si
        funcion.comentario = f"# funcion {funcion.nombre}: {self.simbolo(total)}"

    # ----- recorrido del programa -------------------------------------------

    def registrar(self, nodo: Nodo, propio: tuple, veces: tuple, contexto: dict, nota: str = ""):
        recursion = contexto["recursion"]
        nodo.propio = propio
        nodo.veces = veces
        nodo.acumulado = self.aplicar_recursion(multiplicar(propio, veces), recursion)
        nodo.nota = nota
        s = self.simbolo

        if recursion == "divide":
            nodo.comentario = (f"# {s(multiplicar(propio, veces))} por llamada "
                               f"-> {s(nodo.acumulado)} en toda la recursion")
        elif recursion:
            total_veces = self.aplicar_recursion(veces, recursion)
            nodo.comentario = f"# {s(propio)} x {s(total_veces)} = {s(nodo.acumulado)}"
        elif veces == UNO:
            nodo.comentario = f"# {s(propio)}"
        else:
            nodo.comentario = f"# {s(propio)} x {s(veces)} = {s(nodo.acumulado)}"
        if nota:
            nodo.comentario += f"  ({nota})"

    def analizar_bloque(self, hijos: list, veces: tuple, contexto: dict) -> None:
        for grupo in agrupar(hijos):
            if isinstance(grupo, list):
                self.analizar_condicional(grupo, veces, contexto)
            else:
                self.analizar_nodo(grupo, veces, contexto)

    def analizar_nodo(self, nodo: Nodo, veces: tuple, contexto: dict) -> None:
        tipo = nodo.tipo

        if tipo == "def":
            self.analizar_funcion(nodo)
            return

        if tipo == "class" or tipo in SIN_COSTO:
            nodo.cuenta, nodo.anotar = False, False
            self.analizar_bloque(nodo.hijos, veces, contexto)
            return

        if tipo in {"for", "while"}:
            vueltas, nota = self.iteraciones(nodo)
            if tipo == "for":
                expresion = re.sub(r"^(?:async\s+)?for\s+.+?\s+in\s+", "", nodo.texto)
            else:
                expresion = nodo.texto[len("while"):]
            # el encabezado se evalua una vez por vuelta: cuesta lo que el ciclo da vueltas
            propio = max(vueltas, self.costo_expresion(expresion.rstrip(":"), contexto["funcion"]))
            self.registrar(nodo, propio, veces, contexto, nota)

            interno = dict(contexto, salida=(vueltas == UNO and "salida" in nota))
            self.analizar_bloque(nodo.hijos, multiplicar(veces, vueltas), interno)
            return

        texto = nodo.texto
        if tipo == "with":
            texto = texto[len("with"):].rstrip(":")
        self.registrar(nodo, self.costo_expresion(texto, contexto["funcion"]), veces, contexto)
        self.analizar_bloque(nodo.hijos, veces, contexto)

    def analizar_condicional(self, ramas: list, veces: tuple, contexto: dict) -> None:
        for rama in ramas:
            if rama.tipo in {"if", "elif"}:
                condicion = re.sub(r"^(el)?if\s+", "", rama.texto).rstrip(":")
                self.registrar(rama, self.costo_expresion(condicion, contexto["funcion"]),
                               veces, contexto)
            else:
                rama.cuenta, rama.anotar = False, False
            self.analizar_bloque(rama.hijos, veces, contexto)

        if self.modo != "mejor":
            return  # peor caso: se suman todas las ramas (cota superior)
        if contexto["recursion"]:
            return  # en recursion todas las ramas se ejecutan en alguna llamada (el caso base en las hojas)

        # Mejor caso: solo se ejecuta UNA rama, la mas barata. Si no hay else, existe
        # la opcion de no entrar a ninguna, que siempre es la mas barata.
        def costo_rama(rama):
            return max((n.acumulado for n in contados(rama)), default=(-1, -1, -1))

        elegida = None
        if contexto["salida"]:
            # dentro de un ciclo que termina temprano, la rama que tiene el
            # return/break es justamente la que se toma en el mejor caso
            for rama in ramas:
                if any(n.tipo in {"return", "break"} for n in recorrer(rama)):
                    elegida = rama
                    break
        if elegida is None and ramas[-1].tipo == "else":
            elegida = min(ramas, key=costo_rama)

        for rama in ramas:
            if rama is not elegida:
                excluir(rama)


def contados(nodo: Nodo) -> list:
    """Los descendientes que entran a la suma (con costo calculado)."""
    return [n for n in recorrer(nodo) if n.cuenta and n.acumulado is not None]


def excluir(rama: Nodo) -> None:
    """Marca el cuerpo de una rama que no se ejecuta en el mejor caso."""
    for n in recorrer(rama):
        if n.acumulado is not None and n.cuenta:
            n.cuenta = False
            n.comentario += "  (rama no ejecutada en el mejor caso)"


# ---------------------------------------------------------------------------
# 4. Archivo de salida
# ---------------------------------------------------------------------------

def envolver(sumandos: list, sangria: str, ancho: int = 76) -> list:
    """Parte 'O(1) + O(n) + ...' en varias lineas de comentario si es muy largo."""
    renglones, actual = [], ""
    for i, s in enumerate(sumandos):
        pieza = s if i == 0 else f" + {s}"
        if actual and len(sangria + actual + pieza) > ancho:
            renglones.append(actual)
            actual = f"+ {s}"
        else:
            actual += pieza
    renglones.append(actual)
    return [f"#{sangria}{r}" for r in renglones]


def bloque_de_resumen(unidad: str, nodos: list, modo: str, extra: str = "") -> tuple:
    terminos = [n.acumulado for n in nodos]
    mayor = max(terminos, default=UNO)
    lineas = [f"# {unidad}"]
    if extra:
        lineas.append(f"#   Recursion: {extra}")
    lineas.append("#   Suma de complejidades individuales:")
    lineas += envolver([notacion(t, modo) for t in terminos] or ["(sin operaciones)"], "     ")
    lineas.append(f"#     = {polinomio(terminos)}")
    lineas.append(f"#   Complejidad de mayor grado: {notacion(mayor, modo)}")
    resumen = {
        "unidad": unidad,
        "suma": polinomio(terminos),
        "mayor_grado": notacion(mayor, modo),
    }
    return lineas, resumen


def analizar(codigo: str, modo: str) -> tuple:
    """Regresa (programa anotado, resumen en diccionario)."""
    if modo not in SIMBOLOS:
        raise ValueError(f"Modo desconocido: {modo}")

    lineas = codigo.splitlines()
    raiz = construir_arbol(escanear(lineas))
    analizador = Analizador(raiz, modo)
    analizador.analizar_bloque(raiz.hijos, UNO, {"funcion": None, "recursion": None, "salida": False})

    # comentarios linea por linea (si dos instrucciones comparten linea, gana la mas costosa)
    por_linea = {}
    for nodo in recorrer(raiz, entrar_a_funciones=True):
        if not nodo.anotar or not nodo.comentario:
            continue
        previo = por_linea.get(nodo.linea.fin)
        if previo is None or (nodo.acumulado or UNO) > (previo.acumulado or UNO):
            por_linea[nodo.linea.fin] = nodo

    salida = []
    for idx, linea in enumerate(lineas):
        if idx in por_linea:
            salida.append(f"{linea.rstrip()}  {por_linea[idx].comentario}")
        else:
            salida.append(linea)

    # resumen: una seccion por funcion, otra para el nivel principal y el total
    titulo = "PEOR CASO (Big-O)" if modo == "peor" else "MEJOR CASO (Big-Omega)"
    barra = "# " + "=" * 74
    division = "# " + "-" * 74
    bloque = ["", "", barra, f"# RESUMEN DE COMPLEJIDAD -- {titulo}", barra]
    resumenes, todos = [], []

    funciones = [n for n in recorrer(raiz, entrar_a_funciones=True) if n.tipo == "def"]
    for funcion in funciones:
        nodos = sorted(contados(funcion), key=lambda n: n.linea.fin)
        todos += nodos
        texto, resumen = bloque_de_resumen(f"Funcion {funcion.nombre}", nodos, modo,
                                           funcion.recursion)
        bloque += texto + [division]
        resumenes.append(resumen)

    # contados() no entra a las funciones: esto es solo el codigo del nivel principal
    principal = sorted(contados(raiz), key=lambda n: n.linea.fin)
    if principal:
        todos += principal
        texto, resumen = bloque_de_resumen("Nivel principal (fuera de funciones)", principal, modo)
        bloque += texto + [division]
        resumenes.append(resumen)

    todos.sort(key=lambda n: n.linea.fin)
    texto, total = bloque_de_resumen("Programa completo", todos, modo)
    if len(resumenes) > 1:
        bloque += texto + [barra]
    else:
        bloque[-1] = barra  # una sola unidad: su resumen ya es el del programa completo

    resultado = "\n".join(salida + bloque) + "\n"
    return resultado, {"modo": modo, "unidades": resumenes, "programa": total}

