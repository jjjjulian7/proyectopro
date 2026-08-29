import tkinter as tk
import os

def cargar_foto(nombre_archivo):
    """
    Busca la imagen en la carpeta 'imagenes' y la convierte a PhotoImage.
    Asume que tienes una carpeta llamada 'imagenes' junto a tus scripts.
    """
    ruta_completa = f"imagenes/{nombre_archivo}.png"  #el codigo automaticamente arma la frase
    
    #Comprobación de seguridad por si la imagen no existe (se mete a buscar el archivo)
    if not os.path.exists(ruta_completa):
        print(f"Error: No se encontró {ruta_completa}")
        return None
        
    #Cargamos y devolvemos la imagen
    return tk.PhotoImage(file=ruta_completa)