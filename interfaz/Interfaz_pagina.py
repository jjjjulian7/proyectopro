import tkinter as tk
from . import FuncionBotones as F
from datos import bd as bd
from . import estilo_boton as et
from . import procesador_categoria
from . import gestor_imagenes 
from clases import inventario 

#colores
gris="#E0E0E0"
blanco="#FFFFFF"
morado="#7422A8"

def ejecutar(ventana_log):

    #CODIGO CREADO ´POR JOSE COFRE 25/08
    ventana = tk.Toplevel()
    ventana.title("Pagina principal")
    ventana.geometry("1280x720")

    # BARRA SUPERIOR
    barra = tk.Frame(ventana,bg="#7422A8", height=60)
    barra.pack(fill="x")

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

    frame_derecho = tk.Frame(barra, bg="#7422A8")
    frame_derecho.grid(row=0, column=2, sticky="e", padx=(0, 100))

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

    #frame general
    contenido=tk.Frame(ventana,bg="#F7F7F7")
    contenido.pack(fill="both", expand=True)

    #frame filtrar
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
    def filtrar_por_categoria(categoria):
        nonlocal productos_buscados
        buscador.delete(0, tk.END)
        buscador.insert(0, categoria)
        productos_buscados = F.buscar(buscador, inventario_productos)
        mostrar_productos()

    Mouse.bind("<Button-1>", lambda event: filtrar_por_categoria("Mouses"))
    Monitores.bind("<Button-1>", lambda event: filtrar_por_categoria("Monitores"))
    teclados.bind("<Button-1>", lambda event: filtrar_por_categoria("Teclados"))
    Ram.bind("<Button-1>", lambda event: filtrar_por_categoria("Ram"))
    procesadores.bind("<Button-1>", lambda event: filtrar_por_categoria("Procesadores"))

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

    def mostrar_productos():
        for widget in frame_interior.winfo_children():
            widget.destroy()

        for columna in range(4):
            frame_interior.grid_columnconfigure(columna, weight=1)

        if productos_buscados is None:
            productos=bd.mostrar_productos()
            for i, producto in enumerate(productos):
                fila = i // 4
                columna = i % 4
                frameProducto = tk.Frame(
                frame_interior,width=180,height=220,borderwidth=1,relief="solid")
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