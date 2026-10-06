#funciones a completar despues con sqlite3
import sqlite3
import tkinter as tk
from clases.usuario import usuario
from clases.producto import Producto
from clases.inventario import Inventario as I
from datos import bd_usuarios as BD
from datos import bd 
from . import Interfaz_pagina
from . import ventana_admin
<<<<<<< Updated upstream
from . import procesador_categoria
from . import Mouses_categoria
from . import Ram_categoria
from . import Monitores_categoria
from . import Teclados_categora
=======
from . import interfaz
from . import abrir_carrito
from . import Client_ProyProgV2
import Server_ProgProyV2
import threading
from tkinter import ttk
>>>>>>> Stashed changes
# Codigo realizado por Cristobal Maulen

inventario=I()
def ventana_a(ventana):
    ventana_admin.ejecutar()
    ventana.iconify()
def ventana_usuario(ventana,texto,IngresoClave):
        Nombre=texto.get()
        contraseña=IngresoClave.get()
        resultado=BD.buscar_usuario(Nombre)
        if resultado==None:
            ventanaAdvertencia=tk.Toplevel(ventana)
            ventanaAdvertencia.geometry("200x60")
            texto=tk.Label(ventanaAdvertencia,text="EL usuario no existe")
            texto.pack()
            ventanaAdvertencia.after(3000,ventanaAdvertencia.destroy)
        elif contraseña!=resultado[2]:
            ventanaAdvertencia=tk.Toplevel(ventana)
            ventanaAdvertencia.geometry("200x60")
            texto=tk.Label(ventanaAdvertencia,text="la contraseña es incorrecta")
            texto.pack()
            ventanaAdvertencia.after(2000,ventanaAdvertencia.destroy)
        else:
            Interfaz_pagina.ejecutar(ventana)
        
def registro(texto,IngresoClave,ventana):
    Texto=texto.get()
    Clave=IngresoClave.get()
    resultado=BD.buscar_usuario(Texto)
    if resultado==None:
        nuevo_usuario=usuario(Texto,Clave)
        BD.insertar_usuario(nuevo_usuario)
    else:
         ventanaAdvertencia=tk.Toplevel(ventana)
         ventanaAdvertencia.geometry("50x50")
         texto=tk.Label(ventanaAdvertencia,text="EL usuario ya existe")
         texto.pack()
         ventanaAdvertencia.after(2000,ventanaAdvertencia.destroy)

def mostrar_frame(frame, frames):
    for f in frames:
        f.pack_forget()
    frame.pack(fill="both", expand=True)

def hacer_admin(nombre, rut):
    nombre = nombre.strip()
    rut = rut.strip()

    if not nombre or not rut:
        tk.messagebox.showwarning("Falta información", "Debes completar nombre y RUT.")
        return False

    BD.convertir_en_admin(nombre, rut)
    tk.messagebox.showinfo("Éxito", f"El usuario {nombre} fue convertido a admin.")
    return True

def aplicar_estilo_tabla(widget):
    estilo = ttk.Style(widget)        # objeto que administra los estilos de ttk
    estilo.theme_use("clam")    # este tema nos permite cambiar el color la cabecera

    # Estilo del CUERPO de la tabla
    estilo.configure(
        "Productos.Treeview",
        font=("Segoe UI", 10),      
        rowheight=36,              
        background="#ffffff",       
        fieldbackground="#ffffff",  
        borderwidth=0,              
    )


    #Estilo de CABECERA tabla
    estilo.configure(
        "Productos.Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background="#7422A8",       
        foreground="white",         
        relief="flat",              
        padding=(8, 8),             
    )

 # estilo.map cambia colores según el estado del widget.
    # Por defecto la cabecera cambia de color al pasar el mouse. Aquí lo dejamos igual.
    estilo.map("Productos.Treeview.Heading", background=[("active", "#7422A8")])

    # Color de la fila seleccionada 
    estilo.map(
        "Productos.Treeview",
        background=[("selected", "#e7f5ff")],
        foreground=[("selected", "black")],
    )

ICONO_EDITAR = "↹"
ICONO_BORRAR = "🗑"

def mostrar_productos(Frame_productos):
    # La primera vez creamos la tabla. las siguientes veces solo la rellenamos
    if not hasattr(Frame_productos, "tabla"):
        aplicar_estilo_tabla(Frame_productos)

        columnas = ("id", "nombre", "precio", "stock", "categoria", "editar", "borrar") #asignamos el orden de las columnas
        tabla = ttk.Treeview(
            Frame_productos,
            columns=columnas,
            show="headings",
            style="Productos.Treeview",                  
        )

        # texto, ancho, alineacion de cada columna
        config_columnas = {
            "id":        ("ID", 60, "center"),
            "nombre":    ("NOMBRE", 260, "w"),         # "w" = west = izquierda
            "precio":    ("PRECIO", 110, "e"),         # "e" = east = derecha 
            "stock":     ("STOCK", 80, "center"),
            "categoria": ("CATEGORÍA", 160, "w"),
            "editar":    ("", 50, "center"),
            "borrar":    ("", 50, "center"),
        }
        for col, (texto, ancho, ancla) in config_columnas.items():
            tabla.heading(col, text=texto)                # texto de la cabecera
            tabla.column(col, width=ancho, anchor=ancla)  # ancho y alineación del contenido

        # un tag es una etiqueta que le ponemos a una fila para darle color.
        # Aqui definimos que color tiene cada etiqueta, después las asignamos al insertar.
        tabla.tag_configure("par", background="#ffffff")
        tabla.tag_configure("impar", background="#e0e0e0")

        tabla.pack(fill="both", expand=True)
        Frame_productos.tabla = tabla

    tabla = Frame_productos.tabla
    tabla.delete(*tabla.get_children())

    # enumerate() entrega (posicion, elemento)
    # usamos la posicion para saber si la fila es par o impar
    for i, producto in enumerate(bd.mostrar_productos()):
        etiqueta = "par" if i % 2 == 0 else "impar"       
        tabla.insert("", "end", iid=str(producto[0]), values=producto + (ICONO_EDITAR, ICONO_BORRAR), tags=(etiqueta,))   # tags debe ser una tupla, por eso la coma al final       


def ingresar_producto(nombre,precio,stock,categoria,Frame_productos):
    n=nombre.get()
    p=precio.get()
    s=stock.get()
    c=categoria.get()
    producto=Producto(n,p,s,c)
    inventario.agregar_producto(producto)
    mostrar_productos(Frame_productos)

def borrar(id_producto,Frame_productos):
    i=int(id_producto.get())
    inventario.quitar_producto(i)    
    mostrar_productos(Frame_productos)

def actualizar_producto(id_N,Nombre,Precio,Stock,Categoria,Frame_productos):
    i=int(id_N.get())
    nombre=Nombre.get()
    precio=Precio.get()
    stock=Stock.get()
    categoria=Categoria.get()
    p=Producto(i,nombre,precio,stock,categoria)
    inventario.actualizar_producto(p)
    mostrar_productos(Frame_productos)

def buscar(buscador, inventario_productos):
    valor = buscador.get()
    return inventario_productos.buscar_producto(2, valor)


def categoria_procesadores():
    procesador_categoria.ejecutar()
def categoria_Mouses():
    Mouses_categoria.ejecutar()
def categoria_Ram():
    Ram_categoria.ejecutar()
def categoria_Monitores():
    Monitores_categoria.ejecutar()
def categoria_Teclados():
    Teclados_categora.ejecutar()