#Filtro de Bloom implementado con un arreglo compacto de bits.
import math #importamos la biblioteca matemática 


class FiltroBloom:

    def __init__(self, n, tasa_error=0.01, m=None, k=None):

        self.__n = n 
        self.__tasa_error = tasa_error
        self.__m = m 
        self.__k = k 
