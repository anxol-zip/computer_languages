// Proposito: Define una clase Persona con atributos y metodos, y crea una instancia para mostrar su uso e imprimir resultados en consola.
#include <iostream>
#include <string>

using namespace std;

class Persona {
	public:
		string nombre;
		int edad;
		void saludar(){
			cout << "Hola mundo" << endl; // Ω(1)
		}
		int suma(int a, int b){
			return a+b; // Ω(1)
		}
};

int main() {
	Persona daniel; // Ω(1)
	daniel.nombre = "Paulo"; // Ω(1)
	daniel.edad = 46; // Ω(1)
	cout << "Mi nombre es " << daniel.nombre << endl; // Ω(1)
	cout << "Mi edad es de " << daniel.edad << " anios" << endl; // Ω(1)
	daniel.saludar(); // Ω(1)
	cout << daniel.suma(2, 8) << endl; // Ω(1)
	return 0; // Ω(1)
}
// Suma de complejidades individuales: Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) = 10
// Complejidad de mayor grado: Ω(1)
