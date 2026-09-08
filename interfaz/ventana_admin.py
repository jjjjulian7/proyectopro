import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
from . import FuncionBotones as F
from datos import bd
from datos import bd_usuarios as BD

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
    Frame_actualizar=tk.Frame(Frame_contenido)
    Frame_estadisticas=tk.Frame(Frame_contenido)
    lista_F=[Frame_ingreso,Frame_borrar,Frame_actualizar,Frame_estadisticas]#esto es para que le pasemos los frame a la funcion mostrar frame asi los va a poder ocultar y mostrar el contenido que elija el usuario

    #botones
    boton_ingreso=tk.Button(Frame_botones,text="Ingresar producto",command=lambda:mostrar_seccion(Frame_ingreso))
    boton_borrar=tk.Button(Frame_botones,text="Eliminar producto",command=lambda:mostrar_seccion(Frame_borrar))
    boton_actualizar=tk.Button(Frame_botones,text="Modificar producto",command=lambda:mostrar_seccion(Frame_actualizar))
    boton_estadisticas=tk.Button(Frame_botones,text="Estadísticas",command=lambda:mostrar_seccion(Frame_estadisticas))
    boton_ingreso.grid(column=1,row=1)
    boton_borrar.grid(column=2,row=1)
    boton_actualizar.grid(column=3,row=1)
    boton_estadisticas.grid(column=4,row=1)

    #boton para asignar permisos de admin
    frame_admin = tk.Frame(Frame_botones)
    frame_admin.grid(row=1, column=5, padx=(80, 0), pady=10, sticky="w")
    frame_admin.grid_remove()

    def mostrar_admin_fields():
        frame_admin.grid()

    def mostrar_seccion(frame):
        frame_admin.grid_remove()
        F.mostrar_frame(frame, lista_F)

    boton_admin = tk.Button(Frame_botones, text="Hacer admin", command=mostrar_admin_fields)
    boton_admin.grid(row=1, column=5, padx=(40, 0), pady=10, sticky="w")

    #frame_ingreso
    tk.Label(Frame_ingreso,text="Ingrese nombre").grid(row=1,column=1)
    tk.Label(Frame_ingreso,text="Precio").grid(row=2,column=1)
    tk.Label(Frame_ingreso,text="Stock").grid(row=3,column=1)
    tk.Label(Frame_ingreso,text="Categoria").grid(row=4,column=1)
    nombre=tk.Entry(Frame_ingreso)
    precio=tk.Entry(Frame_ingreso)
    stock=tk.Entry(Frame_ingreso)
    categoria=tk.Entry(Frame_ingreso)
    boton=tk.Button(Frame_ingreso,text="Ingresar",command=lambda:F.ingresar_producto(nombre,precio,stock,categoria,Frame_producto))
    nombre.grid(row=1,column=2)
    precio.grid(row=2,column=2)
    stock.grid(row=3,column=2)
    categoria.grid(row=4,column=2)
    boton.grid(row=5,column=1)

    #frame borrar
    tk.Label(Frame_borrar,text="Ingrese ID del producto a borrar").grid(row=1,column=1)
    id_producto=tk.Entry(Frame_borrar)
    botonB=tk.Button(Frame_borrar,text="BORRAR",command=lambda:F.borrar(id_producto,Frame_producto))
    id_producto.grid(row=1,column=2)
    botonB.grid(row=2,column=1)

    #frame actualizar producto
    tk.Label(Frame_actualizar,text="Ingrese ID").grid(row=1,column=1)
    tk.Label(Frame_actualizar,text="Ingrese nombre").grid(row=2,column=1)
    tk.Label(Frame_actualizar,text="Stock").grid(row=3,column=1)
    tk.Label(Frame_actualizar,text="Categoria").grid(row=4,column=1)
    tk.Label(Frame_actualizar,text="Precio").grid(row=5,column=1)
    id_N=tk.Entry(Frame_actualizar)
    Nombre=tk.Entry(Frame_actualizar)
    Precio=tk.Entry(Frame_actualizar)
    Stock=tk.Entry(Frame_actualizar)
    Categoria=tk.Entry(Frame_actualizar)
    Boton=tk.Button(Frame_actualizar,text="Ingresar",command=lambda:F.actualizar_producto(id_N,Nombre,Precio,Stock,Categoria,Frame_producto))
    id_N.grid(row=1,column=2)
    Nombre.grid(row=2,column=2)
    Stock.grid(row=3,column=2)
    Categoria.grid(row=4,column=2)
    Precio.grid(row=5,column=2)
    Boton.grid(row=6,column=1)

    cargar_datos = lambda event=None: F.cargar_producto(
        id_N, Nombre, Precio, Stock, Categoria
    )
    id_N.bind("<Return>", cargar_datos)
    id_N.bind("<FocusOut>", cargar_datos)

    # Frame para asignar permisos de administrador
    tk.Label(frame_admin,text="Nombre del usuario a convertir en admin").grid(row=1,column=1)
    entrada_nombre_admin = tk.Entry(frame_admin)
    entrada_nombre_admin.grid(row=2,column=1)

    tk.Label(frame_admin,text="RUT del administrador").grid(row=3,column=1)
    entrada_rut_admin = tk.Entry(frame_admin)
    entrada_rut_admin.grid(row=4,column=1)

    def hacer_admin():
        nombre = entrada_nombre_admin.get().strip()
        rut = entrada_rut_admin.get().strip()

        if not F.hacer_admin(nombre, rut):
            return

        entrada_nombre_admin.delete(0, tk.END)
        entrada_rut_admin.delete(0, tk.END)
        frame_admin.grid_remove()

    boton_hacer_admin = tk.Button(frame_admin, text="Hacer admin", command=hacer_admin)
    boton_hacer_admin.grid(row=5,column=1)

    # Frame de estadísticas por categoría
    tk.Label(Frame_estadisticas, text="Categoría").grid(row=1, column=1, padx=5, pady=5)
    categorias = sorted({producto[4] for producto in bd.mostrar_productos()})
    categoria_estadisticas = tk.StringVar()
    selector_categoria = ttk.Combobox(
        Frame_estadisticas,
        textvariable=categoria_estadisticas,
        values=categorias,
        state="readonly"
    )
    selector_categoria.grid(row=1, column=2, padx=5, pady=5)
    if categorias:
        selector_categoria.current(0)

    resultado_estadisticas = tk.Label(Frame_estadisticas, justify="left")
    resultado_estadisticas.grid(row=3, column=1, columnspan=2, padx=5, pady=10)
    boton_calcular = tk.Button(
        Frame_estadisticas,
        text="Calcular",
        command=lambda: F.mostrar_estadisticas(
            selector_categoria, resultado_estadisticas
        )
    )
    boton_calcular.grid(row=2, column=1, columnspan=2, pady=5)
    boton_total = tk.Button(
        Frame_estadisticas,
        text="Calcular total del inventario",
        command=lambda: F.mostrar_total_inventario(resultado_estadisticas)
    )
    boton_total.grid(row=2, column=3, padx=5, pady=5)

    #frame de los productos
    F.mostrar_productos(Frame_producto)