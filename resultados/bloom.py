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

        