import tkinter as tk

def crear_boton_verde(ventana_padre, texto_boton, funcion_comando):
    """
    funcion solo de estetica del boton
    """
    boton = tk.Button(ventana_padre, 
                      text=texto_boton, 
                      font=("Arial", 12, "bold"),
                      bg="#2ecc71",      
                      fg="white",         
                      relief="flat",      #Sin bordes feos
                      borderwidth=0,      
                      padx=20,            
                      pady=10,            
                      cursor="hand2",
                      command=funcion_comando) #conecta la acción
    
    def al_entrar(e):
        boton.config(bg="#27ae60")

    def al_salir(e):
        boton.config(bg="#2ecc71") #Vuelve al verde claro

    boton.bind("<Enter>", al_entrar)
    boton.bind("<Leave>", al_salir)
    
    # Devolvemos el botón ya listo para llamarlo en la iunterfaz
    return boton