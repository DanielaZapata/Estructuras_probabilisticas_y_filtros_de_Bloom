#Filtro de Bloom implementado con un arreglo compacto de bits.
import math #importamos la biblioteca matemática 


class FiltroBloom:

    def __init__(self, n, tasa_error=0.01, m=None, k=None):

        if n <= 0:
            raise ValueError("La cantidad de elementos debe ser mayor que cero.") # si la cantidad de elementos a insertar es menor que cero, se genera el error

        if not 0 < tasa_error < 1:
            raise ValueError("La tasa de error debe estar entre 0 y 1.") # si la tasa no está entre cero y uno, se genera el error

        # Calculamos el tamaño del arreglo 
        if m is None:
            m = math.ceil(
                -n * math.log(tasa_error) / (math.log(2) ** 2) # el math.ceil redondea hacia arriba o sea si tengo 958.7, devuelve 959.
            )

        # verificamos que el tamaño del arreglo sea positivo.
        if m <= 0:
            raise ValueError("El tamaño del arreglo debe ser positivo.")

        # Calculamos la cantidad óptima aproximada de posiciones hash.
        if k is None:
            k = max(1, round((m / n) * math.log(2)))
        # utilizamos el round() para redondear el resultado al entero más cercano.
        # el max nos garantiza que el resultado sea mínimo uno.

        if k <= 0:
            raise ValueError("La cantidad de hashes debe ser positiva.") # impide utilizar cero o una cantidad negativa de posiciones hash.

        self.__n = n 
        self.__tasa_error = tasa_error
        self.__m = m 
        self.__k = k 
        self.__bits = bytearray((m + 7) // 8) # Cada byte almacena 8 bits.
        self.__insertados = 0 # Contador de inserciones.

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
    def insertados(self):
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

    #Calcular el hash FNV-1a de 32 bits.
    def _fnv1a(self, texto):

        h = 2166136261
        constante = 16777619
        residuo = 0xFFFFFFFF # Es para que el hash se mantenga dentro del rango de un entero de 32 bits, y el valor es de 4294967295

        # Convertimos el texto en bytes
        for byte in texto.encode("utf-8"):
            # Paso 1: XOR entre el hash y el byte, el operador ^ realiza la operación XOR
            h ^= byte

            # Paso 2: multiplicación por la constante FNV.
            h = (h * constante) & residuo # & hace el residuo para conservar solo los últimos 32 bits del hash.

        return h

    # Esta función recibe un valor hash y mezcla sus bits mediante varias operaciones y su propósito es ayudar a dispersar los valores hash antes de convertirlos en posiciones del filtro.
    def _mezclar(self, h):

        residuo = 0xFFFFFFFF

        # >> es el desplazamiento de bits hacia la derecha.
        h ^= h >> 16
        h = (h * 0x85EBCA6B) & residuo
        h ^= h >> 13
        h = (h * 0xC2B2AE35) & residuo
        h ^= h >> 16

        return h

    # Genera las posiciones del elemento en el arreglo
    def _posiciones(self, elemento):

        posiciones = []

        for i in range(self.__k):

            # El índice va al inicio para que cambie todo el recorrido de FNV-1a, y luego se mezclan los bits del resultado.
            valor_hash = self._mezclar(self._fnv1a(f"{i}:{elemento}")) # La expresión de la f crea un texto que combina el número de interación y el elmento 

            # El módulo convierte el hash en una posición válida.
            posicion = valor_hash % self.__m

            posiciones.append(posicion)

        return posiciones


    # Agregar un elemento activando sus posiciones
    def agregar(self, elemento):

        for posicion in self._posiciones(elemento):

            indice_byte = posicion // 8
            indice_bit = posicion % 8

            self.__bits[indice_byte] |= 1 << indice_bit # | es una asignación combinada con OR bit a bit 
        self.__n += 1

    # ver si el elemento posiblemente está en el filtro

    def contiene(self, elemento):

        for posicion in self._posiciones(elemento):

            indice_byte = posicion // 8
            indice_bit = posicion % 8

            bit = (self.__bits[indice_byte] >> indice_bit) & 1
            if bit == 0:
                return False

        return True

    # Cuenta cuántos bits están activados.
    def bits_encendidos(self):

        return sum(bin(byte).count("1") for byte in self.__bits)

    # Calcula la probabilidad teórica aproximada de falsos positivos
    def prob_falso_positivo(self):
            
        return (
            1 - math.exp(-self.k * self.n / self.m)
        ) ** self.k

    # Devuelve la memoria del arreglo en bytes
    def memoria_bytes(self):

        return len(self.__bits)

