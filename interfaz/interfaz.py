import tkinter as tk
from . import estilo_boton
from . import FuncionBotones as F

#ventana de ingreso
ventana = tk.Tk()
ventana.title("MaulencitosMarket")
ventana.geometry("350x350")

# Codigo realizado por Jose Cofre
texto = tk.Label(ventana, text="Nombre Usuario")
texto.grid(row=2, column=2, padx=(40, 0), pady=(40, 0))

IngresoNombre = tk.Entry(ventana)
IngresoNombre.grid(row=2, column=3, padx=(10, 40), pady=(40, 0))

texto = tk.Label(ventana, text="Clave Usuario")
texto.grid(row=3, column=2, padx=(40, 0), pady=(10, 0))

IngresoClave = tk.Entry(ventana, show="*")
IngresoClave.grid(row=3, column=3, padx=(10, 40), pady=(10, 0))


# Codigo realizado por Jose Cofre
#botones,llamamos al archivo estilo_boton
boton_registrar = estilo_boton.crear_boton_verde(ventana, "Registrar",lambda:F.registro(IngresoNombre,IngresoClave,ventana)) 
boton_registrar.grid(row=4, column=2, padx=(40, 10), pady=(20, 0))

boton_ingresar = estilo_boton.crear_boton_verde(ventana, "Ingresar",lambda: F.ventana_usuario(ventana,IngresoNombre,IngresoClave)) 
boton_ingresar.grid(row=4, column=3, padx=(10, 40), pady=(20, 0))

#texto para cambiar al login del admin
cambiar_admin= tk.Label(ventana, text="¿Eres administrador? Haz click aqui")
cambiar_admin.grid(row=5, column=2, padx=(0,0), pady=(170, 0))
cambiar_admin.bind("<Button-1>",lambda event:F.ventana_admin(ventana))

ventana.mainloop()