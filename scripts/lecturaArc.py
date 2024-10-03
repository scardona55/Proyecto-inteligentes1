import tkinter as tk
from tkinter import filedialog

def cargar_archivo():
    root = tk.Tk()
    root.withdraw()
    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    return ruta_archivo

def validar_mapa(ruta_archivo):
    try:
        with open(ruta_archivo, 'r') as archivo:
            lineas = archivo.readlines()
            
            mapa = []
            salida_encontrada = False  # Para verificar si hay al menos una salida
            for linea in lineas:
                fila = linea.strip().split(',')
                mapa.append(fila)

                # Verificar si hay una salida en la fila
                if 'S' in fila:
                    salida_encontrada = True

            # Verificar que todas las filas tengan el mismo número de columnas
            columnas_esperadas = len(mapa[0])
            for fila in mapa:
                if len(fila) != columnas_esperadas:
                    print("Error: Una fila no tiene el número correcto de columnas.")
                    return None
            
            # Verificación de caracteres
            caracteres_validos = {'C', 'C_b', 'M', 'R', 'S'}
            for fila in mapa:
                for celda in fila:
                    if celda not in caracteres_validos:
                        print(f"Error: El carácter '{celda}' no es válido en el mapa.")
                        return None

            if not salida_encontrada:
                print("Error: No se encontró ninguna salida en el mapa.")
                return None

            print("El mapa es válido.")
            print(f"Dimensiones: {len(mapa)} filas x {columnas_esperadas} columnas")
            return mapa  # Retorna el mapa validado

    except FileNotFoundError:
        print(f"El archivo '{ruta_archivo}' no se encontró.")
        return None
    except Exception as e:
        print(f"Ha ocurrido un error: {e}")
        return None
