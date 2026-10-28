# Actividad 14 — Implementación de estrategia Divide y Vencerás

**Materia:** Lenguajes de Computación · Otoño 2026

| Nombre completo | No. de cuenta |
|---|---|
| Angel Rugerio Jiménez | 201720 |

---

## Descripción

Implementación recursiva del **algoritmo de Karatsuba** para multiplicar enteros gigantes (20, 50 y 100
dígitos), con medición de **T(N)** y **S(N)** y pruebas que comparan su resultado contra la
multiplicación sin el algoritmo.

Para que la comparación diga algo, Karatsuba se mide junto a otros tres métodos:

| Método | Archivo | Estrategia | Multiplicaciones de un dígito |
|---|---|---|---|
| Escolar | [`escolar.py`](./src/dyv/escolar.py) | La de primaria, dígito por dígito (iterativa) | $N^2$ |
| DyV 4 llamadas | [`clasico.py`](./src/dyv/clasico.py) | Divide y vencerás con 4 subproblemas | $N^2$ |
| **Karatsuba** | [`karatsuba.py`](./src/dyv/karatsuba.py) | Divide y vencerás con **3** subproblemas | $\approx N^{1.585}$ |
| Python `*` | — | El operador del lenguaje, como resultado esperado | — |

## Cómo correr

```bash
uv sync                              # crea el entorno (no hay dependencias externas)
uv run main.py                       # traza de 1234 x 5678 y mediciones con 20, 50 y 100 dígitos
uv run main.py 200 500 1000          # mediciones con otros tamaños
```

Los números se generan con una semilla fija (`14`), así que los conteos de multiplicaciones, llamadas y
profundidad salen idénticos en cada ejecución. Los tiempos cambian un poco de una corrida a otra.

## 1. Divide y vencerás

Como se vio en clase, un algoritmo de divide y vencerás tiene tres fases:

1. **División:** separar el problema en subproblemas que son instancias más pequeñas del mismo problema.
2. **Conquista:** resolver los subproblemas de forma recursiva; los suficientemente pequeños se
   resuelven directo como **caso base**.
3. **Combinación:** juntar las soluciones de los subproblemas en la solución del problema original.

## 2. Algoritmo de Karatsuba

Karatsuba (1960) multiplica dos números de $N$ dígitos partiendo cada uno a la mitad. Con
$m = \lfloor N/2 \rfloor$:

$$x = a \cdot 10^m + b \qquad y = c \cdot 10^m + d$$

$$x \cdot y = ac \cdot 10^{2m} + (ad + bc) \cdot 10^m + bd$$

Así escrito hacen falta **cuatro** productos: $ac$, $ad$, $bc$ y $bd$. El truco de Karatsuba es obtener
$ad + bc$ con **una sola** multiplicación, reutilizando $ac$ y $bd$:

$$(a + b)(c + d) = ac + ad + bc + bd \quad\Longrightarrow\quad ad + bc = (a + b)(c + d) - ac - bd$$

Son **3 multiplicaciones de la mitad del tamaño en lugar de 4**. Las sumas, restas y potencias de 10
cuestan poco: multiplicar por $10^k$ es solo agregar $k$ ceros a la derecha.

### Las tres fases en el código

```python
def karatsuba(x, y, contador, nivel=1):
    if x == 0 or y == 0:                  # por cero no hace falta multiplicar
        return 0
    if x < 10 and y < 10:                 # caso base: un digito por un digito
        contador.multiplicaciones += 1
        return x * y

    # 1. Division: cada numero en mitad alta y mitad baja (m digitos en la baja)
    m = max(num_digitos(x), num_digitos(y)) // 2
    a, b = partir(x, m)
    c, d = partir(y, m)

    # 2. Conquista: tres subproblemas mas pequenos, resueltos con la misma funcion
    ac = karatsuba(a, c, contador, nivel + 1)
    bd = karatsuba(b, d, contador, nivel + 1)
    suma = karatsuba(a + b, c + d, contador, nivel + 1)
    ad_mas_bc = suma - ac - bd

    # 3. Combinacion: x * y = ac * 10^(2m) + (ad + bc) * 10^m + bd
    return desplazar(ac, 2 * m) + desplazar(ad_mas_bc, m) + bd
```

(Versión resumida: el archivo real además imprime la traza.)

`partir` y `desplazar` ([`digitos.py`](./src/dyv/digitos.py)) trabajan sobre la **cadena de dígitos**:
cortan el número en dos o le pegan ceros, sin usar `*`, `//` ni `%`. Así el único `*` de todo el
algoritmo queda en el caso base, y contar multiplicaciones es contar exactamente esos productos de un
dígito por un dígito.

### Traza: 1234 × 5678

`uv run main.py` imprime primero cómo se resuelve un ejemplo pequeño. Cada sangría es un nivel más de
recursión; la línea con `->` es la **división**, las de abajo la **conquista**, y la línea con `=` la
**combinación**:

```
1234 x 5678  ->  a=12, b=34, c=56, d=78  (m=2)
    12 x 56  ->  a=1, b=2, c=5, d=6  (m=1)
        1 x 5 = 5   (caso base)
        2 x 6 = 12   (caso base)
        3 x 11  ->  a=0, b=3, c=1, d=1  (m=1)
            0 x 1 = 0   (por cero, sin multiplicar)
            3 x 1 = 3   (caso base)
            3 x 2 = 6   (caso base)
        = 0*10^2 + 3*10^1 + 3 = 33
    = 5*10^2 + 16*10^1 + 12 = 672
    34 x 78  ->  a=3, b=4, c=7, d=8  (m=1)
        ...
    = 21*10^2 + 52*10^1 + 32 = 2652
    46 x 134  ->  a=4, b=6, c=13, d=4  (m=1)
        ...
    = 52*10^2 + 94*10^1 + 24 = 6164
= 672*10^4 + 2840*10^2 + 2652 = 7006652
```

En el primer nivel: $ac = 12 \cdot 56 = 672$, $bd = 34 \cdot 78 = 2652$ y
$(a+b)(c+d) = 46 \cdot 134 = 6164$, de donde $ad + bc = 6164 - 672 - 2652 = 2840$. El resultado,
$7\,006\,652$, sale con **13** multiplicaciones de un dígito; la escolar necesita $4 \cdot 4 = 16$.

## 3. T(N): tiempo de ejecución

Cada llamada hace 3 llamadas de tamaño $N/2$ y trabajo lineal (partir, sumar, restar, agregar ceros):

$$T(N) = 3\,T(N/2) + O(N)$$

Por el **teorema maestro** ($a = 3$, $b = 2$, $f(N) = O(N)$): como $N^{\log_2 3} \approx N^{1.585}$ crece
más rápido que $f(N)$, domina el número de subproblemas y

$$T(N) = \Theta\!\left(N^{\log_2 3}\right) \approx \Theta\!\left(N^{1.585}\right)$$

| Método | Recurrencia | T(N) |
|---|---|---|
| Escolar | — (dos ciclos anidados de $N$) | $\Theta(N^2)$ |
| DyV 4 llamadas | $T(N) = 4\,T(N/2) + O(N)$ | $\Theta(N^{\log_2 4}) = \Theta(N^2)$ |
| **Karatsuba** | $T(N) = 3\,T(N/2) + O(N)$ | $\Theta(N^{1.585})$ |

La fila de en medio es la importante: **dividir por sí solo no ahorra nada**. Con 4 subproblemas el
árbol de recursión termina haciendo los mismos $N^2$ productos que la escolar. La mejora viene
exclusivamente de bajar a 3 subproblemas.

T(N) se mide de dos formas ([`medicion.py`](./src/dyv/medicion.py)):

- **Multiplicaciones de un dígito**: no dependen de la computadora; son la medida directa de lo que
  pide la actividad.
- **Tiempo**: promedio de 100 ejecuciones con `time.perf_counter`, en microsegundos.

## 4. S(N): espacio

- **Pila de recursión:** cada nivel parte el número a la mitad, así que la profundidad máxima es
  $O(\log N)$. Se mide en la columna **Profundidad**.
- **Memoria auxiliar:** en el nivel $k$ hay vivos números de $N/2^k$ dígitos. La suma
  $N + N/2 + N/4 + \dots \le 2N$, así que $S(N) = O(N)$. Se mide en la columna **Memoria (KB)**: el
  pico de memoria reservada, con `tracemalloc`.

`tracemalloc` hace más lento el código que mide, así que tiempo y memoria salen de ejecuciones
distintas (igual que en la Actividad 13).

## 5. Resultados

Salida de `uv run main.py` (los números `x` y `y` completos se imprimen en la consola).

**N = 20** · referencia: $N^2 = 400$, $N^{\log_2 3} \approx 115$

```
x = 95815028503973011889
y = 51448639579792535354

Metodo          Correcto  Mult. 1 dig  Llamadas  Profundidad  Tiempo (us)  Memoria (KB)
Python  *             si            -         -            -         0.19          0.05
Escolar               si          400         1            1        83.20          3.20
DyV 4 llamadas        si          340       709            6       362.00          0.67
Karatsuba             si          182       361            7       251.99          0.79
```

**N = 50** · referencia: $N^2 = 2\,500$, $N^{\log_2 3} \approx 493$

```
Metodo          Correcto  Mult. 1 dig  Llamadas  Profundidad  Tiempo (us)  Memoria (KB)
Python  *             si            -         -            -         0.21          0.07
Escolar               si         2500         1            1       384.93          7.06
DyV 4 llamadas        si         2024      4333            7      1533.04          1.10
Karatsuba             si          781      1504            9       798.56          1.17
```

**N = 100** · referencia: $N^2 = 10\,000$, $N^{\log_2 3} \approx 1\,479$

```
Metodo          Correcto  Mult. 1 dig  Llamadas  Profundidad  Tiempo (us)  Memoria (KB)
Python  *             si            -         -            -         0.26          0.12
Escolar               si        10000         1            1      1128.09         13.57
DyV 4 llamadas        si         7743     16153            8      6881.45          1.51
Karatsuba             si         2221      4414           10      2708.43          1.71
```

Resumen de Karatsuba frente a la escolar:

| N | Escolar | Karatsuba | Ahorro de multiplicaciones |
|---|---|---|---|
| 20 | 400 | 182 | 2.2 veces menos |
| 50 | 2 500 | 781 | 3.2 veces menos |
| 100 | 10 000 | 2 221 | 4.5 veces menos |

### Tamaños más grandes

`uv run main.py 200 500 1000 2000`, solo Karatsuba y la escolar:

| N | Mult. escolar | Mult. Karatsuba | Tiempo escolar (µs) | Tiempo Karatsuba (µs) | Profundidad |
|---|---|---|---|---|---|
| 200 | 40 000 | 6 762 | 4 373 | 7 182 | 11 |
| 500 | 250 000 | 28 610 | 27 724 | 28 013 | 12 |
| 1 000 | 1 000 000 | 85 629 | 107 369 | 87 289 | 13 |
| 2 000 | 4 000 000 | 255 987 | 456 226 | 261 628 | 14 |

## 6. Análisis

**Las multiplicaciones crecen como predice T(N).** Al duplicar $N$, la escolar multiplica por $4$
($= 2^2$) sus productos y Karatsuba por $\approx 3$ ($= 2^{1.585}$): de 1 000 a 2 000 dígitos pasa de
85 629 a 255 987, un factor de 2.99. Los conteos de Karatsuba quedan alrededor de 1.5 veces por encima
de $N^{1.585}$ porque $N$ no es potencia de 2 y porque $a + b$ y $c + d$ a veces tienen un dígito más
(acarreo), pero el ritmo de crecimiento es el de la teoría.

**Menos multiplicaciones no es lo mismo que menos tiempo, al menos al principio.** Con 20, 50 y 100
dígitos Karatsuba hace entre 2 y 4.5 veces menos multiplicaciones, pero tarda **más** que la escolar.
Cada llamada recursiva cuesta mucho más que una vuelta de ciclo: crear el marco de la función, convertir
números a cadena para partirlos y volver a entero. Con pocos dígitos ese costo fijo pesa más que las
multiplicaciones ahorradas; **alrededor de 500 dígitos se igualan** y desde ahí Karatsuba gana cada
vez por más (1.7 veces más rápida con 2 000 dígitos). Por eso las implementaciones reales cambian a la
escolar por debajo de cierto tamaño en lugar de bajar hasta un dígito.

**DyV 4 llamadas** hace menos de $N^2$ multiplicaciones solo porque se salta los productos por cero:
termina multiplicando cada par de dígitos distintos de cero exactamente una vez. Es la más lenta de
todas: hace el mismo trabajo que la escolar y además paga el costo de la recursión.

**S(N).** La profundidad crece de uno en uno cada vez que $N$ se duplica ($\approx \log_2 N + 3$; las
sumas con acarreo agregan algún nivel extra). La memoria de Karatsuba crece de forma lineal: casi se
duplica de 1 000 a 2 000 dígitos (7.00 → 13.47 KB). La escolar ocupa más porque guarda cada dígito como
un entero de Python dentro de una lista.

**Python `*`** es miles de veces más rápido que todo lo anterior porque está escrito en C y no trabaja
en base 10 sino en base $2^{30}$: un número de 100 dígitos son solo 11 "dígitos" internos. CPython usa
la multiplicación escolar para números chicos y **cambia a Karatsuba** a partir de 70 dígitos internos
(unos 630 dígitos decimales); es la misma idea de este proyecto, con el umbral que se mencionó arriba.

## 7. Pruebas de funcionamiento

`main.py` hace la prueba en cada medición: calcula `x * y` con el operador `*` de Python (la
multiplicación sin Karatsuba) y compara contra él el resultado de cada método. La columna **Correcto**
de las tablas de la sección 5 es esa comparación: `si` cuando el producto coincide dígito por dígito,
`NO` si no. Con 20, 50 y 100 dígitos (y con 200, 500, 1 000 y 2 000), los tres métodos dan `si`.

La traza de la sección 2 también se comprueba: termina en $7\,006\,652$, que es $1234 \times 5678$.

## Estructura del proyecto

```
CL_actividad_14/
├── main.py                 # traza de ejemplo y mediciones de T(N) y S(N)
├── src/dyv/
│   ├── digitos.py          #   partir, desplazar (x 10^k) y generar numeros de N digitos
│   ├── medicion.py         #   contador, tiempo y memoria
│   ├── escolar.py          #   multiplicacion de primaria
│   ├── clasico.py          #   divide y venceras con 4 llamadas
│   └── karatsuba.py        #   divide y venceras con 3 llamadas (Karatsuba)
├── pyproject.toml          # proyecto de uv, sin dependencias externas
└── .python-version         # Python 3.14
```
