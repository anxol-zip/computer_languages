def union_lenguajes(L: set, M:set) -> set:
	return L.union(M)

def interseccion_lenguajes(L: set, M: set) -> set:
	return L.intersection(M)

def diferencia_lenguajes(L: set, M:set) -> set:
	return L.difference(M)

def concatenar_lenguajes(L: set, M:set) -> set:
	return [x + y for x in L for y in M]

L = {"ab", "bb"}
M = {"a", "b"}
print("Unión de lenguajes: ", union_lenguajes(L, M))
print("Intersección de lenguajes: ", interseccion_lenguajes(L, M))
print("Diferencia de lenguajes: ", diferencia_lenguajes(L, M))
print("Concatenación de lenguajes: ", concatenar_lenguajes(L, M))