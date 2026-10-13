# Actividad 12 — Búsqueda informada en grafos: Greedy Best-First Search y A*

**Materia:** Lenguajes de Computación · Otoño 2026

| Nombre completo | No. de cuenta |
|---|---|
| Angel Rugerio Jiménez | 201720 |

---

## Descripción

Backend en **FastAPI** que busca una ruta entre dos nodos de un grafo **dirigido y ponderado** con
dos algoritmos de búsqueda informada, implementados a mano (sin librerías de grafos):

| Endpoint | Método | Módulo | Criterio para elegir el siguiente nodo |
|---|---|---|---|
| `/search/greedy` | POST | [`greedy_search.py`](./src/busqueda/greedy_search.py) | Menor $h(n)$ — solo la heurística |
| `/search/star` | POST | [`star_search.py`](./src/busqueda/star_search.py) | Menor $f(n) = g(n) + h(n)$ — costo real + heurística |
| `/` | GET | [`main.py`](./main.py) | Información del servicio |

Los dos endpoints reciben el mismo esquema de entrada y regresan el mismo esquema de salida, así que
cualquier diferencia en los resultados se debe solo al algoritmo. La actividad contrasta tres cosas:
**cuántos nodos explora** cada uno, **si la ruta que regresa es la de menor costo** y **cuánto
cuesta** en tiempo $T(n)$ y espacio $S(n)$.

## Estructura del proyecto

```
CL_actividad_12/
├── main.py                  # punto de entrada: crea la app y conecta los endpoints
├── src/busqueda/
│   ├── esquemas.py          # Pydantic: SolicitudBusqueda (entrada), ResultadoBusqueda (salida)
│   ├── heuristica.py        # h(n): por saltos (BFS hacia atrás) o euclidiana
│   ├── greedy_search.py     # Greedy Best-First Search
│   ├── star_search.py       # A*
│   ├── utilidades.py        # reconstruir la ruta y sumar su costo
│   └── rutas.py             # POST /search/greedy, POST /search/star
├── grafos/                  # los 3 grafos del archivo de la actividad, en JSON
│   ├── grafo_10.json
│   ├── grafo_25.json
│   └── grafo_50.json
├── resultados/              # respuesta de la API en cada prueba + resumen.md
├── generar_resultados.py    # corre las 9 pruebas y regenera resultados/
├── verificar_optimo.py      # compara A* contra Dijkstra en todos los pares de nodos
├── Material/                # archivos del profesor (imágenes y .txt de los grafos)
├── pyproject.toml           # dependencias y configuración del proyecto (uv)
├── uv.lock                  # versiones exactas de las dependencias
└── .python-version          # versión de Python que usa uv (3.14)
```

Los grafos de `grafos/` se transcribieron del archivo `Material/Actividad 12 (Nodos).txt` sin
cambiar ninguna arista. El `.txt` no es JSON válido tal cual (al grafo de 10 le sobra una coma y al
de 50 le falta la llave de cierre), por eso se guardaron aparte, ya corregidos. Se comprobó que
cada grafo tiene el número de nodos de su nombre y que cada vecino es también un nodo:

| Grafo | Nodos $V$ | Aristas $E$ | Peso mínimo |
|---|---|---|---|
| `grafo_10` | 10 | 17 | 8 |
| `grafo_25` | 25 | 45 | 5 |
| `grafo_50` | 50 | 56 | 12 |

## Cómo correr el servicio

```bash
uv sync                  # instala las dependencias de uv.lock
uv run fastapi dev       # servidor en http://127.0.0.1:8000
# o bien
uv run main.py
```

La documentación interactiva queda en `http://127.0.0.1:8000/docs`.

```bash
uv run python generar_resultados.py   # las 9 pruebas de la actividad -> resultados/
uv run python verificar_optimo.py     # A* contra Dijkstra en todos los pares
```

# Esquemas de entrada y salida (Pydantic)

## Entrada — `SolicitudBusqueda`

```json
{
  "grafo": {
    "A": [["B", 15], ["C", 22], ["D", 10]],
    "B": [["E", 35], ["F", 18]],
    "...": "...",
    "J": []
  },
  "origen": "A",
  "destino": "J",
  "limite_nodos": 8,
  "coordenadas": null
}
```

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `grafo` | `{nodo: [[vecino, peso], ...]}` | Sí | Lista de adyacencia con pesos, el mismo formato del archivo de la actividad |
| `origen` | `str` | Sí | Nodo de inicio |
| `destino` | `str` | Sí | Nodo meta |
| `limite_nodos` | `int ≥ 1` | No | Máximo de nodos a visitar. **Por defecto, 80 % de los nodos** ($\lceil 0.8\,V \rceil$): 8, 20 y 40 en los tres grafos |
| `coordenadas` | `{nodo: [x, y]}` | No | Si se manda, $h(n)$ es la distancia euclidiana (ver [Heurística](#la-heurística-hn)) |

Validaciones (si alguna falla, la API responde **422** con el motivo):

- El grafo tiene al menos un nodo.
- Cada vecino de una arista es también un nodo del grafo.
- Ningún peso es negativo (A\* solo garantiza el óptimo con costos $\ge 0$).
- `origen` y `destino` son nodos del grafo.
- `limite_nodos` no es mayor que el número de nodos.
- Si se mandan `coordenadas`, cubren todos los nodos.

```json
{"detail": [{"msg": "Value error, El destino 'Z' no es un nodo del grafo.", "...": "..."}]}
```

## Salida — `ResultadoBusqueda`

Respuesta real de `POST /search/star` para A → J en el grafo de 10 nodos
([`resultados/grafo_10_A-J_star.json`](./resultados/grafo_10_A-J_star.json)):

```json
{
  "algoritmo": "A*",
  "origen": "A",
  "destino": "J",
  "heuristica": "saltos al destino x peso minimo",
  "limite_nodos": 8,
  "nodos_visitados": 8,
  "solucion": true,
  "ruta": ["A", "B", "F", "I", "J"],
  "costo": 56.0,
  "orden_visita": ["A", "D", "C", "B", "G", "F", "I", "J"],
  "T(n)": {"cota": "O((V + E) log V)", "V": 10, "E": 17, "operaciones": 23, "tiempo_ms": 0.0346},
  "S(n)": {"cota": "O(V + E)", "max_nodos_en_memoria": 12}
}
```

| Campo | Lo que pide la actividad | Significado |
|---|---|---|
| `nodos_visitados` | No. total de nodos visitados | Nodos **expandidos** (sacados de la lista abierta para revisar sus vecinos). Es lo que se compara contra el límite |
| `solucion` | Solución (True/False) | `true` si se llegó al destino sin pasar el límite |
| `ruta` | Ruta de solución | Del origen al destino; `[]` si no hay solución |
| `T(n)` | T(n) | Cota asintótica + medición: `operaciones` (extracciones de la lista abierta + aristas revisadas) y `tiempo_ms` |
| `S(n)` | S(n) | Cota asintótica + medición: máximo de entradas en las listas abierta y cerrada al mismo tiempo |
| `costo`, `orden_visita`, `heuristica`, `limite_nodos` | — | Extra: para comparar los dos algoritmos y revisar el resultado a mano |

# La heurística h(n)

La instrucción pide una heurística "como la distancia euclidiana". La distancia euclidiana necesita
la **posición** $(x, y)$ de cada nodo, y el archivo de la actividad solo trae **aristas y pesos**:
las posiciones únicamente aparecen en las imágenes, y no corresponden a los pesos (no son un mapa a
escala). Por eso el servicio tiene dos heurísticas ([`heuristica.py`](./src/busqueda/heuristica.py)):

| Caso | Heurística | Cuándo se usa |
|---|---|---|
| La solicitud trae `coordenadas` | $h(n) = \sqrt{(x_n - x_d)^2 + (y_n - y_d)^2}$ | Grafos con posición real (un mapa) |
| La solicitud **no** trae `coordenadas` | $h(n) = \text{saltos}(n, d) \cdot w_{\min}$ | Los grafos de la actividad |

donde $d$ es el destino, $w_{\min}$ el peso más pequeño del grafo y $\text{saltos}(n, d)$ el menor
número de aristas para ir de $n$ a $d$. Los saltos se calculan con una **búsqueda en anchura (BFS)
sobre las aristas invertidas**, empezando en el destino — la BFS vista en clase, que encuentra el
camino con menos pasos ignorando los pesos. Un nodo sin ningún camino al destino recibe
$h(n) = \infty$: se puede explorar, pero siempre al final.

**Es admisible.** Un camino de $k$ aristas cuesta por lo menos $k \cdot w_{\min}$, y el mejor camino
de $n$ al destino tiene al menos $\text{saltos}(n, d)$ aristas, así que $h(n) \le h^*(n)$: nunca
sobreestima el costo real.

**Es consistente.** Para una arista $n \to m$ con costo $c(n, m)$, ir por $m$ da
$\text{saltos}(n, d) \le \text{saltos}(m, d) + 1$, entonces

$$h(n) \le h(m) + w_{\min} \le h(m) + c(n, m)$$

Esto le permite a A\* no reabrir nodos cerrados (ver [A\*](#búsqueda-a)) y garantiza que la ruta que
regresa es la de menor costo. Se comprobó empíricamente con
[`verificar_optimo.py`](./verificar_optimo.py) (sección [Verificación](#verificación-de-optimalidad)).

Tabla $h(n)$ del grafo de 10 nodos con destino J ($w_{\min} = 8$):

| Nodo | A | B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|---|---|
| saltos a J | 3 | 3 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 0 |
| $h(n)$ | 24 | 24 | 16 | 16 | 16 | 16 | 8 | 8 | 8 | 0 |

> **Sobre la euclidiana con coordenadas.** Es admisible solo si cada arista pesa al menos la distancia
> en línea recta entre sus extremos (como en el ejemplo de clase CDMX → SLP, donde los km por
> carretera nunca son menores que los km en línea recta). Si las coordenadas que se manden no
> cumplen eso, A\* puede regresar una ruta que no sea la óptima.

# Búsqueda voraz (Greedy Best-First Search)

Archivo: [`src/busqueda/greedy_search.py`](./src/busqueda/greedy_search.py)

**Criterio de selección:** de la lista abierta siempre se saca el nodo con **menor $h(n)$**, el que
parece estar más cerca del destino. El costo ya recorrido $g(n)$ no se toma en cuenta. Empates:

1. **Valor** — menor peso de la arista por la que se llegó al nodo.
2. **Orden** — orden alfabético del nombre del nodo.

```
abierta  <- [(h(origen), 0, origen)]          # cola de prioridad (heapq)
padre    <- {origen: None}
mientras abierta no esté vacía y visitados < límite:
    nodo <- sacar el de menor (h, peso, nombre)
    marcar nodo como visitado
    si nodo == destino: reconstruir la ruta con padre y terminar
    para cada (vecino, peso) de nodo:
        si vecino no se ha descubierto:
            padre[vecino] <- nodo
            meter (h(vecino), peso, vecino) en abierta
```

Igual que el método greedy de clase, **no se echa atrás**: un nodo se queda con el primer padre que
lo descubre, aunque después aparezca un camino más barato hacia él. La lista abierta sí le permite
salir de un callejón sin salida (por eso es *best-first* y no un greedy puro que solo mira a los
vecinos del nodo actual).

**Traza — grafo de 10 nodos, A → J:**

| Paso | Visitado | Vecinos nuevos $(h,\ \text{peso})$ | Lista abierta |
|---|---|---|---|
| 1 | A ($h = 24$) | B (24, 15), C (16, 22), D (16, 10) | D, C, B |
| 2 | D ($h = 16$) — empata con C, gana por peso 10 < 22 | F (16, 28), G (8, 30) | G, C, F, B |
| 3 | G ($h = 8$) | I (8, 10), J (0, 50) | J, I, C, F, B |
| 4 | J ($h = 0$) | **Meta** | — |

Ruta **A → D → G → J**, costo $10 + 30 + 50 = 90$, con 4 nodos visitados. Greedy eligió G → J
(50) porque J tiene $h = 0$, sin ver que G → I → J cuesta $10 + 8 = 18$. Es la misma lección que el
escenario 2 de las casetas Puebla → Veracruz: la información que importa estaba más adelante.

# Búsqueda A*

Archivo: [`src/busqueda/star_search.py`](./src/busqueda/star_search.py)

**Función de valor:** $f(n) = g(n) + h(n)$, con $g(n)$ el costo real acumulado desde el origen
(suma de los pesos conocidos) y $h(n)$ la heurística. Siempre se expande el nodo con menor $f(n)$;
en empate, el de menor $h(n)$, y después el orden alfabético.

```
g        <- {origen: 0}
abierta  <- [(h(origen), h(origen), origen)]   # (f, h, nodo)
mientras abierta no esté vacía y visitados < límite:
    nodo <- sacar el de menor (f, h, nombre)
    si nodo ya está cerrado: ignorar (entrada vieja) y seguir
    cerrar nodo y marcarlo como visitado
    si nodo == destino: reconstruir la ruta y terminar
    para cada (vecino, peso) de nodo que no esté cerrado:
        nuevo_g <- g[nodo] + peso
        si nuevo_g < g[vecino]:                  # se encontró un camino más barato
            g[vecino] <- nuevo_g;  padre[vecino] <- nodo
            meter (nuevo_g + h(vecino), h(vecino), vecino) en abierta
```

A diferencia de greedy, A\* **sí corrige** el padre de un nodo cuando encuentra un camino más barato.
La entrada vieja se queda en el heap y se descarta cuando sale (*lazy deletion*). Como la heurística
es consistente, un nodo cerrado ya tiene su $g$ mínimo y no hace falta reabrirlo.

**Traza — grafo de 10 nodos, A → J** (mismo formato que el ejemplo de clase CDMX → SLP):

| Iteración | Nodo expandido | Cálculos | Lista abierta (por $f$) |
|---|---|---|---|
| 1 | A ($f = 24$) | $f(B) = 15 + 24 = 39$; $f(C) = 22 + 16 = 38$; $f(D) = 10 + 16 = 26$ | D(26), C(38), B(39) |
| 2 | D ($f = 26$) | $f(F) = 38 + 16 = 54$; $f(G) = 40 + 8 = 48$ | C(38), B(39), G(48), F(54) |
| 3 | C ($f = 38$) | $f(E) = 42 + 16 = 58$; G por C: $g = 67 \ge 40$, no mejora | B(39), G(48), F(54), E(58) |
| 4 | B ($f = 39$) | E por B: $g = 50 \ge 42$, no mejora; F por B: $g = 33 < 38$, **mejora** → $f(F) = 49$ | G(48), F(49), E(58) |
| 5 | G ($f = 48$) | $f(I) = 50 + 8 = 58$; $f(J) = 90 + 0 = 90$ | F(49), E(58), I(58), J(90) |
| 6 | F ($f = 49$) | $f(H) = 73 + 8 = 81$; I por F: $g = 48 < 50$, **mejora** → $f(I) = 56$ | I(56), E(58), H(81), J(90) |
| 7 | I ($f = 56$) | J por I: $g = 56 < 90$, **mejora** → $f(J) = 56$ | J(56), E(58), H(81) |
| 8 | J ($f = 56$) | **Meta** | — |

Ruta **A → B → F → I → J**, costo $15 + 18 + 15 + 8 = 56$ — la de menor costo. En la iteración 5,
A\* ya había generado J con $f = 90$ (la ruta de greedy), pero no la aceptó: todavía había nodos con
$f$ menor que podían llevar a algo más barato, y efectivamente lo hicieron.

# Complejidad: T(n) y S(n)

Con $V$ nodos y $E$ aristas, y la lista abierta como montículo binario (`heapq`, de la biblioteca
estándar de Python; es solo la estructura de datos, no implementa ningún algoritmo de búsqueda):

| | Greedy | A\* |
|---|---|---|
| $T(n)$ | $O((V + E) \log V)$ | $O((V + E) \log V)$ |
| $S(n)$ | $O(V)$ | $O(V + E)$ |

- **Tiempo.** Cada arista se revisa a lo más una vez (cuando su nodo de origen se expande) y cada
  inserción o extracción del heap cuesta $O(\log V)$. En greedy cada nodo entra al heap una sola vez;
  en A\* puede volver a entrar cada vez que mejora su $g$, a lo más una vez por arista entrante.
- **Espacio.** Greedy guarda a lo más $V$ entradas en el heap más el conjunto de cerrados y el
  diccionario de padres: $O(V)$. A\* además puede acumular entradas viejas en el heap (una por
  mejora): $O(V + E)$.
- **Heurística.** Calcular $h$ por saltos es una BFS: $O(V + E)$ en tiempo y $O(V)$ en espacio,
  antes de la búsqueda. No cambia el orden de ninguno de los dos.
- El peor caso exponencial que se mencionó en clase para A\* es para espacios de búsqueda
  implícitos (un árbol que se genera mientras se busca, sin lista de cerrados). Aquí el grafo es
  explícito y finito y cada nodo se cierra una sola vez, así que la cota es polinomial.

Lo medido en cada respuesta:

- `T(n).operaciones` = extracciones de la lista abierta + aristas revisadas. Es independiente de la
  máquina; es la que se usa para comparar.
- `T(n).tiempo_ms` = tiempo de reloj de la búsqueda (`time.perf_counter`). Son centésimas de
  milisegundo y **cambian entre una ejecución y otra**; solo sirven como orden de magnitud.
- `S(n).max_nodos_en_memoria` = máximo de entradas en la lista abierta + la lista cerrada al mismo
  tiempo.

# Pruebas y resultados

Tres pruebas por grafo, con distintos orígenes y destinos, cada una en los dos endpoints, con el
**límite por defecto** (80 % de los nodos). Las respuestas completas están en
[`resultados/`](./resultados/) y la tabla se regenera con `uv run python generar_resultados.py`
([`resultados/resumen.md`](./resultados/resumen.md)).

| Grafo | Origen → Destino | Algoritmo | Visitados / límite | Solución | Ruta | Costo | T(n): operaciones | T(n): ms | S(n): máx. en memoria |
|---|---|---|---|---|---|---|---|---|---|
| grafo_10 | A → J | Greedy | 4 / 8 | True | A → D → G → J | 90 | 11 | 0.0153 | 8 |
| grafo_10 | A → J | A* | 8 / 8 | True | A → B → F → I → J | **56** | 23 | 0.0346 | 12 |
| grafo_10 | B → H | Greedy | 3 / 8 | True | B → F → H | 58 | 7 | 0.0097 | 5 |
| grafo_10 | B → H | A* | 4 / 8 | True | B → E → H | **47** | 10 | 0.014 | 6 |
| grafo_10 | D → I | Greedy | 3 / 8 | True | D → F → I | 43 | 7 | 0.008 | 5 |
| grafo_10 | D → I | A* | 4 / 8 | True | D → G → I | **40** | 10 | 0.0156 | 7 |
| grafo_25 | A → Y | Greedy | 7 / 20 | True | A → D → I → M → R → U → Y | 142 | 20 | 0.0156 | 14 |
| grafo_25 | A → Y | A* | 18 / 20 | True | A → D → F → K → R → U → Y | **115** | 56 | 0.0316 | 23 |
| grafo_25 | D → W | Greedy | 6 / 20 | True | D → I → M → R → T → W | 207 | 17 | 0.0141 | 12 |
| grafo_25 | D → W | A* | 16 / 20 | True | D → F → K → R → T → W | **180** | 50 | 0.0316 | 21 |
| grafo_25 | B → V | Greedy | 5 / 20 | True | B → G → K → R → V | **82** | 16 | 0.0089 | 12 |
| grafo_25 | B → V | A* | 13 / 20 | True | B → G → K → R → V | **82** | 43 | 0.0177 | 19 |
| grafo_50 | A → AA | Greedy | 5 / 40 | True | A → B → I → S → AA | 156 | 12 | 0.0077 | 8 |
| grafo_50 | A → AA | A* | 8 / 40 | True | A → F → G → N → W → AA | **117** | 19 | 0.012 | 12 |
| grafo_50 | E → AX | Greedy | 7 / 40 | True | E → O → P → AC → AN → AU → AX | **187** | 14 | 0.0094 | 8 |
| grafo_50 | E → AX | A* | 9 / 40 | True | E → O → P → AC → AN → AU → AX | **187** | 18 | 0.0119 | 10 |
| grafo_50 | D → AM | Greedy | 9 / 40 | False | — | — | 18 | 0.0157 | 9 |
| grafo_50 | D → AM | A* | 9 / 40 | False | — | — | 18 | 0.0206 | 9 |

En **negritas**, el costo óptimo (confirmado con Dijkstra).

## Análisis

**Eficiencia de exploración.** Greedy visitó menos nodos que A\* en todas las pruebas con solución:
en total 40 contra 80, la mitad. La diferencia crece con el grafo: en A → Y (grafo de 25), greedy
llegó en 7 visitas y A\* necesitó 18 de las 20 permitidas. Greedy va directo hacia donde $h$ baja;
A\* tiene que confirmar que ninguna alternativa con $f$ menor lleva a algo más barato antes de
aceptar la meta.

**Optimalidad.** A\* regresó la ruta de menor costo en las 9 pruebas. Greedy la encontró solo en 2
de las 8 pruebas con solución (B → V y E → AX). En las otras pagó entre 7.5 % (D → I: 43 contra 40)
y 61 % más (A → J: 90 contra 56). Cuando las dos rutas coinciden, A\* igual visitó más nodos (13
contra 5 en B → V): ese trabajo extra es el precio de **garantizar** que la ruta es la óptima, no
solo de encontrarla.

**Complejidad medida.** Las operaciones y la memoria siguen el mismo patrón que los nodos
visitados: en las pruebas con solución, A\* hizo de 1.3 a 2.9 veces más operaciones y guardó más entradas a la vez (sus entradas
viejas en el heap se ven en S(n): 23 contra 14 en A → Y). Las dos cotas teóricas son del mismo orden;
lo que cambia es **cuánta parte del grafo** recorre cada uno antes de detenerse.

**La forma del grafo importa.** El grafo de 50 es casi un árbol (56 aristas para 50 nodos; casi
todos los nodos tienen una sola salida), así que hay pocas rutas alternativas y greedy casi nunca se
equivoca: en todos los pares del grafo, greedy pagó de más en 1 de 201 (ver
[Verificación](#verificación-de-optimalidad)). El grafo de 25 tiene muchas rutas que se cruzan, y
ahí es donde greedy falla más (41 de 217 pares).

**Sin solución.** En D → AM (grafo de 50) no existe camino: AM no se alcanza desde D. Los dos
algoritmos visitaron los 9 nodos alcanzables desde D, vaciaron la lista abierta sin pasar el límite
y respondieron `"solucion": false`.

**El límite de nodos también es un compromiso.** En A → J (grafo de 10), A\* encontró la meta
justo en la visita 8, que es el límite por defecto. Con `"limite_nodos": 7`, el mismo A\* responde
`"solucion": false`, mientras que greedy sigue encontrando su ruta (de costo 90) en 4 visitas:

| `limite_nodos` | Greedy | A\* |
|---|---|---|
| 8 (por defecto) | True — A → D → G → J (90), 4 visitas | True — A → B → F → I → J (56), 8 visitas |
| 7 | True — A → D → G → J (90), 4 visitas | **False** — 7 visitas, sin ruta |

Con un presupuesto de exploración apretado, greedy puede dar una respuesta aceptable donde A\* no
da ninguna. Es el compromiso de la actividad: greedy sacrifica optimalidad por rapidez; A\* paga en
exploración por la garantía del óptimo.

## Verificación de optimalidad

[`verificar_optimo.py`](./verificar_optimo.py) recorre **todos los pares (origen, destino)** de los
tres grafos y compara el costo de `/search/star` contra el de Dijkstra (que es A\* con $h = 0$ y
siempre es óptimo). Usa `limite_nodos` = total de nodos para que el límite no corte ninguna
búsqueda:

```
grafo_10: 34 pares con camino | A* optimo en 34/34 | greedy mas caro que el optimo en 10/34
grafo_25: 217 pares con camino | A* optimo en 217/217 | greedy mas caro que el optimo en 41/217
grafo_50: 201 pares con camino | A* optimo en 201/201 | greedy mas caro que el optimo en 1/201
```

A\* fue óptimo en los 452 pares con camino, que es lo que predice la consistencia de la heurística.

# Limitaciones

- **La heurística por saltos conoce la estructura del grafo.** Para calcularla se recorre el grafo
  completo hacia atrás desde el destino (BFS, $O(V + E)$) antes de buscar. Es lo que hace un GPS que
  ya tiene el mapa, pero significa que greedy recibe más información que una heurística puramente
  geométrica: un nodo con $h = \infty$ (sin camino al destino) queda al final de la lista abierta.
- **La heurística euclidiana depende de las coordenadas que se manden.** El servicio no comprueba
  que sean admisibles; si una arista pesa menos que la distancia en línea recta entre sus extremos,
  A\* puede no regresar el óptimo.
- **`tiempo_ms` no es reproducible.** Mide microsegundos y varía entre ejecuciones; para comparar
  algoritmos se usa `operaciones`.
- **Grafos dirigidos.** Una arista `["B", 15]` en la lista de `A` va solo de A a B. Para un grafo no
  dirigido hay que escribir la arista en las dos listas.
