# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Etapa 4: reporte. Arbol ya analizado -> archivo de salida.
#
# Escribe el comentario de complejidad al final de cada linea y agrega el bloque
# final con la suma de las complejidades individuales y la de mayor grado.

from complejidad.arbol import Nodo, contados, recorrer
from complejidad.notacion import UNO, notacion, polinomio


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


def anotar_lineas(lineas: list, raiz: Nodo) -> list:
    """Agrega a cada linea fisica el comentario de la instruccion que termina en ella."""
    # si dos instrucciones comparten linea (if x: return y), gana la mas costosa
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
    return salida


def resumen_final(raiz: Nodo, modo: str) -> tuple:
    """Una seccion por funcion, otra para el nivel principal y el total del programa."""
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

    return bloque, {"modo": modo, "unidades": resumenes, "programa": total}
