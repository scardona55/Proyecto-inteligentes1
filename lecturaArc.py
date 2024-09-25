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
            contenido = archivo.readlines()
            
            # Quitar saltos de línea y dividir en filas
            mapa = [linea.strip().split(',') for linea in contenido]

            # Obtener el tamaño esperado de las filas
            columnas_esperadas = len(mapa[0])

            # Verificar que todas las filas tengan el mismo número de columnas
            for fila in mapa:
                if len(fila) != columnas_esperadas:
                    print("Error: Una fila no tiene el número correcto de columnas.")
                    return
            
            # Verificacion de caracteres
            caracteres_validos = {'C', 'C_b', 'M', 'R'}
            for fila in mapa:
                for celda in fila:
                    if celda not in caracteres_validos:
                        print(f"Error: El carácter '{celda}' no es válido en el mapa.")
                        return

            print("El mapa es válido.")
            print(f"Dimensiones: {len(mapa)} filas x {columnas_esperadas} columnas")

    except FileNotFoundError:
        print(f"El archivo '{ruta_archivo}' no se encontró.")
    except Exception as e:
        print(f"Ha ocurrido un error: {e}")

ruta = cargar_archivo()
if ruta:  # Verificar si el usuario seleccionó un archivo
    validar_mapa(ruta)
else:
    print("No se seleccionó ningún archivo.")
