
import tkinter as tk
from tkinter import messagebox
from clases.usuario import usuario
from clases.producto import Producto
from clases.inventario import Inventario as I
from clases.carrito import Carrito as C
from datos import bd_usuarios as BD
from datos import bd 
from . import Interfaz_pagina
from . import ventana_admin
from . import interfaz
from . import abrir_carrito
from . import Client_ProyProgV2
import Server_ProgProyV2
import threading
# Codigo realizado por Cristobal Maulen
carrito = C()
inventario=I()
usuario_actual = None
def ventana_a(ventana):
    ventana_admin.ejecutar()
    #Server_ProgProyV2.handle_client()
    ventana.iconify()
def ventana_usuario(ventana,texto,IngresoClave):
        global usuario_actual   # Usamos global para que la variable cambie fuera de la funcion
        Nombre=texto.get()
        contraseña=IngresoClave.get()
        resultado=BD.buscar_usuario(Nombre)
        if resultado==None:
            ventanaAdvertencia=tk.Toplevel(ventana)
            ventanaAdvertencia.geometry("200x60")
            texto=tk.Label(ventanaAdvertencia,text="El usuario no existe")
            texto.pack()
            ventanaAdvertencia.after(3000,ventanaAdvertencia.destroy)
        elif contraseña!=resultado[2]:
            ventanaAdvertencia=tk.Toplevel(ventana)
            ventanaAdvertencia.geometry("200x60")
            texto=tk.Label(ventanaAdvertencia,text="El usuario y/o la contraseña es incorrecta")
            texto.pack()
            ventanaAdvertencia.after(2000,ventanaAdvertencia.destroy)
        else:
            hilo_cliente = threading.Thread(target=Client_ProyProgV2.start_client)
            hilo_cliente.daemon = True
            hilo_cliente.start()
            
            usuario_actual = resultado[1] 
            ventana.destroy()
           

def hay_usuario_autenticado():
    return usuario_actual is not None      

def validar_sesion():
    if not hay_usuario_autenticado():       # Si no se ha iniciado sesion, imprimira el mensaje y bloqueara la funcion de añadir al carrito 
        messagebox.showwarning(
            "Inicio de sesión requerido",
            "Debes iniciar sesión antes de agregar artículos al carrito."
        )
        return False
    return True

def cerrar_sesion():        # AVISO: Falta implementar la funcion. Aun hay q agregar boton de cerrar sesion!
    global usuario_actual
    usuario_actual = None
        
        
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
         texto=tk.Label(ventanaAdvertencia,text="El usuario ya existe")
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



def agregar_producto_carrito(ProductoS, cantidad):
    carrito.agregar_producto(ProductoS,cantidad)


def vaciarcarrito(ventana):
    carrito.vaciar_carrito()
    tk.messagebox.showinfo("Carrito", "El carrito ha sido vaciado.")
    ventana.destroy()
    abrir_carrito.abrir_carrito()
def mostrar_info():
    subtotal= carrito.calcular_subtotal()
    iva = carrito.calcular_iva()
    total= carrito.calcular_total()
    return subtotal,iva,total
def eliminar_producto(ventana, i):
    ventana_cantidad = tk.Toplevel(ventana)
    ventana_cantidad.title("Carrito")
    ventana_cantidad.geometry("300x160")
    ventana_cantidad.grab_set()

    tk.Label(ventana_cantidad, text="CANTIDAD:").pack(pady=5)
    cantidad = tk.Entry(ventana_cantidad)
    cantidad.pack(pady=5)
    cantidad.focus()

    def eliminar():
        cant = cantidad.get()
        if cant.isdigit():
  
            carrito.eliminar_producto(i, int(cant))
            ventana_cantidad.destroy()
        else:
            print("Ingrese una cantidad válida")

    btn_confirmar = tk.Button(ventana_cantidad, text="Aceptar", command=eliminar)
    btn_confirmar.pack(pady=10)


    ventana.wait_window(ventana_cantidad)