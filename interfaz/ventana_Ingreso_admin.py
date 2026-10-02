import tkinter as tk
from . import estilo_boton
from . import FuncionBotones as F

def abrir_ventana_funcionario():
    #ventana de ingreso
    ventana = tk.Tk() 
    ventana.title("MaulencitosMarketLoginADMIN")
    ventana.geometry("1280x700")
    
    #AJUSTES DE LA VENTANA Y POSICIONAMENTO DE LOS ELEMENTOSSSSSSSSSSSSSSSSSSSSSSSSSS
    # Codigo realizado por Jose Cofre
    texto = tk.Label(ventana, text="RUT Funcionario")
    texto.grid(row=3, column=2, padx=(250, 0), pady=(210, 0))
    
    texto = tk.Label(ventana, text="Clave Funcionario")
    texto.grid(row=4, column=2, padx=(250, 0), pady=(20, 0))
    
    IngresoNombre = tk.Entry(ventana)
    IngresoNombre.grid(row=3, column=3, padx=(10, 300), pady=(210, 0))
    
    IngresoClave = tk.Entry(ventana, show="*")
    IngresoClave.grid(row=4, column=3, padx=(10, 300), pady=(20, 0))
    
    
    # Codigo realizado por Jose Cofre
    #botones,llamamos al archivo estilo_boton

    
    boton_ingresar = estilo_boton.crear_boton_verde(ventana, "Ingresar",lambda: F.ventana_a(ventana)) 
    boton_ingresar.grid(row=5, column=3, padx=(10, 250), pady=(50, 0))

    
    ventana.mainloop()