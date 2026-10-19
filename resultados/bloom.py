#Filtro de Bloom implementado con un arreglo compacto de bits.
import math #importamos la biblioteca matemática 


class FiltroBloom:

    def __init__(self, n, tasa_error=0.01, m=None, k=None):

        self.__n = n 
        self.__tasa_error = tasa_error
        self.__m = m 
        self.__k = k 
        self.__bits = bytearray((m + 7) // 8) # Cada byte almacena 8 bits.
        self.__n = 0 # Contador de inserciones.

#GETTERS
@property 
def n(self):
    return self.__n
@property 
def tasa_error(self):
    return self.__tasa_error
@property
def m(self):
    return self.__m
@property 
def k(self):
    return self.__k
@property 
def instertados(self):
    return self.__insertados
        
#SETTERS 
@n.setter
def n(self, n):
    self.__n = n 
@tasa_error.setter
def tasa_error(self, tasa_error):
    self.__tasa_error = tasa_error 
@m.setter
def m(self, m):
    self.__m = m 
@k.setter
def k(self, k):
    self.__k = k
        
if n <= 0:
    raise ValueError("La cantidad de elementos debe ser mayor que cero.") # si la cantidad de elementos a insertar es menor que cero, se genera el error

if not 0 < tasa_error < 1:
    raise ValueError("La tasa de error debe estar entre 0 y 1.") # si la tasa no está entre cero y uno, se genera el error


# Calculamos el tamaño del arreglo 
if m is None:
    m = math.ceil(
        -n_esperado * math.log(tasa_error) / (math.log(2) ** 2) # el math.ceil redondea hacia arriba o sea si tengo 958.7, devuelve 959.
    )

# verificamos que el tamaño del arreglo sea positivo.
if m <= 0:
    raise ValueError("El tamaño del arreglo debe ser positivo.")

# Calculamos la cantidad óptima aproximada de posiciones hash.
if k is None:
    k = max(1, round((m / n_esperado) * math.log(2)))
# utilizamos el round() para redondear el resultado al entero más cercano.
# el max nos garantiza que el resultado sea mínimo uno.

if k <= 0:
    raise ValueError("La cantidad de hashes debe ser positiva.") # impide utilizar cero o una cantidad negativa de posiciones hash.


   