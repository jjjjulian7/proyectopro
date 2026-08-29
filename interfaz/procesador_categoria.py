import tkinter as tk
from . import gestor_imagenes 

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
    contenedor_principal = tk.Frame(ventana)
    contenedor_principal.grid(row=1, column=0, sticky="nsew")

    contenedor_principal.grid_rowconfigure(0, weight=1)
    contenedor_principal.grid_columnconfigure(0, weight=1)

    # Crear el Canvas
    canvas = tk.Canvas(contenedor_principal, bg="#f4f4f4", highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")

    # Crear el Scrollbar
    scrollbar = tk.Scrollbar(contenedor_principal, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")

    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame interior donde irán tus productos
    frame_interior = tk.Frame(canvas, bg="#f4f4f4")
    id_ventana = canvas.create_window((0, 0), window=frame_interior, anchor="nw")

    # Funciones clave para el Scroll y el Ancho
    def configurar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def ajustar_ancho_frame(event):
        canvas.itemconfig(id_ventana, width=event.width)

    # Conectar los eventos
    frame_interior.bind("<Configure>", configurar_scroll)
    canvas.bind("<Configure>", ajustar_ancho_frame)

    # OJO: Se elimina ventana.mainloop() porque Toplevel no lo necesita.