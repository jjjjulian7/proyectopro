import tkinter as tk
import FuncionBotones as F
def ejecutar(ventana_log):
    #CODIGO CREADO ´POR JOSE COFRE 25/08
    ventana = tk.Tk()
    ventana.title("Pagina principal")
    ventana.geometry("1280x720")

    

    #creamos un Frame principal que contendrá el Canvas y el Scrollbar
    contenedor_principal = tk.Frame(ventana)
    contenedor_principal.pack(fill="both", expand=True)
     #frame 
    barra=tk.Frame(ventana,background='#7422A8')
    buscador=tk.Entry(barra)
    botonB=tk.Button(text='buscar',lambda:F.buscarr_producto(2,buscador))
    tk.
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
#para poder bajar (40)
    for i in range(50):
        etiqueta = tk.Label(frame_interior)
        etiqueta.grid(row=i, column=0, pady=10, padx=20)