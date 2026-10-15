# Actividad 13 — Algoritmos P, NP y con heurística

**Materia:** Lenguajes de Computación · Otoño 2026 · Angel Rugerio Jiménez (201720)

Este documento explica los tres algoritmos de la actividad, el generador de grafos y las pruebas con
grafos de 5, 10 y 15 nodos. Cómo correr el servicio está en el [README](./README.md).

## 1. Clases P y NP

- **Clase P:** problemas que una Máquina de Turing **determinista** resuelve en tiempo polinómico,
  $O(n^k)$. Son los tratables: el tiempo crece de forma sostenible con la entrada.
- **Clase NP:** *no* significa "no polinómico", sino **polinómico no determinista**. Son los problemas
  cuya solución, si alguien la da, se puede **verificar** en tiempo polinómico, aunque encontrarla
  pueda requerir una búsqueda exponencial.

| Problema | Clase | Por qué |
|---|---|---|
| Camino más corto entre dos nodos | **P** | Dijkstra lo resuelve en tiempo polinómico |
| Agente viajero (recorrido más barato) | **NP-difícil** | No se conoce ningún algoritmo polinómico; el exacto prueba ordenes que crecen como $(n-1)!$ |

> El agente viajero aparece en clase como ejemplo de NP. Más precisamente, su versión de decisión
> ("¿existe un recorrido de costo $\le K$?") es NP-completa: dado un recorrido, verificarlo es solo
> sumar $n$ pesos. La versión que se pide aquí (encontrar el **más barato**) es NP-difícil.

Por eso la actividad incluye un tercer algoritmo: una **heurística voraz** que resuelve el agente
viajero en tiempo polinómico a cambio de no garantizar el óptimo.

## 2. Qué regresa cada endpoint

Los tres algoritmos responden con el mismo esquema:

| Campo | Significado |
|---|---|
| `tiempo_ms` | Tiempo de ejecución del algoritmo, en milisegundos (varía un poco en cada ejecución) |
| `memoria_kb` | Pico de memoria reservada mientras corre el algoritmo, medido con `tracemalloc` |
| `nodos_recorridos` | Cuántos nodos recorrió el algoritmo (lo que significa en cada uno se explica abajo) |
| `costo` | Suma de los pesos del camino o recorrido encontrado (`null` si no hay solución) |
| `ruta`, `solucion` | El camino encontrado y si se encontró |

`tracemalloc` hace más lento al código que mide, así que el algoritmo se ejecuta dos veces: una para
el tiempo y otra para la memoria ([`medicion.py`](./src/pnp/medicion.py)).

## 3. Generador de grafos sintéticos — `POST /grafos/sintetico`

[`sintetico.py`](./src/pnp/sintetico.py) genera un grafo **no dirigido y ponderado** con pesos enteros
al azar:

1. Acomoda los nodos en un orden aleatorio y los une en un ciclo. Así el grafo siempre es conexo y el
   agente viajero siempre tiene al menos un recorrido válido.
2. Cada par de nodos que no quedó unido recibe una arista con probabilidad `densidad`. Con
   `densidad = 1` (por defecto), el grafo es **completo**.

| Parámetro | Por defecto | |
|---|---|---|
| `nodos` | — | De 3 a 26 (A, B, C, …) |
| `densidad` | 1 | Probabilidad de cada arista extra |
| `peso_min`, `peso_max` | 1, 100 | Rango de los pesos |
| `semilla` | al azar | La misma semilla da siempre el mismo grafo |

La respuesta trae el grafo en el mismo formato de lista de adyacencia de la Actividad 12
(`{"A": [["B", 89], ...]}`), así que se puede mandar tal cual a cualquier endpoint de grafos.

## 4. Dijkstra (clase P) — `POST /grafos/dijkstra`

Encuentra el camino de **menor costo** entre `origen` y `destino`
([`dijkstra.py`](./src/pnp/dijkstra.py)).

1. La distancia del origen es 0; la de los demás, infinito.
2. Se saca de la lista abierta (un montículo, `heapq`) el nodo con **menor distancia acumulada**.
3. Para cada vecino, si llegar por ese nodo es más barato que lo conocido, se actualizan su distancia y
   su padre.
4. Se repite hasta sacar el destino. Con pesos no negativos, cuando un nodo sale ya tiene su distancia
   mínima, así que el resultado es **siempre óptimo**.

Es A\* con $h(n) = 0$ (como se vio en la clase de heurística): no estima lo que falta, solo usa el
costo real.

- **Complejidad:** $O((V + E) \log V)$, polinómica.
- **`nodos_recorridos`:** nodos que salieron de la lista abierta (los que se expandieron).

## 5. Agente viajero exacto (NP-difícil) — `POST /grafos/tsp`

Busca el recorrido más barato que sale del `origen`, pasa **una sola vez** por cada nodo y regresa al
origen ([`tsp_exacto.py`](./src/pnp/tsp_exacto.py)).

Prueba los ordenes posibles con **backtracking** (búsqueda en profundidad): desde el nodo actual
intenta cada vecino no visitado, sigue el recorrido y, al regresar, deshace la elección para probar el
siguiente. Cuando el recorrido tiene los $n$ nodos, suma la arista de regreso al origen y lo compara
con el mejor encontrado.

**Poda:** si un recorrido a medias ya cuesta lo mismo o más que el mejor recorrido completo, se
abandona esa rama. La respuesta sigue siendo la óptima; solo se evita terminar recorridos que no
pueden ganar.

- **Complejidad:** $O(n!)$. Hay $(n-1)!$ ordenes posibles; la poda recorta muchos, pero no cambia el
  peor caso.
- **`nodos_recorridos`:** nodos del **árbol de búsqueda** visitados, es decir, cuántos recorridos
  parciales se construyeron.
- **Límite:** solo acepta grafos de hasta 15 nodos. Con 16 responde **422**, porque con 20 nodos
  tardaría horas.

## 6. Agente viajero con heurística voraz — `POST /grafos/tsp-voraz`

Heurística del **vecino más cercano** ([`tsp_voraz.py`](./src/pnp/tsp_voraz.py)), el mismo método
greedy de clase:

1. **Criterio de selección:** desde el nodo actual, ir al vecino **no visitado** con la arista más
   barata (en empate, orden alfabético).
2. La elección se acepta y **no se reconsidera**.
3. Al visitar todos los nodos, regresar al origen.

- **Complejidad:** $O(V + E)$; en un grafo completo, $O(V^2)$. Polinómica.
- **`nodos_recorridos`:** nodos que forman el recorrido (siempre $n$ si encuentra solución).
- **No garantiza el óptimo.** Y en un grafo que no es completo se puede **atorar**: llegar a un nodo
  sin vecinos libres, o terminar en uno sin arista de regreso. En ese caso responde
  `"solucion": false` y en `ruta` muestra hasta dónde llegó.

## 7. Pruebas

Las tres pruebas usan el generador con sus valores por defecto (grafo completo, pesos de 1 a 100) y
están precargadas en `/docs` (menú **Examples** de cada endpoint).

| Prueba | Solicitud a `/grafos/sintetico` | Aristas | Dijkstra | Agente viajero |
|---|---|---|---|---|
| 1 | `{"nodos": 5, "semilla": 5}` | 10 | A → C | desde A |
| 2 | `{"nodos": 10, "semilla": 10}` | 45 | A → D | desde A |
| 3 | `{"nodos": 15, "semilla": 15}` | 105 | A → H | desde A |

Los destinos de Dijkstra se eligieron para que el camino más corto **no** sea la arista directa.

### Prueba 1 — 5 nodos

Pesos del grafo (no dirigido, así que la matriz es simétrica):

| | A | B | C | D | E |
|---|---|---|---|---|---|
| **A** | — | 89 | 100 | 84 | 4 |
| **B** | 89 | — | 21 | 95 | 61 |
| **C** | 100 | 21 | — | 84 | 68 |
| **D** | 84 | 95 | 84 | — | 49 |
| **E** | 4 | 61 | 68 | 49 | — |

| Algoritmo | Ruta | Costo | Nodos recorridos | Tiempo (ms) | Memoria (KB) |
|---|---|---|---|---|---|
| Dijkstra (A → C) | A → E → C | **72** | 5 | 0.020 | 0.85 |
| TSP exacto | A → B → C → D → E → A | **247** | 63 | 0.024 | 1.82 |
| TSP voraz | A → E → D → C → B → A | **247** | 5 | 0.015 | 1.14 |

- **Dijkstra:** la arista directa A → C cuesta 100, pero ir por E cuesta $4 + 68 = 72$.
- **Voraz:** sale por la arista más barata (A → E, 4) y desde ahí siempre elige la menor disponible.
  Encuentra el mismo costo que el exacto: es el mismo ciclo recorrido al revés.

### Prueba 2 — 10 nodos

| Algoritmo | Ruta | Costo | Nodos recorridos | Tiempo (ms) | Memoria (KB) |
|---|---|---|---|---|---|
| Dijkstra (A → D) | A → B → H → D | **32** | 8 | 0.013 | 1.32 |
| TSP exacto | A → B → F → E → D → H → I → G → C → J → A | **217** | 74,224 | 9.93 | 4.60 |
| TSP voraz | A → B → I → H → D → C → G → F → E → J → A | 282 | 10 | 0.015 | 3.78 |

- **Dijkstra:** la arista directa A → D cuesta 49; por B y H, 32.
- **Voraz:** cuesta **30 % más** que el óptimo (282 contra 217). Las primeras elecciones fueron
  baratas, pero al final le quedaron solo aristas caras para cerrar el recorrido.

### Prueba 3 — 15 nodos

| Algoritmo | Ruta | Costo | Nodos recorridos | Tiempo (ms) | Memoria (KB) |
|---|---|---|---|---|---|
| Dijkstra (A → H) | A → L → F → N → D → H | **22** | 11 | 0.021 | 1.85 |
| TSP exacto | A → B → D → I → C → G → E → J → H → M → K → N → F → L → O → A | **192** | 5,180,432 | 598 | 11.39 |
| TSP voraz | A → L → F → N → D → H → J → E → G → C → K → M → O → B → I → A | 261 | 15 | 0.052 | 8.23 |

- **Dijkstra:** el camino más corto tiene 5 aristas (22), contra 83 de la arista directa.
- **Voraz:** cuesta **36 % más** que el óptimo (261 contra 192), pero tardó unas 10,000 veces menos.

### Comparación

| Nodos | Dijkstra: nodos recorridos | TSP exacto: nodos recorridos | $(n-1)!$ ordenes | TSP exacto: tiempo | TSP voraz: costo / óptimo |
|---|---|---|---|---|---|
| 5 | 5 | 63 | 24 | 0.024 ms | 247 / 247 (igual) |
| 10 | 8 | 74,224 | 362,880 | 9.9 ms | 282 / 217 (+30 %) |
| 15 | 11 | 5,180,432 | 87,178,291,200 | 598 ms | 261 / 192 (+36 %) |

- **P contra NP en números.** De 5 a 15 nodos, Dijkstra pasó de 5 a 11 nodos recorridos y su tiempo
  apenas se movió. El agente viajero exacto pasó de 63 a más de 5 millones de nodos y de 0.02 ms a
  casi 600 ms: unas 25,000 veces más tiempo por triplicar los nodos. Con 20 nodos ($19! \approx 1.2
  \times 10^{17}$ ordenes) ya no es práctico.
- **La poda ayuda, pero no cambia la clase.** Sin poda, el árbol de 15 nodos tendría unos
  $2.4 \times 10^{11}$ nodos; con poda se visitaron 5 millones. Sigue siendo exponencial: cada nodo
  extra multiplica el trabajo.
- **La heurística cambia exactitud por tiempo.** El voraz recorre solo $n$ nodos y responde en
  microsegundos, pero no garantiza el óptimo: lo encontró con 5 nodos y pagó 30–36 % más con 10 y 15.
  Es la misma lección del ejemplo de las casetas de clase: la decisión local barata no ve lo que
  cuesta más adelante.
- **La memoria se queda chica en los tres.** El exacto solo guarda el recorrido actual y el mejor
  ($O(n)$); lo que explota es el **tiempo**, no el espacio.
- **Verificación.** Durante el desarrollo, los resultados se compararon contra dos algoritmos
  independientes que no forman parte del repositorio: Floyd-Warshall para Dijkstra (todos los
  destinos de los tres grafos) y programación dinámica de Held-Karp para el agente viajero exacto.
  Coincidieron en todos los casos.

### Observación: grafo no completo

Con `{"nodos": 10, "semilla": 10, "densidad": 0.5}` (27 aristas), el exacto encuentra el recorrido
óptimo (costo 230), pero el voraz se **atora**: llega a I después de visitar los 10 nodos, y I no tiene
arista de regreso a A. Responde `"solucion": false`. Una heurística puede, incluso, no encontrar
solución donde sí la hay.
