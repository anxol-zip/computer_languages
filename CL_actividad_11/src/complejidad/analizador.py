# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Etapa 3: analisis. Recorre el arbol y le escribe a cada nodo su complejidad.
#
# Las reglas son las de la clase de notacion asintotica: una linea que no es ciclo,
# recursion ni llamada a otra funcion es O(1); un ciclo multiplica lo que tiene dentro;
# la complejidad total es la suma y se queda el termino dominante.
#
# Funciona en dos modos:
#   - "peor":  Big-O     -> se suman todas las ramas, los ciclos dan todas sus vueltas
#   - "mejor": Big-Omega -> solo la rama mas barata, un ciclo con return/break da 1 vuelta

import re

from complejidad.arbol import Nodo, agrupar, contados, recorrer, texto_del_cuerpo
from complejidad.notacion import (DOS_A_LA_N, LOG_N, N, N_LOG_N, UNO, multiplicar,
                                  notacion)

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

# range(...) con puros numeros: da las mismas vueltas sin importar n, asi que es O(1).
RANGO_FIJO = r"range\s*\(\s*-?\d+\s*(?:,\s*-?\d+\s*){0,2}\)"

# Una variable que se divide o se multiplica en cada vuelta hace que el while sea O(log n).
PATRON_LOGARITMICO = re.compile(
    r"//\s*2\b|/\s*2\b|>>\s*1\b|\*\s*2\b|\*=\s*[2-9]\b|//=|/=|>>=|<<="
)

# En recursion solo cuenta reducir el problema a la mitad (dividir), no multiplicar.
PATRON_MITAD = re.compile(r"//\s*2\b|/\s*2\b|>>\s*1\b|\[\s*:\s*\w+\s*\]|\[\s*\w+\s*:\s*\]")

# Lineas que no son una operacion: no se anotan ni se suman.
SIN_COSTO = {"else", "try", "except", "finally", "pass", "decorador", "cadena"}


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

        # comprension de listas: cada for que recorre algo que depende de n multiplica
        # por n, igual que un ciclo; los que van sobre un rango fijo no cuentan
        ciclos = len(re.findall(r"\bfor\b", texto))
        fijos = len(re.findall(rf"\bfor\s+[\w\s,()]+?\s+in\s+{RANGO_FIJO}", texto))
        if ciclos > fijos:
            costo = max(costo, (0, ciclos - fijos, 0))

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
            if re.fullmatch(RANGO_FIJO, iterable):
                return UNO, "rango de tamano fijo: no depende de n"
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


def excluir(rama: Nodo) -> None:
    """Marca el cuerpo de una rama que no se ejecuta en el mejor caso."""
    for n in recorrer(rama):
        if n.acumulado is not None and n.cuenta:
            n.cuenta = False
            n.comentario += "  (rama no ejecutada en el mejor caso)"
