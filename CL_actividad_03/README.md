# Actividad 3 – Cadenas y Lenguajes con FastAPI

**Estudiante:** Angel Rugerio Jiménez
**No. de cuenta:** 201720
**Actividad:** Actividad 3 – Operaciones de cadenas y lenguajes a través de un servicio web

## Descripción

Servicio web hecho con [FastAPI](https://fastapi.tiangolo.com/) (`main.py`) que expone un
endpoint por cada operación de cadenas y de lenguajes vista en clase. El desarrollo completo,
documentado paso a paso y con las llamadas reales a los endpoints, está en
[`Actividad_3.ipynb`](./Actividad_3.ipynb).

## Endpoints

### Cadenas

| Endpoint | Método | Descripción |
|---|---|---|
| `/Cadenas/concatenar/{x}/{y}` | GET | Concatena `x` y `y` |
| `/Cadenas/unir/{x}/{y}` | GET | Une `x` y `y` en un conjunto `{x, y}` |
| `/Cadenas/potencia/{x}/{n}` | GET | Repite `x` (`x` * `n`) |

### Lenguajes

Todos reciben en el cuerpo un objeto `Lenguaje` con `L`, `M` (listas de cadenas), `sigma`
(alfabeto) y `k` (según el endpoint), según aplique.

| Endpoint | Método | Descripción |
|---|---|---|
| `/lenguajes/union` | POST | $L \cup M$ |
| `/lenguajes/interseccion` | POST | $L \cap M$ |
| `/lenguajes/diferencia` | POST | $L - M$ |
| `/lenguajes/concatenar` | POST | $L \cdot M = \{xy : x \in L, y \in M\}$ |
| `/lenguajes/complemento` | POST | $\Sigma^{\le k} - L$ |
| `/lenguajes/kleene` | POST | Clausura de Kleene de $L$, hasta `k` iteraciones |

## Cómo correr el servicio

```bash
uvicorn main:app --reload
```

Documentación interactiva en `http://127.0.0.1:8000/docs`.

> **Nota:** dos endpoints (`/Cadenas/concatenar` y `/lenguajes/union`) declaraban un tipo de
> retorno (`-> str`, `-> set`) que no correspondía con el diccionario que en realidad devuelven,
> lo que hacía que FastAPI rechazara la respuesta con `ResponseValidationError` (error 500). Se
> quitó esa anotación incorrecta para que ambos endpoints funcionen igual que el resto.

## Ejercicios

Dado el alfabeto $\Sigma = \{a, b\}$ y los lenguajes:

- $L = \{\lambda, a, b\}$ (la cadena vacía $\lambda$ se representa como `""`)
- $M = \{b, aa\}$

se calcularon las siguientes operaciones **usando los endpoints anteriores** (llamadas
encadenadas cuando el ejercicio lo requería). El detalle de cada llamada está en el notebook;
aquí solo se listan los resultados.

### Operaciones de conjuntos

| Operación | Resultado |
|---|---|
| $L \cup M$ | $\{\lambda, a, b, aa\}$ |
| $L \cap M$ | $\{b\}$ |
| $L - M$ | $\{\lambda, a\}$ |
| $M - L$ | $\{aa\}$ |

### Operaciones sobre cadenas (concatenación de lenguajes)

| Operación | Resultado |
|---|---|
| $L \cdot M$ | $\{b, aa, ab, bb, aaa, baa\}$ |
| $M \cdot L$ | $\{b, aa, ba, bb, aaa, aab\}$ |
| $M^2$ | $\{bb, aab, baa, aaaa\}$ |

### Clausura de Kleene y combinación

`/lenguajes/kleene` recibe `k` como número de iteraciones, no como longitud máxima, así que se
llamó con `k = 8` y del resultado se tomaron los primeros 8 elementos en **orden shortlex**
(primero por longitud, luego alfabético) — el orden estándar para enumerar un lenguaje infinito.

| Operación | Resultado (primeros 8, orden shortlex) |
|---|---|
| $L^*$ | $[\lambda, a, b, aa, ab, ba, bb, aaa]$ |
| $M^*$ | $[\lambda, b, aa, bb, aab, baa, bbb, aaaa]$ |

Para $(LM) \cup (M^* \cap L^2)$ se reutilizaron los resultados ya obtenidos de $L \cdot M$ y de
$L^2$ (= concatenar con `L` y `M` iguales a $L$), y se calculó $M^*$ completo
(no solo los primeros 8) para la intersección:

| Paso | Resultado |
|---|---|
| $L^2$ | $\{\lambda, a, b, aa, ab, ba, bb\}$ |
| $M^* \cap L^2$ | $\{\lambda, b, aa, bb\}$ |
| $(LM) \cup (M^* \cap L^2)$ | $\{\lambda, b, aa, ab, bb, aaa, baa\}$ |