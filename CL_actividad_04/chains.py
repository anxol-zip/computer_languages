def concatenar_cadenas(x: str, y:str) -> str:
	return x+y

def invertir_cadena(x: str) -> str:
	return x[::-1]

def potencia_cadena(x: str, k: int) -> str:
	if k <= 0:
		return "" #Si la potencia es cero o menor que cero, devuelve la cadena
	return x*k

print("Concatenación de cadenas: ", concatenar_cadenas('0', '1'))
print("Inversión de una cadena: ", invertir_cadena("hola"))
print("Potencia de una cadena: ", potencia_cadena("ab", 0))
print("Potencia de una cadena: ", potencia_cadena("ab", 1))
print("Potencia de una cadena: ", potencia_cadena("ab", 2))