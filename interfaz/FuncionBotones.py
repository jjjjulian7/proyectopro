
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
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
from . import Client_ProyProgV2 as ClienteRed
import Server_ProgProyV2 as ServidorRed
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
            hilo_cliente = threading.Thread(target=ClienteRed.conectar)
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
        tabla.tag_configure("sin_stock", foreground="#e8283c")

        def al_hacer_click(event):
            if tabla.identify_region(event.x, event.y) != "cell":
                return  # Si no se hizo click en una celda, no hacemos nada

            fila = tabla.identify_row(event.y)  #iid de la fila = ID del producto
            columna = tabla.identify_column(event.x)  # "#6" = editar y "#7" = borrar
            if not fila:
                return  # Si no se hizo click en una fila, no hacemos nada

            id_producto = int(fila) # convertimos el iid a int

            if columna == "#6":  # columna editar
                if hasattr(Frame_productos, "al_editar"):
                    Frame_productos.al_editar(id_producto)
                
            elif columna == "#7":  # columna borrar
                producto = inventario.buscar_producto(1, id_producto) 
                nombre = producto.nombre if producto else id_producto 

                if messagebox.askyesno("Confirmación", f"¿Eliminar '{nombre}'?"):
                    inventario.quitar_producto(id_producto)     # Borra de la BD y de la memoria 
                    mostrar_productos(Frame_productos)          # Volvemos a dibujar la tabla actualizada
 
        tabla.bind("<Button-1>", al_hacer_click)    # Conectamos el click izquierdo con la funcion de arriba

        # --- Implementacion del scrollbar
        # command=tabla.yview      -> al mover la barra, la tabla se desplaza
        # yscrollcommand   -> al desplazar la tabla con la rueda del mouse, la barra se mueve
        scroll = ttk.Scrollbar(Frame_productos, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)
        # Asignamos el orden en el frame, la barra del scroll a la derecha y la tabla a la izquierda
        scroll.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)
        Frame_productos.tabla = tabla

    tabla = Frame_productos.tabla
    tabla.delete(*tabla.get_children())

    # enumerate() entrega (posicion, elemento)
    # usamos la posicion para saber si la fila es par o impar
    for i, producto in enumerate(bd.mostrar_productos()):
        etiquetas = ["par" if i % 2 == 0 else "impar"]       # lista con la etiqueta de fondo 
        
        if int(producto[3]) == 0:
            etiquetas.append("sin_stock")

        tabla.insert("", "end", iid=str(producto[0]), values=producto + (ICONO_EDITAR, ICONO_BORRAR), tags=tuple(etiquetas))   # tags debe ser una tupla


def guardar_producto(id_producto, nombre, precio, stock, categoria, Frame_productos):
    """
        Sirve para agregar y modificar los productos en la pestaña admin
        id_producto = None ; se agregara un producto
        id_producto = 5    ; se modifica producto con id 5 
    """
    precio_num = float(precio.get())        # Pasamos precio y stock a numeros
    stock_num = int(stock.get())

    if stock_num < 0:                       # Validamos que el stock sea correcto
        messagebox.showwarning("Stock incorrecto", "El stock no puede ser negativo ")
        return False

    # Parte donde se registra un nuevo producto y se lo pasamos al inventario
    if id_producto is None:
        ok = inventario.agregar_producto(       
            Producto(nombre.get(), precio_num, stock_num, categoria.get())
        )
        mensaje = "Revisa que no haya campos vacios."
    # Parte donde se edita un producto ya existente, se busca por el id y le cambia los datos
    else:
        ok = inventario.actualizar_producto(
            id_producto, nombre.get(), precio_num, stock_num, categoria.get()
        )
        mensaje = "Producto no encontrado"

        # agregar_producto y actualizar_producto devuelven False si las validacion falla
        # si ok = False, da mensaje de error y usamos el mensaje de su seccion respectiva
    if not ok:
        messagebox.showwarning("Error", mensaje)
        return False

    mostrar_productos(Frame_productos)
    return True


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
    hilo_server = threading.Thread(target= ServidorRed.iniciar_servidor)
    hilo_server.daemon = True
    hilo_server.start()
    if usuario==None:
        interfaz.ejecutar()
    else:
        
        return usuario



def agregar_producto_carrito(ProductoS, cantidad):
    carrito.agregar_producto(ProductoS,cantidad)


def vaciarcarrito():
    carrito.vaciar_carrito()
    
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