import os
import sys
CARPETA_RESULTADOS_TEMP = os.path.dirname(os.path.abspath(__file__))
if CARPETA_RESULTADOS_TEMP not in sys.path:
    sys.path.insert(0, CARPETA_RESULTADOS_TEMP)

import csv
import random
import time
import unicodedata

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bloom import FiltroBloom


# Rutas del proyecto.
CARPETA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_CSV = os.path.join(CARPETA, "datos", "municipios.csv")
CARPETA_RESULTADOS = os.path.join(CARPETA, "resultados")

random.seed(42)


def normalizar(texto):
    """Pasa a minusculas y quita tildes (Medellín -> medellin)."""

    texto = unicodedata.normalize("NFD", texto.strip().lower())

    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def cargar_municipios():
    """Carga los municipios del archivo CSV."""

    if not os.path.exists(RUTA_CSV):
        raise FileNotFoundError(
            f"No se encontró el archivo: {RUTA_CSV}"
        )

    municipios = []

    with open(RUTA_CSV, encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)

        if not lector.fieldnames:
            raise ValueError("El CSV no contiene encabezados.")

        columna = None

        # Buscamos la columna exacta con los nombres. Ojo: "Codigo Municipio"
        # tambien contiene la palabra "municipio", por eso no se usa esa
        # coincidencia parcial.
        for encabezado in lector.fieldnames:
            if encabezado.strip().lower() == "nombre municipio":
                columna = encabezado
                break

        if columna is None:
            raise ValueError(
                "No se encontró la columna 'Nombre Municipio'. "
                f"Columnas disponibles: {lector.fieldnames}"
            )

        for fila in lector:
            valor = fila.get(columna)

            if valor:
                nombre = normalizar(valor)

                if nombre:
                    municipios.append(nombre)

    # Eliminamos duplicados y ordenamos para obtener datos consistentes.
    municipios = sorted(set(municipios))

    if len(municipios) < 2:
        raise ValueError(
            "Se necesitan al menos dos municipios para realizar "
            "los experimentos."
        )

    return municipios


def tamano_set(conjunto):
    """Estima la memoria del set y de las cadenas almacenadas."""

    return (
        sys.getsizeof(conjunto)
        + sum(sys.getsizeof(nombre) for nombre in conjunto)
    )


def ejecutar():
    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)

    municipios = cargar_municipios()

    random.shuffle(municipios)

    mitad = len(municipios) // 2

    registrados = municipios[:mitad]
    no_insertados = municipios[mitad:]

    print("=" * 55)
    print("PROYECTO: FILTRO DE BLOOM PARA MUNICIPIOS")
    print("=" * 55)

    print(f"Municipios disponibles: {len(municipios)}")
    print(f"Municipios insertados: {len(registrados)}")
    print(f"Municipios no insertados: {len(no_insertados)}")

    # --------------------------------------------------
    # 1. CREAR E INSERTAR EN EL FILTRO
    # --------------------------------------------------

    print("\n1. CREACIÓN DEL FILTRO")

    tasa_error_objetivo = 0.01

    filtro = FiltroBloom(
        n_esperado=len(registrados),
        tasa_error=tasa_error_objetivo
    )

    inicio = time.perf_counter()

    for municipio in registrados:
        filtro.agregar(municipio)

    tiempo_insercion = time.perf_counter() - inicio

    conjunto = set(registrados)

    print(f"Tamaño del arreglo (m): {filtro.m} bits")
    print(f"Posiciones hash (k): {filtro.k}")
    print(f"Bits encendidos: {filtro.bits_encendidos()}")
    print(f"Memoria del filtro: {filtro.memoria_bytes()} bytes")
    print(f"Memoria estimada del set: {tamano_set(conjunto)} bytes")
    print(f"Tiempo de insercion: {tiempo_insercion:.6f} segundos")

    # --------------------------------------------------
    # 2. COMPROBAR FALSOS NEGATIVOS
    # --------------------------------------------------

    print("\n2. COMPROBACION DE FALSOS NEGATIVOS")

    falsos_negativos = sum(
        1
        for municipio in registrados
        if not filtro.contiene(municipio)
    )

    print(f"Falsos negativos: {falsos_negativos}")

    if falsos_negativos == 0:
        print("Correcto: todos los municipios insertados se reconocen.")
    else:
        print("ATENCION: se detectaron falsos negativos.")

    # --------------------------------------------------
    # 3. MEDIR FALSOS POSITIVOS
    # --------------------------------------------------

    print("\n3. MEDICION DE FALSOS POSITIVOS")

    falsos_positivos = sum(
        1
        for municipio in no_insertados
        if filtro.contiene(municipio)
    )

    cantidad_no_insertados = len(no_insertados)

    tasa_real = falsos_positivos / cantidad_no_insertados

    tasa_teorica = filtro.prob_falso_positivo()

    print(f"Consultas de municipios no insertados: {cantidad_no_insertados}")
    print(f"Falsos positivos: {falsos_positivos}")
    print(f"Tasa real: {tasa_real:.4%}")
    print(f"Tasa teorica aproximada: {tasa_teorica:.4%}")