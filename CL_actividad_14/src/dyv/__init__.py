# Actividad 14 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Multiplicacion de enteros gigantes con divide y venceras:
#   digitos.py    partir un numero en mitades y multiplicar por 10^k sin usar  *
#   medicion.py   contador de multiplicaciones/llamadas, tiempo y memoria
#   escolar.py    multiplicacion de primaria, digito por digito (sin divide y venceras)
#   clasico.py    divide y venceras con 4 multiplicaciones recursivas
#   karatsuba.py  divide y venceras con 3 multiplicaciones recursivas (Karatsuba)

from dyv.clasico import multiplicar_clasico
from dyv.digitos import numero_aleatorio
from dyv.escolar import multiplicar_escolar
from dyv.karatsuba import multiplicar_karatsuba
from dyv.medicion import medir, multiplicar_python
