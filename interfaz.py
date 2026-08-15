import tkinter as tk

#configuracion que tendra la ventana
ventana=tk.Tk()
ventana.title("MauelncitosMarket")
ventana.geometry("300x350")

texto=tk.Label(ventana,text="Nombre Usuario")
IngresoNombre=tk.Entry(ventana)
contraseña=tk.Label(ventana,text="contraseña")
IngresoContraseña=tk.Entry(ventana,show="*")
BotonIngreso=tk.Button(ventana,text="Ingresar")

#colocar los objetos creados en la ventana
texto.pack()
IngresoNombre.pack()
contraseña.pack()
IngresoContraseña.pack()
BotonIngreso.pack()

#sin esto la ventana se cierra altiro
ventana.mainloop()