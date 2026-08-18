import tkinter as tk
import estilo_boton as estilo_boton

#ventana de ingreso
ventana = tk.Tk()
ventana.title("MaulencitosMarket")
ventana.geometry("350x350")


texto = tk.Label(ventana, text="Nombre Usuario")
texto.grid(row=2, column=2, padx=(40, 0), pady=(40, 0))

IngresoNombre = tk.Entry(ventana)
IngresoNombre.grid(row=2, column=3, padx=(10, 40), pady=(40, 0))

texto = tk.Label(ventana, text="Clave Usuario")
texto.grid(row=3, column=2, padx=(40, 0), pady=(10, 0))

IngresoClave = tk.Entry(ventana, show="*")
IngresoClave.grid(row=3, column=3, padx=(10, 40), pady=(10, 0))

#funciones a completar despues con sqlite3
def ventana_de_admin():
        #falta agregar modo de confirmacion
        ventana3=tk.Toplevel(ventana)
        ventana3.geometry("350x350")
        BarraBusqueda=tk.Frame(ventana3, bg="#8ADEFF", height=50)
        BarraBusqueda.pack(fill="x")
<<<<<<< HEAD
        ventana.iconify()
        
=======
        buscador=tk.Entry(ventana3,text="Ingrese nombre producto")
        buscador.grid(row=1,column=2,padx=(10,40),pady=(10,0))
        ventana.iconify()

>>>>>>> d0414bce06a64c402ac5f413510444fcc07b0b3c
def simular_registro():
    print("El boton Registrar funciona correctamente")

#botones,llamamos al archivo estilo_boton
boton_registrar = estilo_boton.crear_boton_verde(ventana, "Registrar", simular_registro) 
boton_registrar.grid(row=4, column=2, padx=(40, 10), pady=(20, 0))

boton_ingresar = estilo_boton.crear_boton_verde(ventana, "Ingresar", ventana_de_admin) 
boton_ingresar.grid(row=4, column=3, padx=(10, 40), pady=(20, 0))


<<<<<<< HEAD
cambiar_admin= tk.Label(ventana, text="¿Eres administrador? Haz click aqui")
cambiar_admin.grid(row=5, column=2, padx=(0,0), pady=(170, 0))
cambiar_admin=tk.Toplevel(ventana)
=======
>>>>>>> d0414bce06a64c402ac5f413510444fcc07b0b3c

ventana.mainloop()