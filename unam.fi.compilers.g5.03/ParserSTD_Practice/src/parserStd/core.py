from lark import Lark, Transformer, exceptions
import sys 

grammar = """
    ?start: sum
          | assign_var
          | declaration  // 3. Añadimos la nueva regla de declaración

    // 3. Nueva regla para "int x = ---"
    ?declaration: "int" NAME "=" sum -> declare_var

    // Regla de asignación 
    ?assign_var: NAME "=" sum -> assign_var

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    // 2. 'atom' ahora también acepta un STRING
    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "(" sum ")"
         | STRING           -> string  

    // --- Definiciones de Terminales ---
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
    
    // 1. Definicion de que es un STRING
    STRING: /"[^"]*"/ | /'[^']*'/
"""
#Implementación del SDT 
class verifSTD(Transformer):
    
    def number(self, items): 
        return float(items[0])
    
    def neg(self, items): 
        return -items[0]
    
    def add(self, items): 
        return items[0] + items[1]
    
    def sub(self, items): 
        return items[0] - items[1]
    
    def mul(self, items): 
        return items[0] * items[1]
    
    def div(self, items):
        if items[1] == 0:
            raise ZeroDivisionError("División por cero")
        return items[0] / items[1]
    
    def string(self, items):
        return items[0][1:-1] #Maneja el token string. Quita las comillas.

    def assign_var(self, items):
        #Para asignaciones simples (x = ...)
        # items[0] es el token NAME
        # items[1] es el valor ya calculado de 'sum'
        nombreVariable = items[0].value 
        valor = items[1]
        print(f"\nSDT Verified! (Asignación: {nombreVariable} = {valor})")
        return valor

    def declare_var(self, items):
        "Para declaraciones (int x = ...)"
        # items[0] es el token NAME
        # items[1] es el valor ya calculado de 'sum'
        nombreVariable = items[0].value 
        valor = items[1]           
        
        # Verificar si el valor es un string
        if isinstance(valor, str):
            # ERROR SEMANTICO!
            raise TypeError(f"Error de tipo: No se puede asignar un string ('{valor}') a la variable 'int {nombreVariable}'")
        
        # Si no es string, es un número, así que es válido
        print(f"\nSDT Verified! (Declaración: int {nombreVariable} = {valor})")
        return valor

# Creación del Parser 
try:
    parser = Lark(grammar)
    std = verifSTD()
except exceptions.LarkError as e:
    print(f"Error en la gramática... : {e}")
    parser = None

def main():
    if parser:
        print("\n---Parser y STD---")

        while True:

            instruccion = input("Ingresa la cadena a analizar: ")

            if instruccion.lower() == 'salir':
                break 

            if not instruccion: 
                continue

            print(f"\nProbando: {instruccion} ")
            try:
                arbol = parser.parse(instruccion)
                print("\nParsing Success!")

                try:
                    with open("parseTree.txt", "w", encoding="utf-8") as f:
                        f.write(arbol.pretty())
                        print("Parse Tree guardado en 'parseTree.txt'")
                except IOError as e:
                        print(f"Error al escribir el archivo del árbol: {e}")

                resultado = std.transform(arbol)

                if arbol.data == 'add':
                    print(f"\nSDT Verified! Resultado: {resultado}")

            except exceptions.VisitError as e_sdt:
                print(f"\nSDT error...!\nDetalle: {e_sdt.orig_exc}")
            except exceptions.LarkError as e_parse:
                print(f"Parsing error...!\nDetalle: {e_parse}")

            print("-" * 40)


if __name__ == "__main__":
    main()