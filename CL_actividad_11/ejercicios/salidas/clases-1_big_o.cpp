# Proposito: Define una clase Persona y prueba sus atributos y metodos en la funcion principal.
#include <iostream>
#include <string>

using namespace std;

class Persona {
	public:
		string nombre;
		int edad;
		void saludar(){
			cout << "Hola mundo" << endl; // O(1)
		}
		int suma(int a, int b){
			return a+b; // O(1)
		}
};

int main() {
	Persona daniel; // O(1)
	daniel.nombre = "Paulo"; // O(1)
	daniel.edad = 46; // O(1)
	cout << "Mi nombre es " << daniel.nombre << endl; // O(1)
	cout << "Mi edad es de " << daniel.edad << " anios" << endl; // O(1)
	daniel.saludar(); // O(1)
	cout << daniel.suma(2, 8) << endl; // O(1)
	return 0; // O(1)
}
# Suma de complejidades individuales: O(1) + O(1) + O(1) + O(1) + O(1) + O(1) + O(1) + O(1) + O(1) + O(1) = 10
# Complejidad de mayor grado: O(1)
