import tkinter as tk

ventana=tk.Tk()
ventana.title("MauelncitosMarket")
ventana.geometry("300x350")

texto=tk.Label(ventana,text="Nombre Usuario")
IngresoNombre=tk.Entry(ventana)

texto.pack()
IngresoNombre.pack()
ventana.mainloop()