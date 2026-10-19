import math

class FiltroBloom:
    def __init__(self, n_esperado, tasa_error=0.01, m=None, k=None):
        self.n_esperado = n_esperado
        # si no pasan m y k los calculo con las formulas
        if m is None:
            m = math.ceil(-n_esperado * math.log(tasa_error) / (math.log(2) ** 2))
        if k is None:
            k = max(1, round((m / n_esperado) * math.log(2)))
        self.m = m
        self.k = k
        self.bits = bytearray((m + 7) // 8)  # 8 bits por byte
        self.n = 0  # cuantos elementos he insertado