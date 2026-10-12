# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Plantillas del prompt que se le manda al modelo de lenguaje.
#
# Parten de la variable `template` del notebook del profesor
# (ejemplo_profesor/analizador.ipynb), con cuatro cambios:
#   - hay una plantilla por caso: peor caso (Big-O) y mejor caso (Big-Omega);
#   - el bloque final pide lo que exige la actividad: la suma de las complejidades
#     individuales y la complejidad de mayor grado;
#   - se le recuerdan al modelo las reglas vistas en clase, para que no las invente,
#     y se le da un ejemplo de respuesta (sumaLista, de la presentacion de la clase);
#   - se le pide que la suma tenga un termino por linea comentada, en orden: sin
#     esa regla el modelo omitia terminos y la suma no cuadraba con los comentarios.
# La primera linea del template ("Eres un experto en analisis de complejidad
# algoritmica.") ahora va como system instruction en modelo.py.

from pathlib import PurePath

PLANTILLA = """Tu tarea es tomar un código desarrollado en cualquier lenguaje de programación y crear una versión alterna del mismo código agregando comentarios. Estos comentarios deberán contener la complejidad algorítmica en notación {notacion} ({caso}) línea por línea, al final de cada línea que realice una operación. Además, debes seguir el estilo de comentarios que corresponda al lenguaje de programación.
Añade un bloque al inicio, donde se describa el propósito general del código, y un bloque final con la suma de las complejidades individuales y la complejidad de mayor grado.

Usa estas reglas:
- Una línea que no es ciclo, recursión ni llamada a una función costosa es {simbolo}(1).
- Un ciclo que recorre los n datos es {simbolo}(n); una línea dentro de un ciclo se ejecuta n veces, y ciclos anidados se multiplican: {simbolo}(n^2).
- Un ciclo cuya variable se multiplica o se divide en cada vuelta es {simbolo}(log n).
- Una función que se llama a sí misma dos veces reduciendo n en una constante es {simbolo}(2^n).
- La suma de complejidades individuales lleva exactamente un término por cada línea que comentaste con una complejidad, en el mismo orden en que aparecen; después agrupa los términos iguales (por ejemplo, 2n + 2).
- La complejidad de mayor grado conserva solo el término dominante de esa suma y descarta las constantes.
{regla_del_caso}

Ejemplo de respuesta para un código en Python:
# Proposito: suma los elementos de una lista.
def sumaLista(lista):
    total = 0                   # {simbolo}(1)
    for elemento in lista:      # {simbolo}(n)
        total += elemento       # {simbolo}(n)
    return total                # {simbolo}(1)
# Suma de complejidades individuales: {simbolo}(1) + {simbolo}(n) + {simbolo}(n) + {simbolo}(1) = 2n + 2
# Complejidad de mayor grado: {simbolo}(n)

No modifiques ninguna línea del código original: solo agrega comentarios. Responde únicamente con el código comentado, con el mismo formato del ejemplo, sin explicaciones fuera del código y sin bloques de markdown.

Código a analizar:
```{lenguaje}
{codigo}
```
"""

CASOS = {
    "peor": {
        "notacion": "Big-O",
        "simbolo": "O",
        "caso": "peor de los casos",
        "regla_del_caso": "- Peor caso: supón la entrada más desfavorable; los ciclos dan todas sus vueltas "
                          "y de un if/else se toma la rama más costosa.",
    },
    "mejor": {
        "notacion": "Big-Omega",
        "simbolo": "Ω",
        "caso": "mejor de los casos",
        "regla_del_caso": "- Mejor caso: supón la entrada más favorable; un ciclo que tiene un return o un "
                          "break puede terminar en su primera vuelta ({simbolo}(1)) y de un if/else se toma "
                          "la rama más barata. Las líneas que no se ejecutan en el mejor caso se comentan como "
                          "'no se ejecuta en el mejor caso' y no entran a la suma. Escribe todas las "
                          "complejidades con Ω, no con O.",
    },
}

# Extension del archivo -> nombre del lenguaje para el bloque de codigo del prompt.
# Si la extension no esta aqui, el bloque va sin lenguaje y el modelo lo deduce.
LENGUAJES = {
    ".py": "python", ".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
    ".java": "java", ".js": "javascript", ".ts": "typescript", ".cs": "csharp",
    ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php", ".kt": "kotlin",
    ".swift": "swift",
}


def lenguaje_de(nombre_archivo: str) -> str:
    return LENGUAJES.get(PurePath(nombre_archivo or "").suffix.lower(), "")


def construir_prompt(codigo: str, nombre_archivo: str, modo: str) -> str:
    """Llena la plantilla, como template.format(code=codigo) en el notebook del profesor."""
    caso = CASOS[modo]
    regla = caso["regla_del_caso"].format(simbolo=caso["simbolo"])
    return PLANTILLA.format(
        codigo=codigo.rstrip("\n"),
        lenguaje=lenguaje_de(nombre_archivo),
        notacion=caso["notacion"],
        simbolo=caso["simbolo"],
        caso=caso["caso"],
        regla_del_caso=regla,
    )
