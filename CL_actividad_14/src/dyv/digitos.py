# Actividad 14 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Operaciones sobre los digitos decimales de un entero no negativo.
#
# Karatsuba trabaja con los digitos del numero, no con su valor: partir un numero en
# dos mitades y "multiplicar por 10^k" son solo cortar la cadena de digitos o pegarle
# ceros. Por eso aqui se hacen con cadenas y no con  //, %  ni  * : asi el unico  *
# de los algoritmos recursivos queda en su caso base (un digito por un digito), y
# contar multiplicaciones es contar exactamente esas.


def num_digitos(x):
    return len(str(x))


def partir(x, m):
    """Divide x en (alta, baja), donde baja son sus ultimos m digitos.

    Ejemplo: partir(123456, 2) -> (1234, 56), porque 123456 = 1234 * 10^2 + 56.
    """
    s = str(x)
    if len(s) <= m:
        return 0, x
    return int(s[:-m]), int(s[-m:])


def desplazar(x, k):
    """x * 10^k sin multiplicar: se le agregan k ceros a la derecha."""
    if x == 0:
        return 0
    return int(str(x) + "0" * k)


def aplicar_signo(x, y, producto):
    """Los algoritmos multiplican valores absolutos; el signo se decide aparte."""
    negativo = (x < 0) != (y < 0)
    return -producto if negativo else producto


def numero_aleatorio(n, rng):
    """Entero de exactamente n digitos (el primero nunca es 0)."""
    return rng.randint(10 ** (n - 1), 10**n - 1)
