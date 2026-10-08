import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
from . import FuncionBotones as F
from datos import bd
from datos import bd_usuarios as BD


def ejecutar():
    ventana = tk.Tk()
    ventana.title("MaulencitosMarketADMIN")
    ventana.geometry("1280x720")

    #frames padres
    Frame_botones=tk.Frame(ventana)
    Frame_botones.config(bg="#f1f3f5")
    Frame_contenido=tk.Frame(ventana)
    Frame_botones.grid(row=0, column=0, columnspan=2, sticky="ew")
    Frame_contenido.grid(row=1, column=0, sticky="n", padx=20, pady=20)
    Frame_producto=tk.Frame(ventana)
    Frame_producto.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=20)

    Frame_botones.grid_columnconfigure(0, weight=1)
    Frame_botones.grid_columnconfigure(1, weight=0)
    Frame_botones.grid_columnconfigure(2, weight=0)
    Frame_botones.grid_columnconfigure(3, weight=0)
    Frame_botones.grid_columnconfigure(4, weight=0)
    Frame_botones.grid_columnconfigure(5, weight=0)
    Frame_botones.grid_columnconfigure(6, weight=0)

    #Frae hijos de Frame contenido
    Frame_ingreso=tk.Frame(Frame_contenido)
    Frame_estadisticas=tk.Frame(Frame_contenido)
    lista_F=[Frame_ingreso,Frame_estadisticas]#esto es para que le pasemos los frame a la funcion mostrar frame asi los va a poder ocultar y mostrar el contenido que elija el usuario

    #botones
    boton_ingreso=tk.Button(Frame_botones,text="Ingresar producto",command=lambda:mostrar_seccion(Frame_ingreso))
    boton_estadisticas=tk.Button(Frame_botones,text="Estadísticas",command=lambda:mostrar_seccion(Frame_estadisticas))
    boton_ingreso.grid(column=1,row=1)
    boton_estadisticas.grid(column=4,row=1)

    #boton para asignar permisos de admin
    frame_admin = tk.Frame(Frame_botones)
    frame_admin.grid(row=1, column=5, padx=(20, 0), pady=10, sticky="w")
    frame_admin.grid_remove()

    def mostrar_admin_fields():
        frame_admin.grid()

    def mostrar_seccion(frame):
        frame_admin.grid_remove()
        F.mostrar_frame(frame, lista_F)

    boton_admin = tk.Button(Frame_botones, text="Hacer admin", command=mostrar_admin_fields)
    boton_admin.grid(row=1, column=5, padx=(20, 0), pady=10, sticky="w")

    #frame_ingreso
    titulo_formulario =tk.Label(Frame_ingreso, text="Registrar Producto",
                                bg="#dcdde1", font=("Segoe UI", 12), pady=14)
    titulo_formulario.grid(row=0, column=1, sticky="ew")
    tk.Label(Frame_ingreso,text="Nombre del producto").grid(row=1,column=1, sticky="w")
    tk.Label(Frame_ingreso,text="Precio").grid(row=3,column=1, sticky="w")
    tk.Label(Frame_ingreso,text="Stock").grid(row=5,column=1, sticky="w")
    tk.Label(Frame_ingreso,text="Categoria").grid(row=7,column=1, sticky="w")

    nombre=tk.Entry(Frame_ingreso, width=30,
                    highlightthickness=1,               # Agregamos grosor al borde del boton
                    highlightbackground="#ced4da",    # Color del borde
                    highlightcolor="#0d6efd")         #Color del borde al hacer clic
    precio=tk.Entry(Frame_ingreso, width=30, highlightthickness=1,highlightbackground="#ced4da", highlightcolor="#0d6efd") 
    stock=tk.Entry(Frame_ingreso, width=30, highlightthickness=1,highlightbackground="#ced4da", highlightcolor="#0d6efd") 
    categoria=tk.Entry(Frame_ingreso, width=30, highlightthickness=1,highlightbackground="#ced4da", highlightcolor="#0d6efd") 

    nombre.grid(row=2,column=1, ipady=6)                # ipady = mas alto por dentro
    precio.grid(row=4,column=1, ipady=6)
    stock.grid(row=6,column=1, ipady=6)
    categoria.grid(row=8,column=1, ipady=6)

    id_editando = None # Producto que se esta editando

    def limpiar_formulario():
        nonlocal id_editando        # Con nonlocal editamos la variable desde afura de la funcion
        id_editando = None          # Volvemos al modo registrar producto
        for campo in (nombre, precio, stock, categoria):
            campo.delete(0, tk.END)     # Vaciamos los entry que se hayan asigando antes
        boton.grid_configure(sticky="")
        boton.config(text="Ingresar")   # Devolvemos el boton a su texto original
        boton_cancelar.grid_remove()    # Ocultamos el boton cancelar
        titulo_formulario.config(text="Registro de productos")

    def guardar():
        # Si se guarda el producto correctamente limpiamos el formulario
        # Sino, dejamos lo escrito para que sea correjido
        if F.guardar_producto(id_editando, nombre, precio, stock, categoria, Frame_producto):
            limpiar_formulario()

    def iniciar_edicion(id_producto):
        nonlocal id_editando
        producto = F.inventario.buscar_producto(1, id_producto) # buscamos por id
        if producto is None:
            return
        mostrar_seccion(Frame_ingreso)      # mostramos el formulario
        limpiar_formulario()                # vaciamos si ya habia algo
        id_editando = id_producto          

        for campo, valor in ((nombre, producto.nombre), (precio, producto.precio), (stock, producto.stock), (categoria, producto.categoria)):
            campo.insert(0, str(valor))     # los entry solo aceptan texto, asi que se transforman antes 

        titulo_formulario.config(text=f"Editando producto #{id_producto}")      # Cambiamos el titulo del formulario
        boton.grid_configure(sticky="w")        
        boton.config(text="Guardar")
        boton_cancelar.grid(row=9, column=1,  sticky="e",pady=(16,0))     # mostramos boton cancelar

    boton= tk.Button(Frame_ingreso, text="Ingresar", command=guardar, bg="#0d6efd", fg="white", relief="flat", bd=0, padx=14,pady=6)
    boton_cancelar= tk.Button(Frame_ingreso, text="Cancelar", command=limpiar_formulario, bg="#fd0d0d", fg="white", relief="flat",bd=0, padx=14,pady=6)
    boton.grid(row=9, column=1, pady=((16,0)))

    Frame_producto.al_editar = iniciar_edicion # DEjamos guardada la funcion dentro del Frame de la tabla


    # Frame para asignar permisos de administrador
    tk.Label(frame_admin,text="Nombre del usuario a convertir en admin").grid(row=1,column=1)
    entrada_nombre_admin = tk.Entry(frame_admin)
    entrada_nombre_admin.grid(row=2,column=1)

    tk.Label(frame_admin,text="RUT del administrador").grid(row=3,column=1)
    entrada_rut_admin = tk.Entry(frame_admin)
    entrada_rut_admin.grid(row=4,column=1)

    def hacer_admin():
        nombre = entrada_nombre_admin.get().strip()
        rut = entrada_rut_admin.get().strip()

        if not F.hacer_admin(nombre, rut):
            return

        entrada_nombre_admin.delete(0, tk.END)
        entrada_rut_admin.delete(0, tk.END)
        frame_admin.grid_remove()

    boton_hacer_admin = tk.Button(frame_admin, text="Hacer admin", command=hacer_admin)
    boton_hacer_admin.grid(row=5,column=1)

    # Frame de estadísticas por categoría
    tk.Label(Frame_estadisticas, text="Categoría").grid(row=1, column=1, padx=5, pady=5)
    categorias = sorted({producto[4] for producto in bd.mostrar_productos()})
    categoria_estadisticas = tk.StringVar()
    selector_categoria = ttk.Combobox(
        Frame_estadisticas,
        textvariable=categoria_estadisticas,
        values=categorias,
        state="readonly"
    )
    selector_categoria.grid(row=1, column=2, padx=5, pady=5)
    if categorias:
        selector_categoria.current(0)

    resultado_estadisticas = tk.Label(Frame_estadisticas, justify="left")
    resultado_estadisticas.grid(row=3, column=1, columnspan=2, padx=5, pady=10)
    boton_calcular = tk.Button(
        Frame_estadisticas,
        text="Calcular",
        command=lambda: F.mostrar_estadisticas(
            selector_categoria, resultado_estadisticas
        )
    )
    boton_calcular.grid(row=2, column=1, columnspan=2, pady=5)
    boton_total = tk.Button(
        Frame_estadisticas,
        text="Calcular total del inventario",
        command=lambda: F.mostrar_total_inventario(resultado_estadisticas)
    )
    boton_total.grid(row=2, column=3, padx=5, pady=5)

    # Vaciar inventario:
    TODO = "-- Todo el inventario --"

    selector_vaciar = ttk.Combobox(Frame_botones, state="readonly", width=22)
    selector_vaciar.grid(row=1, column=6, padx=(20, 5), pady=10)

    def actualizar_selector_vaciar():
        # Vuelve a leer las categorías de la BD (así no queda una categoría ya vaciada)
        categorias_bd = sorted({p[4] for p in bd.mostrar_productos() if p[4] and p[4].strip()})
        selector_vaciar["values"] = [TODO] + categorias_bd
        selector_vaciar.current(0)

        # El selector de estadísticas también se actualiza
        selector_categoria["values"] = categorias_bd
        if categorias_bd:
            selector_categoria.current(0)
        else:
            selector_categoria.set("")
        resultado_estadisticas.config(text="")

    def vaciar():
        boton_vaciar.config(state="disabled")       # evita clics repetidos mientras se procesa
        try:
            seleccion = selector_vaciar.get()      

            if not bd.mostrar_productos():
                messagebox.showinfo("Inventario vacío", "No hay productos para vaciar.", parent=ventana)
                return

            if seleccion == TODO:
                texto = "¿Seguro que quieres vaciar todo el inventario? Esta acción eliminará todos los productos."
            else:
                texto = f"¿Seguro que quieres vaciar la categoría '{seleccion}'? Se eliminarán todos los productos de esa categoría."
            # Si el usuario presiona "No", askyesno devuelve False y se cancela todo.
            if not messagebox.askyesno("Confirmación", texto, parent=ventana):
                return
  
            if seleccion == TODO:
                bd.vaciar_inventario()
                aviso = "Se vació todo el inventario."
            else:
                bd.vaciar_categoria(seleccion)
                aviso = f"Se vació la categoría '{seleccion}'."

            F.inventario.productos = F.I().productos    # actualiza la lista en memoria
            F.mostrar_productos(Frame_producto)
            actualizar_selector_vaciar()
            messagebox.showinfo("Listo", aviso, parent=ventana)
        finally:
            boton_vaciar.config(state="normal")

    boton_vaciar = tk.Button(Frame_botones, text="Vaciar", command=vaciar)
    boton_vaciar.grid(row=1, column=7, padx=(0, 20), pady=10)


        # ---------- estilo de la barra superior ----------

    botones_barra = (boton_ingreso, boton_estadisticas, boton_admin, boton_vaciar)

    # El for repite lo mismo con cada botón.
    for b in botones_barra:
        b.config(
            bg="#f1f3f5",                 # mismo color que la barra, así parece "sin caja"
            fg="#212529",                 # letra casi negra
            activebackground="#dee2e6",   # color mientras lo estás presionando
            activeforeground="#212529",
            relief="flat",                # sin relieve de botón clásico
            bd=0,                         # sin borde
            font=("Segoe UI", 10),
            padx=14, pady=6,              # espacio interno
        )

    # El botón vaciar lo dejamos distinto.
    boton_vaciar.config(bg="#fd0d0d", fg="white",
                        activebackground="#c9202f", activeforeground="white")
    actualizar_selector_vaciar()
    mostrar_seccion(Frame_ingreso)      # mostramos el formulario apensa se abre la ventana
    #frame de los productos
    F.mostrar_productos(Frame_producto)