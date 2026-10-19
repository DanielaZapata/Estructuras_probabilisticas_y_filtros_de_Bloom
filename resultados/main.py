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
        n=len(registrados),
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

    # --------------------------------------------------
    # 4. COMPARAR TIEMPOS DE CONSULTA
    # --------------------------------------------------

    print("\n4. COMPARACIÓN DE TIEMPOS")

    consultas = no_insertados

    inicio = time.perf_counter()

    for municipio in consultas:
        filtro.contiene(municipio)

    tiempo_bloom = time.perf_counter() - inicio

    inicio = time.perf_counter()

    for municipio in consultas:
        municipio in conjunto

    tiempo_set = time.perf_counter() - inicio

    print(f"Consultas realizadas: {len(consultas)}")
    print(f"Tiempo del filtro Bloom: {tiempo_bloom:.6f} segundos")
    print(f"Tiempo del set: {tiempo_set:.6f} segundos")

    # --------------------------------------------------
    # 5. EXPERIMENTO CON DIFERENTES TAMAÑOS
    # --------------------------------------------------

    print("\n5. EFECTO DEL TAMAÑO DEL ARREGLO")

    razones = [4, 6, 8, 10, 12, 16]

    resultados_reales = []
    resultados_teoricos = []

    # Usamos una muestra para mantener razonable el tiempo de ejecución.
    cantidad_muestra = min(
        5000,
        len(registrados),
        len(no_insertados)
    )

    muestra_registrados = random.sample(
        registrados,
        cantidad_muestra
    )

    muestra_ausentes = random.sample(
        no_insertados,
        cantidad_muestra
    )

    n = len(muestra_registrados)

    for razon in razones:

        m = n * razon
        k = max(1, round(razon * 0.693))

        filtro_prueba = FiltroBloom(
            n=n,
            m=m,
            k=k
        )

        for municipio in muestra_registrados:
            filtro_prueba.agregar(municipio)

        falsos = sum(
            1
            for municipio in muestra_ausentes
            if filtro_prueba.contiene(municipio)
        )

        tasa_experimental = falsos / len(muestra_ausentes)

        tasa_estimacion = filtro_prueba.prob_falso_positivo()

        resultados_reales.append(tasa_experimental)
        resultados_teoricos.append(tasa_estimacion)

        print(
            f"m/n={razon:2} | "
            f"k={k:2} | "
            f"Real={tasa_experimental:.4%} | "
            f"Teórica={tasa_estimacion:.4%}"
        )

    # --------------------------------------------------
    # 6. GENERAR GRÁFICA
    # --------------------------------------------------

    ruta_grafica = os.path.join(
        CARPETA_RESULTADOS,
        "comparacion_falsos_positivos.png"
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        razones,
        resultados_reales,
        "o-",
        label="Tasa experimental",
        color="#ff90ff"
    )

    plt.plot(
        razones,
        resultados_teoricos,
        "s--",
        label="Tasa teórica",
        color="#6f63ff"
    )

    plt.xlabel("Bits por elemento (m/n)")
    plt.ylabel("Probabilidad de falso positivo")
    plt.title("Tamaño del filtro y falsos positivos")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(ruta_grafica, dpi=150)
    plt.close()

    print(f"\nGráfica guardada en: {ruta_grafica}")

    # --------------------------------------------------
    # 7. SIMULAR UNA CONSULTA INTERACTIVA
    # --------------------------------------------------

    print("\n7. CONSULTA INTERACTIVA")

    nombre = normalizar(input(
        "Escribe el nombre de un municipio para consultarlo: "
    ))

    if filtro.contiene(nombre):
        print("El municipio posiblemente está registrado.")

        if nombre in conjunto:
            print("Confirmación: sí está en el conjunto real.")
        else:
            print(
                "El filtro produjo un posible falso positivo. "
                "Hay que confirmar en la base de datos."
            )

    else:
        print("El municipio definitivamente no está en el filtro.")

        if nombre in conjunto:
            print(
                "ATENCIÓN: este resultado contradice la pertenencia "
                "al conjunto."
            )


if __name__ == "__main__":
    ejecutar()