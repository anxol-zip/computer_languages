# Actividad 11 - Lenguajes de Computacion (reutilizada en la Actividad 12)
# Angel Rugerio Jimenez  #201720
#
# Etapa 1: escaner. Lineas fisicas del archivo -> lineas logicas.
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
