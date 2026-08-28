#funciones a completar despues con sqlite3
import sqlite3
import tkinter as tk
from clases.usuario import usuario
from clases.producto import Producto
from clases.inventario import Inventario as I
from datos import bd_usuarios as BD
from datos import bd 
from . import Interfaz_pagina
from . import Ventana_admin
# Codigo realizado por Cristobal Maulen

inventario=I()
def ventana_a(ventana):
    Ventana_admin.ejecutar()
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

def mostrar_productos(Frame_productos):
    for widget in Frame_productos.winfo_children():
        widget.destroy()
    productos = bd.mostrar_productos()
    # Muestra los productos en la bd
    for producto in productos:
        tk.Label(Frame_productos,text=f"ID: {producto[0]} | Nombre: {producto[1]} | Precio: ${producto[2]} | Stock: {producto[3]} | Categoría: {producto[4]}").pack(anchor="w")

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