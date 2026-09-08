import tkinter as tk
# Codigo realizado por Jose Cofre
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
        boton.config(bg="#27ae60") #Cambia a verde oscuro al pasar el mouse por encima

    def al_salir(e):
        boton.config(bg="#2ecc71") #Vuelve al verde claro

    boton.bind("<Enter>", al_entrar) #Al mover el mouse sobre el boton, se activa la funcion al_entrar
    boton.bind("<Leave>", al_salir) #Al mover el mouse fuera del boton, se activa la funcion al_salir
    
    # Devolvemos el botón ya listo para llamarlo en la iunterfaz
    return boton

#Funcion para crear titulo en la interfaz, con un color y fuente especifica
def titulo(ventana,titulo,font= None):
    Titulo=tk.Label(ventana,text=titulo,fg="#7422a8",bg="#dddddd")
    if font:
        Titulo.config(font=font)
    return Titulo