import tkinter as tk
from . import FuncionBotones as F
from . import estilo_boton
import tkinter.messagebox as messagebox
from clases import usuario 

def ejecutar():
    #ventana de ingreso
    ventana = tk.Toplevel()
    ventana.title("MaulencitosMarket")
    ventana.geometry("1280x700")
    #   AJUSTES DE LA VENTANA Y POSICIONAMENTO DE LOS ELEMENTOSSSSSSSSSSSSSSSSSSSSSSSSSS
    # Codigo realizado por Jose Cofre
    texto = tk.Label(ventana, text="Nombre Usuario")
    texto.grid(row=3, column=2, padx=(300, 0), pady=(210, 0))

    texto = tk.Label(ventana, text="Clave Usuario")
    texto.grid(row=4, column=2, padx=(300, 0), pady=(20, 0))

    IngresoNombre = tk.Entry(ventana)
    IngresoNombre.grid(row=3, column=3, padx=(10, 300), pady=(210, 0))

    IngresoClave = tk.Entry(ventana, show="*")
    IngresoClave.grid(row=4, column=3, padx=(10, 300), pady=(20, 0))


    # Codigo realizado por Jose Cofre
    #botones,llamamos al archivo estilo_boton
    boton_registrar = estilo_boton.crear_boton_verde(ventana, "Registrar",lambda:F.registro(IngresoNombre,IngresoClave,ventana)) 
    boton_registrar.grid(row=5, column=2, padx=(300, 10), pady=(50, 0))

    boton_ingresar = estilo_boton.crear_boton_verde(ventana, "Ingresar",lambda: F.ventana_usuario(ventana,IngresoNombre,IngresoClave)) 
    boton_ingresar.grid(row=5, column=3, padx=(10, 300), pady=(50, 0))
