from lark import Lark, Transformer, exceptions
import sys 

grammar = """
    ?start: sum
          | assign_var
          | declaration  

    ?declaration: "int" NAME "=" sum -> declare_var

    ?assign_var: NAME "=" sum -> assign_var

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "(" sum ")"
         | STRING           -> string  

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
    
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
        return items[0][1:-1] #Maneja el token string. Quita comillas

    def assign_var(self, items):
        #Para asignaciones simples (x = ...)
        # items[0] es el token NAME
        # items[1] es el valor ya calculado de 'sum'
        nombreVariable = items[0].value 
        valor = items[1]
        print(f"SDT Verified! (Asignación: {nombreVariable} = {valor})")
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
        print(f"SDT Verified! (Declaración: int {nombreVariable} = {valor})")
        return valor

# Creación del Parser 
try:
    parser = Lark(grammar)
    std = verifSTD()
    print("Parser creado exitosamente")
except exceptions.LarkError as e:
    print(f"Error en la gramática... : {e}")
    parser = None

print("-" * 50)

# PRUEBAS 
if parser:

    # --- CASO 1: Declaración valida (int var = operac) 
    instruccion_valida = "int operac =  2 + (3 - 1) * 5 / 2"
    print(f"Probando: '{instruccion_valida}'")
    try:
        arbol = parser.parse(instruccion_valida)
        print("Parsing Success!")
        resultado = std.transform(arbol)
        
    except exceptions.VisitError as e_sdt:
        print(f"SDT error...!\n     Detalle: {e_sdt.orig_exc}")
    except exceptions.LarkError as e_parse:
        print(f"Parsing error...!\n     Detalle: {e_parse}")

    print("-" * 20)

    # --- CASO 2: Declaración valida (int var = numero) 
    instruccion_valida = "int x = 5"
    print(f"Probando: '{instruccion_valida}'")
    try:
        arbol = parser.parse(instruccion_valida)
        print("Parsing Success!")
        resultado = std.transform(arbol)
        
    except exceptions.VisitError as e_sdt:
        print(f"SDT error...!\n     Detalle: {e_sdt.orig_exc}")
    except exceptions.LarkError as e_parse:
        print(f"Parsing error...!\n     Detalle: {e_parse}")

    print("-" * 20)

    # --- CASO 3: Asignación de string valido (x = '...') 
    instruccion_string_valida = "x = 'Hola mundo'"
    print(f"Probando: '{instruccion_string_valida}'")
    try:
        arbol = parser.parse(instruccion_string_valida)
        print("Parsing Success!")
        resultado = std.transform(arbol)
        
    except exceptions.VisitError as e_sdt:
        print(f"SDT error...!\n     Detalle: {e_sdt.orig_exc}")
    except exceptions.LarkError as e_parse:
        print(f"Parsing error...!\n     Detalle: {e_parse}")

    print("-" * 20)

    # --- CASO 4: Declaración invalida (Error de SDT) 
    instruccion_sdt_malo = "int z = 'falla'"
    print(f"Probando: '{instruccion_sdt_malo}'")
    try:
        arbol = parser.parse(instruccion_sdt_malo)
        print("Parsing Success!") # Salida esperada
        
        resultado = std.transform(arbol)
        
    except exceptions.VisitError as e_sdt: # ¡Este se activará!
        if isinstance(e_sdt.orig_exc, TypeError):
            print(f"SDT error...!\nDetalle: {e_sdt.orig_exc}")
        else:
            raise e_sdt 
    except exceptions.LarkError as e_parse:
        print(f"Parsing error...!\nDetalle: {e_parse}")

    print("-" * 20)

    # --- CASO 5: Declaración invalida (Error de SDT, division entre 0) 

    instruccion_string_valida = "x = 9/0"
    print(f"Probando: '{instruccion_string_valida}'")
    try:
        arbol = parser.parse(instruccion_string_valida)
        print("Parsing Success!")
        resultado = std.transform(arbol)
        
    except exceptions.VisitError as e_sdt:
        print(f"SDT error...!\nDetalle: {e_sdt.orig_exc}")
    except exceptions.LarkError as e_parse:
        print(f"Parsing error...!\nDetalle: {e_parse}")

    print("-" * 20)
