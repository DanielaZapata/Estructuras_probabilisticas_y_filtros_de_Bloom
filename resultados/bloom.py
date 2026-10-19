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

            self.bits[indice_byte] |= 1 << indice_bit # | es una asignación combinada con OR bit a bit 
        self.__n += 1

# ver si el elemento posiblemente está en el filtro

def contiene(self, elemento):

        for posicion in self._posiciones(elemento):

            indice_byte = posicion // 8
            indice_bit = posicion % 8

            bit = (self.bits[indice_byte] >> indice_bit) & 1
            if bit == 0:
                return False

        return True

# Cuenta cuántos bits están activados.
def bits_encendidos(self):

        return sum(bin(byte).count("1") for byte in self.bits)

# Calcula la probabilidad teórica aproximada de falsos positivos
def prob_falso_positivo(self):
        
        return (
            1 - math.exp(-self.k * self.n / self.m)
        ) ** self.k

# Devuelve la memoria del arreglo en bytes
def memoria_bytes(self):

        return len(self.bits)