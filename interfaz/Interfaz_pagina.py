import tkinter as tk

def ejecutar(ventana_log):
    ventana_log.iconify()
    ventana=                                                                                                                                                                                                                                                                                            tk.Toplevel(ventana_log)
    ventana.geometry("1280x720")
    cabeza=tk.Frame(ventana, bg="#8ADEFF", height=50)
    cabeza.pack(fill="x")
    textoB=tk.Label(cabeza,text="Ingrese nombre del producto: ")
    textoB.grid(row=1,column=2)
    buscar=tk.Entry(cabeza)
    buscar.grid(row=1,column=3)