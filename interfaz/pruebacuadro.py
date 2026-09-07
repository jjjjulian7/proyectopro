import tkinter as tk

def crear_cuadradito(contenedor_padre, gestor, ruta_imagen, nombre, categoria, precio):
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
    
    btn_ver = tk.Button(marco, text="Ver producto", font=("Arial", 10, "bold"), 
                        bg="white", fg="#4a2a85", bd=1, relief="solid", cursor="hand2")
    btn_ver.pack(fill="x", padx=10) 
    
    return marco