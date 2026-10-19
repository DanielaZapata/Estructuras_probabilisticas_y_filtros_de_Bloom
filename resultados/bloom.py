#Filtro de Bloom implementado con un arreglo compacto de bits.
import math #importamos la biblioteca matemática 


class FiltroBloom:

    def __init__(self, n, tasa_error=0.01, m=None, k=None):

        self.__n = n 
        self.__tasa_error = tasa_error
        self.__m = m 
        self.__k = k 

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
        
#SETTERS 
@n.setter
def n(self, n):
    self.__n
@tasa_error.setter
def tasa_error(self, tasa_error):
    self.__tasa_error
@m.setter
def m(self, m):
    self.__m
@k.setter
def k(self, k):
    self.__k
        
        