import tkinter as tk
from . import gestor_imagenes 
from . import estilo_boton as et
from . import FuncionBotones as F
from . import procesador_categoria
from datos import bd
from clases import inventario

def ejecutar():
    # 1. Usar Toplevel() porque es una ventana secundaria
    ventana = tk.Toplevel()
    ventana.title("Procesadores - MaulencitosMarket")
    ventana.geometry("1280x700")

    # Configuración de las ventanas
    ventana.grid_columnconfigure(0, weight=1)
    ventana.grid_rowconfigure(1, weight=1)

    # BARRA SUPERIOR (Fila 0)
    barra = tk.Frame(ventana, background="#7422A8", height=80)
    barra.grid(row=0, column=0, sticky="ew")
    barra.grid_propagate(False)

    # Configuración de las 3 columnas DENTRO de la barra
    barra.grid_columnconfigure(0, weight=0, minsize=300) 
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

    # Contenedor Derecho (Usuario y Carrito)
    frame_derecho = tk.Frame(barra, background="#7422A8")
    frame_derecho.grid(row=0, column=2, padx=(0, 100), pady=20, sticky="e")

    # Icono Usuario (CORREGIDO: Padre es frame_derecho)
    img_usuario = gestor_imagenes.cargar_foto("usuario_icono")
    lbl_usuario = tk.Label(frame_derecho, image=img_usuario, background="#7422A8")
    lbl_usuario.image = img_usuario
    lbl_usuario.grid(row=0, column=0, padx=10)

    separador = tk.Frame(frame_derecho, bg="white", width=1, height=30)
    separador.grid(row=0, column=1, padx=15)

    # Icono Carrito (CORREGIDO: Padre es frame_derecho)
    img_carrito = gestor_imagenes.cargar_foto("carrito_icono")
    lbl_carrito = tk.Label(frame_derecho, image=img_carrito, background="#7422A8")
    lbl_carrito.image = img_carrito
    lbl_carrito.grid(row=0, column=2, padx=10)


    # CONTENEDOR PRINCIPAL (Fila 1)
    contenido = tk.Frame(ventana, bg="#F7F7F7")
    contenido.grid(row=1, column=0, sticky="nsew")

    #frame filrar
    frame_filtrar=tk.Frame(contenido,width=180,bg="#E0E0E0")
    frame_filtrar.pack(side="left",fill="y",padx=15,pady=15)
    frame_filtrar.pack_propagate(False)#para que no se reduzca

    et.titulo(frame_filtrar,"categorias").grid(row=1,column=1)

    Mouse=tk.Label(frame_filtrar,text="Mouses",cursor="hand2")
    Monitores=tk.Label(frame_filtrar,text="Monitores",cursor="hand2")
    teclados=tk.Label(frame_filtrar,text="teclados",cursor="hand2")
    Ram=tk.Label(frame_filtrar,text="Ram",cursor="hand2")
    procesadores=tk.Label(frame_filtrar,text="procesadores",cursor="hand2")
    
    #cuando se haga click se ejecutara la opcion de filtrado
    Mouse.bind("<Button-1>",lambda event:F.categoria_Mouses())
    Monitores.bind("<Button-1>", lambda event:F.categoria_Monitores())
    teclados.bind("<Button-1>", lambda event:F.categoria_Teclados())
    Ram.bind("<Button-1>", lambda event:F.categoria_Ram())
    procesadores.bind("<Button-1>", lambda event: F.categoria_procesadores)
    
    #posicionamiento
    Mouse.grid(row=2,column=1,sticky="w", pady=5, padx=10)
    Monitores.grid(row=3,column=1,sticky="w", pady=5, padx=10)
    teclados.grid(row=4,column=1,sticky="w", pady=5, padx=10)
    Ram.grid(row=5,column=1,sticky="w", pady=5, padx=10)
    procesadores.grid(row=6,column=1,sticky="w", pady=5, padx=10)


    # CONTENEDOR DE LOS PRODUCTOS
    contenedor_principal = tk.Frame(contenido, bg="#F7F7F7")
    contenedor_principal.pack(side="left",fill="both",expand=True,padx=(0, 15),pady=15)
    contenedor_principal.grid_rowconfigure(0, weight=1)
    contenedor_principal.grid_columnconfigure(0, weight=1)

    # Crear el Canvas
    canvas = tk.Canvas(contenedor_principal,bg="#f4f4f4",highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")

    # Crear el Scrollbar
    scrollbar = tk.Scrollbar(
    contenedor_principal,orient="vertical",command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")

    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame interior donde irán tus productos
    frame_interior = tk.Frame(canvas, bg="#f4f4f4")

    id_ventana = canvas.create_window((0, 0),window=frame_interior,anchor="nw")

    # Funciones clave para el Scroll y el Ancho
    def configurar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def ajustar_ancho_frame(event):
        canvas.itemconfig(id_ventana, width=event.width)

    # Conectar los eventos
    frame_interior.bind("<Configure>", configurar_scroll)
    canvas.bind("<Configure>", ajustar_ancho_frame)


#frame donde se iran guardando los productos

    productos_buscados = None
    inventario_productos = inventario.Inventario()

    def mostrar_productos():
        for widget in frame_interior.winfo_children():
            widget.destroy()

        for columna in range(4):
            frame_interior.grid_columnconfigure(columna, weight=1)

        if productos_buscados is None:
            productos=bd.filtrar_categoria("Procesadores")

            for i, producto in enumerate(productos):
                fila = i // 4
                columna = i % 4
                frameProducto = tk.Frame(frame_interior,width=180,height=220,borderwidth=1,relief="solid")
                frameProducto.grid(row=fila,column=columna,padx=10,pady=10,sticky="nsew")
                tk.Label(frameProducto,text=producto[1]).pack()
                tk.Label(frameProducto,text=f"Precio: ${producto[2]}").pack()
                tk.Label(frameProducto,text=f"Stock: {producto[3]}").pack()
                tk.Label(frameProducto,text=f"Categoría: {producto[4]}").pack()

        else:
            productos=productos_buscados

            for i, producto in enumerate(productos):
                fila = i // 4
                columna = i % 4
                frameProducto = tk.Frame(frame_interior,width=180,height=220,borderwidth=1,relief="solid")
                frameProducto.grid(row=fila,column=columna,padx=10,pady=10,sticky="nsew")
                tk.Label(frameProducto,text=producto.nombre).pack()
                tk.Label(frameProducto,text=f"Precio: ${producto.precio}").pack()
                tk.Label(frameProducto,text=f"Stock: {producto.stock}").pack()
                tk.Label(frameProducto,text=f"Categoría: {producto.categoria}").pack()

    def buscar_enter(event):
        nonlocal productos_buscados
        productos_buscados = F.buscar(buscador, inventario_productos)
        mostrar_productos()

    buscador.bind("<Return>", buscar_enter)

    mostrar_productos()