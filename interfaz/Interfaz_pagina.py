import tkinter as tk
from . import FuncionBotones as F
from datos import bd as bd
def ejecutar(ventana_log):
    #CODIGO CREADO ´POR JOSE COFRE 25/08
    ventana = tk.Tk()
    ventana.title("Pagina principal")
    ventana.geometry("1280x720")

    # BARRA SUPERIOR
    barra = tk.Frame(ventana, background="#7422A8")
    barra.pack(side="top", fill="x")
    buscador = tk.Entry(barra)
    buscador.pack(side="left", padx=10, pady=10)
    botonB = tk.Button(barra,text="buscar",command=lambda: F.buscarr_producto(2, buscador))
    botonB.pack(side="left", padx=10)
#creamos un Frame principal que contendrá el Canvas y el Scrollbar
    contenedor_principal = tk.Frame(ventana)
    contenedor_principal.pack(fill="both", expand=True)
    #Crear el Canvas
    canvas = tk.Canvas(contenedor_principal)
    canvas.pack(side="left", fill="both", expand=True)

#Crear el Scrollbar y conectarlo al Canvas
    scrollbar = tk.Scrollbar(contenedor_principal, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    #Crear el Frame interior que realmente contendrá tus widgets
    frame_interior = tk.Frame(canvas)

# Colocar el frame_interior dentro del Canvas
    canvas.create_window((0, 0), window=frame_interior, anchor="nw")

    #le dice al Canvas cuánto puede bajar basándose en el tamaño del frame_interior
    def actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame_interior.bind("<Configure>", actualizar_scroll)
#frame donde se iran guardando los productos
    productos=bd.mostrar_productos()
    for i, producto in enumerate(productos):
        fila = i // 3
        columna = i % 3
        frameProducto = tk.Frame(frame_interior,borderwidth=1,relief="solid")
        frameProducto.grid(row=fila,column=columna,padx=15,pady=15)
        tk.Label(frameProducto,text=producto[1]).pack()
        tk.Label(frameProducto,text=f"Precio: ${producto[2]}").pack()
        tk.Label(frameProducto,text=f"Stock: {producto[3]}").pack()
        tk.Label(frameProducto,text=f"Categoría: {producto[4]}").pack() 