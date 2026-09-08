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
# Codigo realizado por Cristobal Maulen
carrito = []
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
    try:
        i = int(id_N.get())
        precio = float(Precio.get())
        stock = int(Stock.get())
    except ValueError:
        tk.messagebox.showwarning("Datos inválidos", "ID, precio y stock deben ser numéricos.")
        return

    if stock < 0:       # Validacion para que el stock no sea negativo
        tk.messagebox.showwarning(
            "Stock inválido",
            "El stock no puede ser negativo."
        )
        return

    actualizado = inventario.actualizar_producto(
        i, Nombre.get(), precio, stock, Categoria.get()
    )
    if not actualizado:
        tk.messagebox.showwarning("Producto no encontrado", "No existe un producto con ese ID.")
        return

    mostrar_productos(Frame_productos)


def cargar_producto(id_N, Nombre, Precio, Stock, Categoria):
    """Carga los datos del producto cuyo ID está escrito en el formulario."""
    try:
        id_producto = int(id_N.get())
    except ValueError:
        return

    producto = inventario.buscar_producto(1, id_producto)
    if producto is None:
        return

    campos = (
        (Nombre, producto.nombre),
        (Precio, producto.precio),
        (Stock, producto.stock),
        (Categoria, producto.categoria),
    )
    for campo, valor in campos:
        campo.delete(0, tk.END)
        campo.insert(0, str(valor))

def mostrar_estadisticas(selector_categoria, etiqueta_resultado):
    categoria = selector_categoria.get().strip()

    if not categoria:
        etiqueta_resultado.config(text="Selecciona una categoría.")
        return

    promedio = bd.promedio_precio_categoria(categoria)
    producto = bd.menor_stock(categoria)

    if promedio is None or producto is None:
        etiqueta_resultado.config(
            text="No hay productos registrados en esta categoría."
        )
        return

    etiqueta_resultado.config(
        text=(
            f"Precio promedio: ${promedio:,.0f}\n"
            f"Producto con menor stock: {producto[1]}\n"
            f"Stock disponible: {producto[3]} unidades"
        )
    )

def mostrar_total_inventario(etiqueta_resultado):
    total = bd.calcular_total_inventario()
    etiqueta_resultado.config(
        text=f"Valor total del inventario: ${total:,.0f}"
    )

def buscar(buscador, inventario_productos):
    valor = buscador.get()
    return inventario_productos.buscar_producto(2, valor)



def ingresar_log(usuario):
    if usuario==None:
        interfaz.ejecutar()
    else:
        
        return usuario



def agregar_producto_carrito(nombre, categoria, precio, cantidad):
    carrito.append({"nombre": nombre, "categoria": categoria, "precio": precio, "cantidad": cantidad})

def calcular_total():
    total = 0
    for item in carrito:
        total += item["precio"] * item["cantidad"]
    return total