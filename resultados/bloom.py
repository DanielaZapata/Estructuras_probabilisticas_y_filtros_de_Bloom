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

