import tkinter as tk
from . import FuncionBotones as F
from datos import bd as bd
from . import estilo_boton as et
from . import gestor_imagenes 
from . import pruebacuadro
from clases import inventario 
from . import abrir_carrito
from . import interfaz


#colores
gris="#E0E0E0"
blanco="#FFFFFF"
morado="#7422A8"

def ejecutar():

    #CODIGO CREADO ´POR JOSE COFRE 25/08
    ventana = tk.Tk()#crea la ventana
    ventana.title("Pagina principal")
    ventana.geometry("1280x720")

    # BARRA SUPERIOR
    barra = tk.Frame(ventana,bg="#7422A8", height=60)#crea un frame
    barra.pack(fill="x")#lo coloca en la ventana creada y hace que abarque todo el ancho de la ventana

    barra.grid_columnconfigure(0, weight=0, minsize=300)#configura como el tamaño de la columna 0,minsize es para el tamaño minimo y weight
    barra.grid_columnconfigure(1, weight=1)              
    barra.grid_columnconfigure(2, weight=0, minsize=300) 

    # Logo
    imagen_logo = gestor_imagenes.cargar_foto("logo_maulen")
    logo = tk.Label(barra, image=imagen_logo, background="#7422A8")
    logo.image = imagen_logo # TRUCO VITAL: Evita que la foto se ponga blanca
    logo.grid(row=0, column=0, padx=(100, 0), pady=20, sticky="w")

    # Buscador
    buscador = tk.Entry(barra, font=("Arial", 12))
    buscador.grid(row=0, column=1, sticky="ew", ipady=10, pady=18)

    frame_derecho = tk.Frame(barra, bg="#7422A8")
    frame_derecho.grid(row=0, column=2, sticky="e", padx=(0, 100))

    usuario=None

    # Icono Usuario (CORREGIDO: Padre es frame_derecho)
    img_usuario = gestor_imagenes.cargar_foto("usuario_icono")
    lbl_usuario = tk.Label(frame_derecho, image=img_usuario, background="#7422A8",cursor="hand2")
    lbl_usuario.image = img_usuario
    lbl_usuario.grid(row=0, column=0, padx=10)

    lbl_usuario.bind("<Button-1>",lambda event:F.ingresar_log(None))
    
    separador = tk.Frame(frame_derecho, bg="white", width=1, height=30)
    separador.grid(row=0, column=1, padx=15)
    
    # Icono Carrito (CORREGIDO: Padre es frame_derecho)
    img_carrito = gestor_imagenes.cargar_foto("carrito_icono")
    lbl_carrito = tk.Label(frame_derecho, image=img_carrito, background="#7422A8")
    lbl_carrito.image = img_carrito
    lbl_carrito.grid(row=0, column=2, padx=10)
    lbl_carrito.bind("<Button-1>", lambda event: abrir_carrito.abrir_carrito())

    #frame general
    contenido=tk.Frame(ventana,bg="#F7F7F7")
    contenido.pack(fill="both", expand=True)

    #frame filtrar
    frame_filtrar=tk.Frame(contenido,width=180,bg="#dddddd")
    frame_filtrar.pack(side="left",fill="y",padx=15,pady=15)
    frame_filtrar.pack_propagate(False)#para que no se reduzca
    et.titulo(frame_filtrar,"CATEGORÍAS",font=("Segoe UI", 13, "bold")).grid(row=1,column=1, pady = (5, 5))

    # Elementos de filtrado
    Mouse=tk.Label(frame_filtrar,text="Mouse",font=("Segoe UI", 10, "bold"),cursor="hand2", bg="#dddddd")
    Monitores=tk.Label(frame_filtrar,text="Monitores",font=("Segoe UI", 10, "bold"),cursor="hand2", bg="#dddddd")
    teclados=tk.Label(frame_filtrar,text="Teclados",font=("Segoe UI", 10, "bold"),cursor="hand2", bg="#dddddd")
    Ram=tk.Label(frame_filtrar,text="RAM",font=("Segoe UI", 10, "bold"),cursor="hand2", bg="#dddddd")
    procesadores=tk.Label(frame_filtrar,text="Procesadores",font=("Segoe UI", 10, "bold"),cursor="hand2", bg="#dddddd")

 #cuando se haga click se ejecutara la opcion de filtrado
    # Filtrar por precio
    tk.Label(
        frame_filtrar,
        text="PRECIO",
        font=("Segoe UI", 11, "bold"),
        bg="#dddddd",
    ).grid(row=8, column=1, pady=(20, 5), padx=(0,30))

    tk.Label(
        frame_filtrar,
        text="Mínimo",
        bg="#dddddd",
    ).grid(row=9, column=1)

    entry_min = tk.Entry(frame_filtrar, width=12)
    entry_min.grid(row=10, column=1, pady=(0, 8))

    tk.Label(
        frame_filtrar,
        text="Máximo",
        bg="#dddddd",
    ).grid(row=11, column=1)

    entry_max = tk.Entry(frame_filtrar, width=12)
    entry_max.grid(row=12, column=1, pady=(0, 8))

    def aplicar_filtro_precio():
        nonlocal productos_buscados
        min_precio = entry_min.get()
        max_precio = entry_max.get()

        if min_precio and max_precio:
            try:
                min_precio = float(min_precio)
                max_precio = float(max_precio)
                
                filas = bd.filtrar_rango_precios(min_precio, max_precio)
                productos_buscados = []
                for fila in filas:
                    producto = inventario.Producto(fila[1], fila[2], fila[3], fila[4])
                    producto.id = fila[0]
                    productos_buscados.append(producto)
                mostrar_productos()
                                        
            except ValueError:
                tk.messagebox.showerror("Error", "Por favor, ingresa valores numéricos válidos para el precio.")
        else:
            tk.messagebox.showerror("Error", "Por favor, completa ambos campos de precio.")


    boton_filtrar_precio = tk.Button(
        frame_filtrar,
        text="Filtrar precio",
        command=aplicar_filtro_precio
    )

    boton_filtrar_precio.grid(
        row=13,
        column=1,
        pady=5
    )
    
    categorias_labels = [Mouse, Monitores, teclados, Ram ,procesadores]


    def filtrar_por_categoria(categoria, label_seleccionado):
        nonlocal productos_buscados

        for label in categorias_labels:
            label.config(
                fg="black",
                font=("Segoe UI", 10, "bold")
        )

        label_seleccionado.config(
        fg="#7422A8"
        )

        buscador.delete(0, tk.END)
        buscador.insert(0, categoria)
        buscador.config(font=("Segoe UI", 10, "bold"))
        productos_buscados = F.buscar(buscador, inventario_productos)
        mostrar_productos()

    Mouse.bind("<Button-1>", lambda event: filtrar_por_categoria("Mouse", Mouse))#.bind le dice que tiene que ejecutar la funcion cuando le hacen click
    Monitores.bind("<Button-1>", lambda event: filtrar_por_categoria("Monitores", Monitores))
    teclados.bind("<Button-1>", lambda event: filtrar_por_categoria("Teclados", teclados))
    Ram.bind("<Button-1>", lambda event: filtrar_por_categoria("Ram", Ram))
    procesadores.bind("<Button-1>", lambda event: filtrar_por_categoria("Procesadores", procesadores))

    #posicionamiento
    Mouse.grid(row=2,column=1,sticky="w", pady=5, padx=10)
    Monitores.grid(row=3,column=1,sticky="w", pady=5, padx=10)
    teclados.grid(row=4,column=1,sticky="w", pady=5, padx=10)
    Ram.grid(row=5,column=1,sticky="w", pady=5, padx=10)
    procesadores.grid(row=6,column=1,sticky="w", pady=5, padx=10)

#creamos un Frame principal que contendrá el Canvas y el Scrollbar
    contenedor_principal = tk.Frame(contenido,bg="#E0E0E0")
    contenedor_principal.pack(side="left", fill="both", expand=True, padx=(0,15), pady=15)

    #frame del banner
    Frame_banner=tk.Frame(contenedor_principal,bg="#E0E0E0")
    Frame_banner.pack(side="top", fill="x")

    banner1=gestor_imagenes.cargar_foto("banner_principal")
    lbl_banner = tk.Label(Frame_banner, image=banner1, bg="#E0E0E0")
    lbl_banner.image = banner1
    lbl_banner.pack(fill="x")

    #frame que contendrá el Canvas y el Scrollbar
    frame_scroll = tk.Frame(contenedor_principal,bg="#E0E0E0")
    frame_scroll.pack(fill="both", expand=True)

    #Crear el Canvas
    canvas = tk.Canvas(frame_scroll,bg="#F7F7F7", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

#Crear el Scrollbar y conectarlo al Canvas
    scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    #Crear el Frame interior que realmente contendrá tus widgets
    frame_interior = tk.Frame(canvas,bg="#F7F7F7")

# Colocar el frame_interior dentro del Canvas
    ventana_frame = canvas.create_window((0, 0), window=frame_interior, anchor="nw")

    #le dice al Canvas cuánto puede bajar basándose en el tamaño del frame_interior
    def actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame_interior.bind("<Configure>", actualizar_scroll)

    def ajustar_ancho(event):
        canvas.itemconfig(ventana_frame, width=event.width)

    canvas.bind("<Configure>", ajustar_ancho)

#frame donde se iran guardando los productos

    productos_buscados = None
    inventario_productos = inventario.Inventario()

    imagenes_por_categoria = {
        "mouse": "perifericos_categoria",
        "monitores": "monitor_categoria",
        "teclados": "perifericos_categoria",
        "ram": "ram_categoria",
        "procesadores": "procesadores_categoria",
    }

    def obtener_imagen_producto(categoria):
        categoria_normalizada = str(categoria).strip().lower()
        return imagenes_por_categoria.get(categoria_normalizada, "gaming_categoria")

    def mostrar_productos():
        for widget in frame_interior.winfo_children():#junta todos los elementos en frame interior
            widget.destroy()#los va borrando para luego mostrar los demas productos

        for columna in range(4):#este for configura las columnas
            frame_interior.grid_columnconfigure(columna, weight=1)

        if productos_buscados is None:#si la variable de productos_buscados esta vacia va a mostrar todos los productos
            productos = bd.mostrar_productos()#guarda todos los productos en la variable productos, la funcnion bd.mostrar_productos te devuelve una lista de tupla y cada tupla es un producto
            for i, producto in enumerate(productos):# esto recorre la lista  productos y nos entrega i(posicion) y el producto
                fila = i // 4 #es una division entera, no nos va a dar un numero decimal
                columna = i % 4# nos devuelve el resto
                
                id_producto = producto[0]
                nombre = producto[1]
                precio = producto[2]
                stock = producto[3]
                categoria = producto[4]
                ruta_imagen = obtener_imagen_producto(categoria)

                frameProducto = pruebacuadro.crear_cuadradito( #se llama a al funcion que crea el frame donde se muestra el producto
                    contenedor_padre=frame_interior, 
                    gestor=gestor_imagenes, 
                    ruta_imagen=ruta_imagen, 
                    nombre=nombre, 
                    categoria=categoria, 
                    precio=precio,
                    stock=stock,
                    id_producto=id_producto
                )
                frameProducto.grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")#se agrega el frame del producto al frame interior

        else:#este es el caso en que si se este buscando un producto
            productos = productos_buscados
            for i, producto in enumerate(productos):
                fila = i // 4
                columna = i % 4
                
                id_producto = producto.id
                nombre = producto.nombre
                precio = producto.precio
                stock = producto.stock
                categoria = producto.categoria
                
                ruta_imagen = obtener_imagen_producto(categoria)

                frameProducto = pruebacuadro.crear_cuadradito(
                    contenedor_padre=frame_interior, 
                    gestor=gestor_imagenes, 
                    ruta_imagen=ruta_imagen, 
                    nombre=nombre, 
                    categoria=categoria, 
                    precio=precio,
                    stock=stock,
                    id_producto=id_producto
                )
                frameProducto.grid(row=fila, column=columna, padx=10, pady=10, sticky="nsew")

    def buscar_enter(event):
        nonlocal productos_buscados#se modifica la variable que esta afuera  de buscar_enter
        productos_buscados = F.buscar(buscador, inventario_productos)
        mostrar_productos()

    buscador.bind("<Return>", buscar_enter)

    mostrar_productos()

    ventana.mainloop()