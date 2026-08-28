import tkinter as tk
from . import FuncionBotones as F
from datos import bd
def ejecutar():
    ventana = tk.Tk()
    ventana.title("MaulencitosMarketADMIN")
    ventana.geometry("1280x720")

    #frames padres
    Frame_botones=tk.Frame(ventana)
    Frame_contenido=tk.Frame(ventana)
    Frame_botones.pack()
    Frame_contenido.pack(fill="both", expand=True)
    Frame_producto=tk.Frame(ventana)
    Frame_producto.pack(fill="both", expand=True)

    #Frae hijos de Frame contenido
    Frame_ingreso=tk.Frame(Frame_contenido)
    Frame_borrar=tk.Frame(Frame_contenido)
    lista_F=[Frame_ingreso,Frame_borrar]#esto es para que le pasemos los frame a la funcion mostrar frame asi los va a poder ocultar y mostrar el contenido que elija el usuario

    #botones
    boton_ingreso=tk.Button(Frame_botones,text="ingresar producto",command=lambda:F.mostrar_frame(Frame_ingreso,lista_F))
    boton_borrar=tk.Button(Frame_botones,text="Eliminar producto",command=lambda:F.mostrar_frame(Frame_borrar,lista_F))
    boton_ingreso.grid(column=1,row=1)
    boton_borrar.grid(column=2,row=1)

    #frame_ingreso
    tk.Label(Frame_ingreso,text="ingrese nombre").grid(row=1,column=1)
    tk.Label(Frame_ingreso,text="precio").grid(row=2,column=1)
    tk.Label(Frame_ingreso,text="stock").grid(row=3,column=1)
    tk.Label(Frame_ingreso,text="categoria").grid(row=4,column=1)
    nombre=tk.Entry(Frame_ingreso)
    precio=tk.Entry(Frame_ingreso)
    stock=tk.Entry(Frame_ingreso)
    categoria=tk.Entry(Frame_ingreso)
    boton=tk.Button(Frame_ingreso,text="ingresar",command=lambda:F.ingresar_producto(nombre,precio,stock,categoria,Frame_producto))
    nombre.grid(row=1,column=2)
    precio.grid(row=2,column=2)
    stock.grid(row=3,column=2)
    categoria.grid(row=4,column=2)
    boton.grid(row=5,column=1)

    #frame borrar
    tk.Label(Frame_borrar,text="ingrese id del producto a borrar").grid(row=1,column=1)
    id_producto=tk.Entry(Frame_borrar)
    botonB=tk.Button(Frame_borrar,text="BORRAR",command=lambda:F.borrar(id_producto,Frame_producto))
    id_producto.grid(row=1,column=2)
    botonB.grid(row=2,column=1)

    #frame de los productos
    F.mostrar_productos(Frame_producto)