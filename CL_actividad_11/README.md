# Actividad 11 — Analizador de complejidad (Big-O y Big-Omega)

**Materia:** Lenguajes de Computación · Otoño 2026

| Nombre completo | No. de cuenta |
|---|---|
| Angel Rugerio Jiménez | 201720 |

---

## Descripción

Este proyecto escala el backend de la [Actividad 6](../CL_actividad_06/) (evaluador de cadenas para
AFD y AFN) con **dos endpoints nuevos** que analizan la complejidad de un programa escrito en
Python:

| Endpoint | Método | Qué regresa |
|---|---|---|
| `/complejidad/peor-caso` | POST | El programa con la complejidad **Big-O** (peor caso) de cada línea como comentario |
| `/complejidad/mejor-caso` | POST | El programa con la complejidad **Big-Omega** (mejor caso) de cada línea como comentario |

Los dos reciben un **archivo** `.py` y regresan **otro archivo** `.py`: el mismo programa, sin
cambiar ni una línea de código, con

1. un comentario al final de cada línea con su complejidad, y
2. un **bloque final de resumen** con la **suma de las complejidades individuales** y la
   **complejidad de mayor grado**.

Los endpoints de la Actividad 6 (`/afd/evaluar` y `/afn/evaluar`) siguen funcionando igual.

| Endpoint | Método | Origen |
|---|---|---|
| `/` | GET | Información del servicio |
| `/afd/evaluar` | POST | Actividad 6 |
| `/afn/evaluar` | POST | Actividad 6 |
| `/complejidad/peor-caso` | POST | **Actividad 11** |
| `/complejidad/mejor-caso` | POST | **Actividad 11** |

## Cómo correr el servicio

El proyecto usa [uv](https://docs.astral.sh/uv/) (en la Actividad 6 era `pip` + `requirements.txt`;
las dependencias ahora viven en [`pyproject.toml`](./pyproject.toml) y las versiones exactas en
`uv.lock`).

```bash
uv sync                 # crea .venv e instala las dependencias de uv.lock
uv run fastapi dev      # modo desarrollo, se recarga solo al guardar
# o bien
uv run cl-actividad-11  # el comando que define [project.scripts]
```

Las dos formas levantan el servicio en `http://127.0.0.1:8000`. La documentación interactiva
(Swagger) está en `http://127.0.0.1:8000/docs`; ahí cada endpoint de complejidad tiene un botón
para subir el archivo y descargar el resultado.

Para regenerar los archivos de [`ejercicios/salidas/`](./ejercicios/salidas/) a través de los
endpoints (no hace falta tener el servidor levantado):

```bash
uv run python generar_salidas.py
```

---

# Operación de los endpoints nuevos

## Entrada

Los dos endpoints reciben lo mismo: un formulario `multipart/form-data` con un solo campo.

| Campo | Tipo | Descripción |
|---|---|---|
| `archivo` | archivo | Programa en Python (`.py`), codificado en UTF-8 |

```bash
curl -X POST http://127.0.0.1:8000/complejidad/peor-caso \
     -F "archivo=@ejercicios/factorial.py" \
     -o factorial_big_o.py

curl -X POST http://127.0.0.1:8000/complejidad/mejor-caso \
     -F "archivo=@ejercicios/factorial.py" \
     -o factorial_big_omega.py
```

Antes de analizar, el servicio comprueba que el archivo sea texto UTF-8, que no esté vacío y que
sea un programa de Python **sintácticamente válido** (lo compila con `compile()` sin ejecutarlo).

## Salida

Si todo está bien la respuesta es `200 OK` con el archivo anotado:

| Encabezado | Valor |
|---|---|
| `Content-Type` | `text/x-python; charset=utf-8` |
| `Content-Disposition` | `attachment; filename="<nombre>_big_o.py"` o `"<nombre>_big_omega.py"` |

El archivo que regresa **sigue siendo un programa de Python válido**: lo único que se agrega son
comentarios, así que se puede volver a ejecutar o volver a mandar al analizador.

### Formato de los comentarios línea por línea

Cada línea que realiza una operación recibe un comentario con una de estas formas:

| Comentario | Significado |
|---|---|
| `# O(1)` | La línea cuesta O(1) y se ejecuta una sola vez |
| `# O(n)` en un `for` / `while` | El encabezado del ciclo: el ciclo da O(n) vueltas |
| `# O(1) x O(n) = O(n)` | La línea cuesta O(1), pero está dentro de un ciclo que la repite O(n) veces, así que aporta O(n) |
| `# O(n) x O(n) = O(n^2)` | Un ciclo de O(n) vueltas dentro de otro ciclo de O(n) vueltas |
| `# funcion f: O(n)` | En la línea `def`: la complejidad total de la función |
| `(…)` al final | Nota que explica la regla aplicada, p. ej. *salida temprana* o *rama no ejecutada en el mejor caso* |

El primer factor es lo que dice la regla de la clase para esa línea (lo mismo que se anota en las
diapositivas); el resultado después del `=` es lo que esa línea **suma** al total, porque una
instrucción dentro de un ciclo no se ejecuta una vez sino tantas veces como dé vueltas el ciclo.

No se anotan las líneas vacías, los comentarios, los docstrings, ni las líneas que no son una
operación (`else:`, `try:`, `finally:`, `pass`, decoradores, `class`).

### Bloque final de resumen

Al final del archivo se agrega un bloque como este (es la salida real de `factorial.py`):

```python
# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- PEOR CASO (Big-O)
# ==========================================================================
# Funcion factorial
#   Suma de complejidades individuales:
#     O(1) + O(1) + O(1) + O(n) + O(n) + O(1)
#     = 2n + 4
#   Complejidad de mayor grado: O(n)
# ==========================================================================
```

- **Suma de complejidades individuales:** todas las complejidades anotadas, en orden, y su suma
  ya simplificada como función de crecimiento (`2n + 4`).
- **Complejidad de mayor grado:** el término dominante de esa suma. Es la complejidad del
  programa: se desprecian las constantes y los términos menores.

Si el archivo tiene varias funciones, hay una sección por función, otra para el código que está
fuera de funciones (*nivel principal*), y una última sección **Programa completo** que junta todo.

## Errores

| Caso | Código | Respuesta |
|---|---|---|
| No se mandó el campo `archivo` | `422` | Error de validación de FastAPI (`Field required`) |
| El archivo no es UTF-8 (p. ej. un binario) | `400` | `El archivo debe ser texto en UTF-8.` |
| El archivo está vacío | `400` | `El archivo esta vacio.` |
| El archivo no es Python válido | `400` | `El archivo no es un programa de Python valido (linea 1): invalid syntax` |

---

# Cómo se calcula la complejidad

El análisis está en [`src/cl_actividad_11/complejidad.py`](./src/cl_actividad_11/complejidad.py) y
tiene cuatro pasos:

1. **Escáner.** Lee el archivo carácter por carácter con un pequeño autómata que distingue tres
   estados: código, cadena de texto y comentario. Así se quitan los comentarios y el contenido de
   las cadenas (un `print("for i in range(n)")` **no** es un ciclo) y se juntan en una sola
   *línea lógica* las instrucciones que ocupan varias líneas (paréntesis abiertos, cadenas
   triples, `\` al final).
2. **Árbol de bloques.** Con la sangría de cada línea lógica se arma un árbol: el cuerpo de un
   `for`, `while`, `if` o `def` son sus hijos.
3. **Reglas de complejidad.** Se recorre el árbol aplicando las reglas de abajo. Cada complejidad
   se guarda como $(2^n)^e \cdot n^k \cdot (\log n)^j$, de modo que multiplicar es sumar
   exponentes y comparar el orden de crecimiento es comparar $(e, k, j)$.
4. **Archivo de salida.** Se escribe el comentario en la última línea física de cada instrucción
   y se agrega el bloque de resumen.

## Reglas del peor caso (Big-O)

Son las reglas vistas en clase: *cada línea que realiza una acción es O(1), siempre que no sea un
ciclo, una recursión o una llamada a otra función que no sea O(1)*.

| Construcción | Complejidad | Ejemplo |
|---|---|---|
| Asignación, comparación, `return`, `print`, `import`, acceso por índice | $O(1)$ | `a = 10` |
| `for` sobre `range(...)` que depende de una variable | $O(n)$ vueltas | `for i in range(n)`, `for j in range(i)` |
| `for` sobre `range(...)` con puros números | $O(1)$ vueltas | `for i in range(10)` |
| `for` sobre una colección | $O(n)$ vueltas | `for x in lista` |
| `while` cuya variable de control se **suma/resta** | $O(n)$ vueltas | `while i < n: i += 1` |
| `while` cuya variable se **multiplica o divide** | $O(\log n)$ vueltas | `while b < n: b *= 2`, `medio = (izq + der) // 2` |
| Ciclo dentro de ciclo | se **multiplican** | `for i…: for j…` → $O(n^2)$ |
| `if` / `elif` / `else` | se suman **todas** las ramas (cota superior) | |
| Comprensión de listas | $O(n)$ por cada `for` | `[x * x for x in lista]` |
| Funciones de Python que recorren la colección | $O(n)$ | `sum`, `max`, `min`, `list(...)`, `.index`, `.count`, `.insert`, rebanadas `lista[:m]` |
| Ordenar | $O(n \log n)$ | `sorted(lista)`, `lista.sort()` |
| Llamada a una función definida en el mismo archivo | lo que cueste esa función | `busquedaLineal(datos, x)` |

### Recursión

Si una función se llama a sí misma, cada línea se ejecuta una vez **por llamada**, así que se
multiplica por el número de llamadas:

| Patrón | Llamadas | Ejemplo |
|---|---|---|
| 1 llamada por nivel, el problema baja en una constante | $O(n)$ | `factorial(n - 1)` |
| 1 llamada por nivel sobre la mitad | $O(\log n)$ | búsqueda binaria recursiva |
| 2 o más llamadas por nivel, el problema baja en una constante | $O(2^n)$ | `fibonacci(n - 1) + fibonacci(n - 2)` |
| 2 llamadas sobre mitades (divide y vencerás) | $\log n$ niveles | Merge Sort → $O(n \log n)$ |

Dos llamadas en **ramas distintas** de un `if` cuentan como una sola, porque en cada pasada solo
se ejecuta una de las dos.

> El caso de divide y vencerás no viene en las diapositivas: se agregó para que algoritmos como
> Merge Sort (que sí aparecen en la tabla de tipos de complejidad) den $O(n \log n)$ y no
> $O(n^2)$. En cada nivel de la recursión el trabajo total es $O(n)$ y hay $\log n$ niveles.

## Reglas del mejor caso (Big-Omega)

Se parte de las mismas reglas y se cambian solo dos cosas, que son las que dependen de **cómo
viene la entrada** y no solo de su tamaño:

| Construcción | Mejor caso | Por qué |
|---|---|---|
| Ciclo con un `return` o `break` en su cuerpo | $\Omega(1)$ vueltas | La salida puede ocurrir en la primera iteración (el elemento buscado está al principio). La nota del comentario dice *salida temprana* |
| `if` / `elif` / `else` | solo se suma la rama **más barata** | En el mejor caso la entrada lleva por el camino más corto. Si no hay `else`, lo más barato es no entrar al `if` |
| `if` dentro de un ciclo con salida temprana | se toma la rama que tiene el `return`/`break` | Es justamente la que hace que el ciclo termine en la primera vuelta |

Las líneas de las ramas que no se toman **sí se anotan** (con su complejidad si se ejecutaran),
pero llevan la nota `(rama no ejecutada en el mejor caso)` y **no entran a la suma**.

En una función **recursiva** no se descarta ninguna rama: el caso base y el caso recursivo se
ejecutan los dos, cada uno en distintas llamadas.

Un ciclo **sin** `return` ni `break` da las mismas vueltas en el mejor y en el peor caso; por eso
Bubble Sort, que siempre recorre todos los pares, queda en $\Omega(n^2)$ igual que en $O(n^2)$.

---

# Resultados de los ejercicios

Los programas son los cuatro **ejercicios del final de la presentación** de notación asintótica
(diapositiva *Ejercicios*), copiados tal cual en [`ejercicios/`](./ejercicios/). Todo lo de abajo
es la salida **real** de los endpoints, generada con `generar_salidas.py` y guardada en
[`ejercicios/salidas/`](./ejercicios/salidas/).

## Resumen

| Ejercicio | Peor caso | Mejor caso | Lo que decide el resultado |
|---|---|---|---|
| `raizCuadrada` | $O(\log n)$ | $\Omega(\log n)$ | El `while` divide entre 2 en cada vuelta y no tiene salida temprana |
| `factorial` | $O(n)$ | $\Omega(n)$ | Un solo `for` de $n - 1$ vueltas |
| `burbuja` | $O(n^2)$ | $\Omega(n^2)$ | Dos `for` anidados sin bandera de "ya está ordenado" |
| `ordenacionBinaria` | $O(\log n)$ | $\Omega(1)$ | El rango se parte a la mitad; en el mejor caso el objetivo está justo en `medio` |

## Ejercicio 1 — `raizCuadrada`

Es el método de Newton para la raíz cuadrada entera. Mientras `x` es mucho mayor que $\sqrt{n}$,
el término `n // x` casi no aporta y cada vuelta **divide `x` entre 2**; por eso el `while` es
$O(\log n)$. No tiene `return` dentro del ciclo, así que el mejor caso da lo mismo.

**Peor caso** (`POST /complejidad/peor-caso`):

```python
def raizCuadrada(n):  # funcion raizCuadrada: O(log n)
    if n < 0:  # O(1)
        return None  # O(1)
    x = n  # O(1)
    y = (x + 1) // 2  # O(1)
    while y < x:  # O(log n)  (la variable de control se divide o multiplica en cada vuelta)
        x = y  # O(1) x O(log n) = O(log n)
        y = (x + n // x) // 2  # O(1) x O(log n) = O(log n)
    return x  # O(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- PEOR CASO (Big-O)
# ==========================================================================
# Funcion raizCuadrada
#   Suma de complejidades individuales:
#     O(1) + O(1) + O(1) + O(1) + O(log n) + O(log n) + O(log n) + O(1)
#     = 3 log n + 5
#   Complejidad de mayor grado: O(log n)
# ==========================================================================
```

**Mejor caso** (`POST /complejidad/mejor-caso`):

```python
def raizCuadrada(n):  # funcion raizCuadrada: Ω(log n)
    if n < 0:  # Ω(1)
        return None  # Ω(1)  (rama no ejecutada en el mejor caso)
    x = n  # Ω(1)
    y = (x + 1) // 2  # Ω(1)
    while y < x:  # Ω(log n)  (la variable de control se divide o multiplica en cada vuelta)
        x = y  # Ω(1) x Ω(log n) = Ω(log n)
        y = (x + n // x) // 2  # Ω(1) x Ω(log n) = Ω(log n)
    return x  # Ω(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- MEJOR CASO (Big-Omega)
# ==========================================================================
# Funcion raizCuadrada
#   Suma de complejidades individuales:
#     Ω(1) + Ω(1) + Ω(1) + Ω(log n) + Ω(log n) + Ω(log n) + Ω(1)
#     = 3 log n + 4
#   Complejidad de mayor grado: Ω(log n)
# ==========================================================================
```

En el mejor caso el `return None` del `if n < 0` queda fuera de la suma: no hay `else`, así que lo
más barato es no entrar.

## Ejercicio 2 — `factorial`

Un solo ciclo de $n - 1$ vueltas con cuerpo $O(1)$: $O(1) + O(n) + O(1) = O(n)$.

**Peor caso:**

```python
def factorial(n):  # funcion factorial: O(n)
    if n < 0:  # O(1)
        return None  # O(1)
    resultado = 1  # O(1)
    for i in range(2, n + 1):  # O(n)
        resultado *= i  # O(1) x O(n) = O(n)
    return resultado  # O(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- PEOR CASO (Big-O)
# ==========================================================================
# Funcion factorial
#   Suma de complejidades individuales:
#     O(1) + O(1) + O(1) + O(n) + O(n) + O(1)
#     = 2n + 4
#   Complejidad de mayor grado: O(n)
# ==========================================================================
```

**Mejor caso:**

```python
def factorial(n):  # funcion factorial: Ω(n)
    if n < 0:  # Ω(1)
        return None  # Ω(1)  (rama no ejecutada en el mejor caso)
    resultado = 1  # Ω(1)
    for i in range(2, n + 1):  # Ω(n)
        resultado *= i  # Ω(1) x Ω(n) = Ω(n)
    return resultado  # Ω(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- MEJOR CASO (Big-Omega)
# ==========================================================================
# Funcion factorial
#   Suma de complejidades individuales:
#     Ω(1) + Ω(1) + Ω(n) + Ω(n) + Ω(1)
#     = 2n + 3
#   Complejidad de mayor grado: Ω(n)
# ==========================================================================
```

## Ejercicio 3 — `burbuja`

Ciclo con variable dependiente: el `for j` da $(n-1) + (n-2) + \dots + 0 = \frac{n(n-1)}{2}$
vueltas, que sigue siendo $O(n^2)$. Como esta versión no tiene una bandera que corte cuando la
lista ya está ordenada, el mejor caso **también** es cuadrático: lo único que cambia es que el
intercambio no se ejecuta (la lista ya venía ordenada).

**Peor caso:**

```python
def burbuja(lista):  # funcion burbuja: O(n^2)
    n = len(lista)  # O(1)
    for i in range(n):  # O(n)
        for j in range(0, n - i - 1):  # O(n) x O(n) = O(n^2)
            if lista[j] > lista[j + 1]:  # O(1) x O(n^2) = O(n^2)
                lista[j], lista[j + 1] = lista[j + 1], lista[j]  # O(1) x O(n^2) = O(n^2)
    return lista  # O(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- PEOR CASO (Big-O)
# ==========================================================================
# Funcion burbuja
#   Suma de complejidades individuales:
#     O(1) + O(n) + O(n^2) + O(n^2) + O(n^2) + O(1)
#     = 3n^2 + n + 2
#   Complejidad de mayor grado: O(n^2)
# ==========================================================================
```

**Mejor caso:**

```python
def burbuja(lista):  # funcion burbuja: Ω(n^2)
    n = len(lista)  # Ω(1)
    for i in range(n):  # Ω(n)
        for j in range(0, n - i - 1):  # Ω(n) x Ω(n) = Ω(n^2)
            if lista[j] > lista[j + 1]:  # Ω(1) x Ω(n^2) = Ω(n^2)
                lista[j], lista[j + 1] = lista[j + 1], lista[j]  # Ω(1) x Ω(n^2) = Ω(n^2)  (rama no ejecutada en el mejor caso)
    return lista  # Ω(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- MEJOR CASO (Big-Omega)
# ==========================================================================
# Funcion burbuja
#   Suma de complejidades individuales:
#     Ω(1) + Ω(n) + Ω(n^2) + Ω(n^2) + Ω(1)
#     = 2n^2 + n + 2
#   Complejidad de mayor grado: Ω(n^2)
# ==========================================================================
```

## Ejercicio 4 — `ordenacionBinaria`

A pesar del nombre, es una **búsqueda** binaria (no ordena). Cada vuelta calcula
`medio = (izquierda + derecha) // 2` y descarta la mitad del rango, así que en el peor caso hay
$\lfloor \log_2 n \rfloor + 1$ vueltas. En el mejor caso el objetivo está en el primer `medio` y
el `return medio` termina el ciclo en la primera vuelta: $\Omega(1)$.

**Peor caso:**

```python
def ordenacionBinaria(lista, objetivo):  # funcion ordenacionBinaria: O(log n)
    izquierda, derecha = 0, len(lista) - 1  # O(1)
    while izquierda <= derecha:  # O(log n)  (la variable de control se divide o multiplica en cada vuelta)
        medio = (izquierda + derecha) // 2  # O(1) x O(log n) = O(log n)
        if lista[medio] == objetivo:  # O(1) x O(log n) = O(log n)
            return medio  # O(1) x O(log n) = O(log n)
        elif lista[medio] < objetivo:  # O(1) x O(log n) = O(log n)
            izquierda = medio + 1  # O(1) x O(log n) = O(log n)
        else:
            derecha = medio - 1  # O(1) x O(log n) = O(log n)
    return -1  # O(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- PEOR CASO (Big-O)
# ==========================================================================
# Funcion ordenacionBinaria
#   Suma de complejidades individuales:
#     O(1) + O(log n) + O(log n) + O(log n) + O(log n) + O(log n) + O(log n)
#     + O(log n) + O(1)
#     = 7 log n + 2
#   Complejidad de mayor grado: O(log n)
# ==========================================================================
```

**Mejor caso:**

```python
def ordenacionBinaria(lista, objetivo):  # funcion ordenacionBinaria: Ω(1)
    izquierda, derecha = 0, len(lista) - 1  # Ω(1)
    while izquierda <= derecha:  # Ω(1)  (salida temprana: en el mejor caso termina en la 1a iteracion)
        medio = (izquierda + derecha) // 2  # Ω(1)
        if lista[medio] == objetivo:  # Ω(1)
            return medio  # Ω(1)
        elif lista[medio] < objetivo:  # Ω(1)
            izquierda = medio + 1  # Ω(1)  (rama no ejecutada en el mejor caso)
        else:
            derecha = medio - 1  # Ω(1)  (rama no ejecutada en el mejor caso)
    return -1  # Ω(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- MEJOR CASO (Big-Omega)
# ==========================================================================
# Funcion ordenacionBinaria
#   Suma de complejidades individuales:
#     Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1)
#     = 7
#   Complejidad de mayor grado: Ω(1)
# ==========================================================================
```

Este ejercicio es el que mejor muestra la diferencia entre los dos endpoints: el mismo código da
$O(\log n)$ y $\Omega(1)$, porque el resultado depende de **dónde** esté el objetivo y no solo de
cuántos elementos tenga la lista.

---

## Sobre la suma de complejidades

En el ejemplo `sumaLista` de la presentación la suma se escribe
$O(1) + O(n) + O(1) + O(1) = n + 3$: la línea `total += elemento` se anota $O(1)$ y se suma una
vez. El analizador la suma como $O(1) \times O(n) = O(n)$, porque esa línea se ejecuta una vez por
cada elemento; por eso para `sumaLista` daría $2n + 2$. Los coeficientes cambian, pero la
**complejidad de mayor grado es la misma**, $O(n)$, y es la única forma de que la suma salga bien
con ciclos anidados: si cada línea de `burbuja` se sumara con su costo aislado, el total daría
$O(n)$ en lugar de $O(n^2)$.

Por la misma razón, un ciclo cuya variable **se suma** de 2 en 2 (`for j in range(1, n, 2)`) da
$n/2$ vueltas y se reporta como $O(n)$: para que un ciclo sea $O(\log n)$ su variable de control
tiene que **multiplicarse o dividirse** (`b *= 2`, `// 2`).

## Limitaciones

El análisis es estático y por reglas, igual que como se hace a mano en clase; no ejecuta el
programa. Por eso:

- Solo analiza **Python**. El resultado se expresa siempre en términos de $n$, sin importar cómo
  se llame la variable en el programa.
- No sabe el **tipo** de las variables: `x in lista` (que es $O(n)$) y `x in conjunto` (que es
  $O(1)$) se ven iguales, así que el operador `in` se toma como $O(1)$.
- Un `while True` (o con la condición en el cuerpo) se asume $O(n)$ y lo indica en la nota.
- En el mejor caso de una función recursiva se reporta el mismo número de llamadas que en el peor
  caso: el analizador no distingue entre el caso base y una salida temprana.
- No modela recursión mutua (`f` llama a `g` y `g` llama a `f`).

## Archivos del repositorio

| Archivo | Contenido |
|---|---|
| [`src/cl_actividad_11/main.py`](./src/cl_actividad_11/main.py) | Servicio FastAPI: endpoints de la Actividad 6 y los dos nuevos de complejidad |
| [`src/cl_actividad_11/complejidad.py`](./src/cl_actividad_11/complejidad.py) | Analizador de complejidad (escáner, árbol, reglas y archivo de salida) |
| [`src/cl_actividad_11/__init__.py`](./src/cl_actividad_11/__init__.py) | Comando `cl-actividad-11` que levanta el servidor |
| [`ejercicios/`](./ejercicios/) | Los cuatro ejercicios de la presentación |
| [`ejercicios/salidas/`](./ejercicios/salidas/) | Los archivos que regresaron los endpoints para cada ejercicio |
| [`generar_salidas.py`](./generar_salidas.py) | Manda cada ejercicio a los dos endpoints y guarda las respuestas |
| [`pyproject.toml`](./pyproject.toml), `uv.lock` | Dependencias del proyecto (uv) |
