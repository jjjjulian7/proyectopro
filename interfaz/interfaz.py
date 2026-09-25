import tkinter as tk
from . import FuncionBotones as F
from . import estilo_boton
from .ventana_Ingreso_admin import abrir_ventana_funcionario
import tkinter.messagebox as messagebox
from clases import usuario 

def ejecutar():
    def ir_a_admin(event):
        ventana.withdraw() # Oculta la ventana principal (Guardamos lo que tenia)
        abrir_ventana_funcionario() # Abre la ventana de funcionario

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


    cambiar_admin= tk.Label(ventana, text="¿Eres administrador? Haz click aqui")
    cambiar_admin.grid(row=12, column=0, padx=(0,0), pady=(300, 0))
    cambiar_admin.bind("<Button-1>",ir_a_admin,lambda event: abrir_ventana_funcionario())