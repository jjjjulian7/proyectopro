import tkinter as tk
from . import FuncionBotones as F
from clases.inventario import Inventario
from clases.producto import Producto
from datos import bd
def crear_cuadradito(contenedor_padre, gestor, ruta_imagen, nombre, categoria, precio,stock,id_producto):
    marco = tk.Frame(contenedor_padre, bg="white", bd=1, relief="solid", padx=15, pady=15)
    
    img = gestor.cargar_foto(ruta_imagen)
    lbl_imagen = tk.Label(marco, image=img, bg="white")
    lbl_imagen.image = img
    lbl_imagen.pack(pady=(0, 10))
    
    lbl_nombre = tk.Label(marco, text=nombre, font=("Arial", 12, "bold"), bg="white", fg="#1a1a1a")
    lbl_nombre.pack()
    
    lbl_categoria = tk.Label(marco, text=categoria, font=("Arial", 10), bg="white", fg="#7a7a7a")
    lbl_categoria.pack(pady=(0, 10))
    
    lbl_precio = tk.Label(marco, text=f"${precio:,.0f}".replace(",", "."), font=("Arial", 14, "bold"), bg="white", fg="#4a2a85")
    lbl_precio.pack(pady=(5, 5))
    
    lbl_stock = tk.Label(marco, text="En stock", font=("Arial", 10), bg="white", fg="#2a8c4a")
    lbl_stock.pack(pady=(0, 15))

    stok = tk.Entry(marco, width=5, justify="center")
    stok.insert(0, "1")#coloca como predeterminado 1 producto en el stock
    stok.pack(pady=(0, 10))

    stock_actual = stock

    def agregar_carrito():
        nonlocal stock_actual
        if not F.validar_sesion():      #Si no hay sesion iniciada, no permite agregar cosas al carrito
            return

        cantidad_texto = stok.get()

        if not cantidad_texto.isdigit() or int(cantidad_texto) <= 0:
            tk.messagebox.showerror("Error", "Ingresa una cantidad válida")
            return

        cantidad = int(cantidad_texto)
        nuevo_stock = stock_actual - cantidad

        if not Inventario().validar_stock(nuevo_stock):
            tk.messagebox.showerror("Error", "No hay stock suficiente")
            return
        producto_seleccionado = Producto(nombre, precio, nuevo_stock, categoria)
        producto_seleccionado.id = id_producto
        bd.actualizar_producto(producto_seleccionado)
        F.agregar_producto_carrito(producto_seleccionado, cantidad)

        stock_actual = nuevo_stock
        lbl_stock.config(text=f"Stock: {stock_actual}")

    boton_agregar = tk.Button(marco, text="agregar al carrito", font=("Arial", 10, "bold"), 
                        bg="white", fg="#4a2a85", bd=1, relief="solid", cursor="hand2",
                        command=agregar_carrito)
    boton_agregar.pack(fill="x", padx=10) 
    return marco