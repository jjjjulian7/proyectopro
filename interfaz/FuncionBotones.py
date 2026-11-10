import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from clases.usuario import usuario
from clases.producto import Producto
from clases.inventario import Inventario as I
from clases.carrito import Carrito as C
from datos import bd_usuarios as BD
from datos import bd 
from . import Interfaz_pagina
from . import ventana_admin
from . import interfaz
from . import abrir_carrito
from . import Client_ProyProgV2 as ClienteRed
import Server_ProgProyV2 as ServidorRed
import threading
import queue
# Codigo realizado por Cristobal Maulen
inventario=I()
usuario_actual = None
carrito = C()
ClienteRed.conectar_interfaz_reserva(carrito.procesar_respuesta_reservar)
ClienteRed.conectar_interfaz_reponer(carrito.procesar_respuesta_eliminar)
ClienteRed.conectar_interfaz_vaciar(carrito.procesar_respuesta_vaciar)
ClienteRed.conectar_interfaz_venta(carrito.procesar_respuesta_venta)

def procesar_respuesta_deseos(tipo, ok, mensaje):
    """Llega desde el hilo que escucha al servidor; muestra el resultado de agregar a deseos / suscribirse."""
    titulo = "Lista de deseos" if tipo == 'agregar_deseo' else "Aviso de reposición"
    if ok:
        messagebox.showinfo(titulo, mensaje)
    else:
        messagebox.showwarning(titulo, mensaje)
ClienteRed.conectar_interfaz_deseos(procesar_respuesta_deseos)
def ventana_a(ventana):
    ventana_admin.ejecutar()
    ventana.iconify()
def validar_admin(ventana,IngresoRut,IngresoClave):
    Rut=IngresoRut.get().strip()
    Clave=IngresoClave.get()
    if not Rut or not Clave:
        messagebox.showwarning("Falta información", "Debes completar RUT y clave.")
        return
    Rut=usuario.validar_rut(Rut)
    if Rut==None:
        messagebox.showwarning("RUT inválido", "El RUT debe tener el formato 12.345.678-9")
        return
    resultado=BD.buscar_usuario_por_tipo('admin',Rut)
    if resultado==None or Clave!=resultado[2]:
        messagebox.showwarning("Acceso denegado", "RUT o clave incorrectos, o el usuario no es administrador.")
        return
    ventana_a(ventana)
def ventana_usuario(ventana,texto,IngresoClave):
        global usuario_actual   # Usamos global para que la variable cambie fuera de la funcion
        Nombre=texto.get().strip()
        contraseña=IngresoClave.get()
        resultado=BD.buscar_usuario(Nombre)
        if resultado==None:
            ventanaAdvertencia=tk.Toplevel(ventana)
            ventanaAdvertencia.geometry("200x60")
            texto=tk.Label(ventanaAdvertencia,text="El usuario no existe")
            texto.pack()
            ventanaAdvertencia.after(3000,ventanaAdvertencia.destroy)
        elif contraseña!=resultado[2]:
            ventanaAdvertencia=tk.Toplevel(ventana)
            ventanaAdvertencia.geometry("200x60")
            texto=tk.Label(ventanaAdvertencia,text="El usuario y/o la contraseña es incorrecta")
            texto.pack()
            ventanaAdvertencia.after(2000,ventanaAdvertencia.destroy)
        else:
            hilo_cliente = threading.Thread(target=ClienteRed.conectar)
            hilo_cliente.daemon = True
            hilo_cliente.start()
            usuario_actual = resultado[1]
            ventana.destroy()
           

def hay_usuario_autenticado():
    return usuario_actual is not None      

def validar_sesion():
    if not hay_usuario_autenticado():       # Si no se ha iniciado sesion, imprimira el mensaje y bloqueara la funcion de añadir al carrito 
        messagebox.showwarning(
            "Inicio de sesión requerido",
            "Debes iniciar sesión antes de agregar artículos al carrito."
        )
        return False
    return True

def cerrar_sesion():        # AVISO: Falta implementar la funcion. Aun hay q agregar boton de cerrar sesion!
    global usuario_actual
    usuario_actual = None
        
        
def registro(texto,IngresoClave,IngresoRut,ventana):
    Texto=texto.get().strip()
    Clave=IngresoClave.get()
    Rut=IngresoRut.get().strip()
    if not Texto or not Clave or not Rut:
        messagebox.showwarning("Falta información", "Debes completar nombre, clave y RUT.")
        return
    Rut=usuario.validar_rut(Rut)
    if Rut==None:
        messagebox.showwarning("RUT inválido", "El RUT debe tener el formato 12.345.678-9")
        return
    if Rut=="mal digito":
        messagebox.showerror("digito verificador","digito verificador invalido")
        return
    resultado=BD.buscar_usuario(Texto)
    if resultado==None:
        if BD.buscar_usuario_por_rut(Rut)!=None:
            messagebox.showwarning("RUT ya registrado", "Ya existe un usuario con ese RUT.")
            return
        nuevo_usuario=usuario(Texto,Clave,rut=Rut)
        BD.insertar_usuario(nuevo_usuario)
        messagebox.showinfo("registro","USUARIO REGISTRADO CON EXITO")
    else:
         messagebox.showinfo("registro","EL USUARIO YA EXISTE")

def mostrar_frame(frame, frames):
    for f in frames:
        f.pack_forget()
    frame.pack(fill="both", expand=True)

def hacer_admin(nombre, rut):
    nombre = nombre.strip()
    rut = rut.strip()

    if not nombre or not rut:
        tk.messagebox.showwarning("Falta información", "Debes completar nombre y RUT.")
        return False

    rut = usuario.validar_rut(rut)
    if rut is None:
        tk.messagebox.showwarning("RUT inválido", "El RUT debe tener el formato 12.345.678-9")
        return False

    resultado = BD.buscar_usuario(nombre)
    if resultado is None:
        tk.messagebox.showwarning("Usuario no encontrado", "No existe un usuario con ese nombre.")
        return False
    if resultado[3] is not None and resultado[3] != rut:
        tk.messagebox.showwarning("RUT incorrecto", "El RUT no coincide con el del usuario.")
        return False
    otro = BD.buscar_usuario_por_rut(rut)
    if otro is not None and otro[1] != nombre:
        tk.messagebox.showwarning("RUT en uso", "Ese RUT ya pertenece a otro usuario.")
        return False

    BD.convertir_en_admin(nombre, rut)
    tk.messagebox.showinfo("Éxito", f"El usuario {nombre} fue convertido a admin.")
    return True

def aplicar_estilo_tabla(widget):
    estilo = ttk.Style(widget)        # objeto que administra los estilos de ttk
    estilo.theme_use("clam")    # este tema nos permite cambiar el color la cabecera

    # Estilo del CUERPO de la tabla
    estilo.configure(
        "Productos.Treeview",
        font=("Segoe UI", 10),      
        rowheight=36,              
        background="#ffffff",       
        fieldbackground="#ffffff",  
        borderwidth=0,              
    )


    #Estilo de CABECERA tabla
    estilo.configure(
        "Productos.Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background="#7422A8",       
        foreground="white",         
        relief="flat",              
        padding=(8, 8),             
    )

 # estilo.map cambia colores según el estado del widget.
    # Por defecto la cabecera cambia de color al pasar el mouse. Aquí lo dejamos igual.
    estilo.map("Productos.Treeview.Heading", background=[("active", "#7422A8")])

    # Color de la fila seleccionada 
    estilo.map(
        "Productos.Treeview",
        background=[("selected", "#e7f5ff")],
        foreground=[("selected", "black")],
    )

ICONO_EDITAR = "↹"
ICONO_BORRAR = "🗑"

def mostrar_productos(Frame_productos):
    # La primera vez creamos la tabla. las siguientes veces solo la rellenamos
    if not hasattr(Frame_productos, "tabla"):
        aplicar_estilo_tabla(Frame_productos)

        columnas = ("id", "nombre", "precio", "stock", "categoria", "editar", "borrar") #asignamos el orden de las columnas
        tabla = ttk.Treeview(
            Frame_productos,
            columns=columnas,
            show="headings",
            style="Productos.Treeview",                  
        )

        # texto, ancho, alineacion de cada columna
        config_columnas = {
            "id":        ("ID", 60, "center"),
            "nombre":    ("NOMBRE", 260, "w"),         # "w" = west = izquierda
            "precio":    ("PRECIO", 110, "e"),         # "e" = east = derecha 
            "stock":     ("STOCK", 80, "center"),
            "categoria": ("CATEGORÍA", 160, "w"),
            "editar":    ("", 50, "center"),
            "borrar":    ("", 50, "center"),
        }
        for col, (texto, ancho, ancla) in config_columnas.items():
            tabla.heading(col, text=texto)                # texto de la cabecera
            tabla.column(col, width=ancho, anchor=ancla)  # ancho y alineación del contenido

        # un tag es una etiqueta que le ponemos a una fila para darle color.
        # Aqui definimos que color tiene cada etiqueta, después las asignamos al insertar.
        tabla.tag_configure("par", background="#ffffff")
        tabla.tag_configure("impar", background="#e0e0e0")
        tabla.tag_configure("sin_stock", foreground="#e8283c")

        def al_hacer_click(event):
            if tabla.identify_region(event.x, event.y) != "cell":
                return  # Si no se hizo click en una celda, no hacemos nada

            fila = tabla.identify_row(event.y)  #iid de la fila = ID del producto
            columna = tabla.identify_column(event.x)  # "#6" = editar y "#7" = borrar
            if not fila:
                return  # Si no se hizo click en una fila, no hacemos nada

            id_producto = int(fila) # convertimos el iid a int

            if columna == "#6":  # columna editar
                if hasattr(Frame_productos, "al_editar"):
                    Frame_productos.al_editar(id_producto)
                
            elif columna == "#7":  # columna borrar
                producto = inventario.buscar_producto(1, id_producto) 
                nombre = producto.nombre if producto else id_producto 

                if messagebox.askyesno("Confirmación", f"¿Eliminar '{nombre}'?"):
                    inventario.quitar_producto(id_producto)     # Borra de la BD y de la memoria 
                    mostrar_productos(Frame_productos)          # Volvemos a dibujar la tabla actualizada
 
        tabla.bind("<Button-1>", al_hacer_click)    # Conectamos el click izquierdo con la funcion de arriba

        # --- Implementacion del scrollbar
        # command=tabla.yview      -> al mover la barra, la tabla se desplaza
        # yscrollcommand   -> al desplazar la tabla con la rueda del mouse, la barra se mueve
        scroll = ttk.Scrollbar(Frame_productos, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)
        # Asignamos el orden en el frame, la barra del scroll a la derecha y la tabla a la izquierda
        scroll.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)
        Frame_productos.tabla = tabla

    tabla = Frame_productos.tabla
    tabla.delete(*tabla.get_children())

    # enumerate() entrega (posicion, elemento)
    # usamos la posicion para saber si la fila es par o impar
    for i, producto in enumerate(bd.mostrar_productos()):
        etiquetas = ["par" if i % 2 == 0 else "impar"]       # lista con la etiqueta de fondo 
        
        if int(producto[3]) == 0:
            etiquetas.append("sin_stock")

        tabla.insert("", "end", iid=str(producto[0]), values=producto + (ICONO_EDITAR, ICONO_BORRAR), tags=tuple(etiquetas))   # tags debe ser una tupla


def guardar_producto(id_producto, nombre, precio, stock, categoria, Frame_productos):
    """
        Sirve para agregar y modificar los productos en la pestaña admin
        id_producto = None ; se agregara un producto
        id_producto = 5    ; se modifica producto con id 5 
    """
    precio_num = float(precio.get())        # Pasamos precio y stock a numeros
    stock_num = int(stock.get())

    if stock_num < 0:                       # Validamos que el stock sea correcto
        messagebox.showwarning("Stock incorrecto", "El stock no puede ser negativo ")
        return False

    # Parte donde se registra un nuevo producto y se lo pasamos al inventario
    if id_producto is None:
        ok = inventario.agregar_producto(       
            Producto(nombre.get(), precio_num, stock_num, categoria.get())
        )
        mensaje = "Revisa que no haya campos vacios."
    # Parte donde se edita un producto ya existente, se busca por el id y le cambia los datos
    else:
        ok = inventario.actualizar_producto(
            id_producto, nombre.get(), precio_num, stock_num, categoria.get()
        )
        mensaje = "Producto no encontrado"

        # agregar_producto y actualizar_producto devuelven False si las validacion falla
        # si ok = False, da mensaje de error y usamos el mensaje de su seccion respectiva
    if not ok:
        messagebox.showwarning("Error", mensaje)
        return False

    mostrar_productos(Frame_productos)
    return True


def mostrar_estadisticas(selector_categoria, etiqueta_resultado):
    categoria = selector_categoria.get().strip()

    if not categoria:
        etiqueta_resultado.config(text="Selecciona una categoría.")
        return

    promedio = bd.promedio_precio_categoria(categoria)
    producto = bd.menor_stock(categoria)

    if promedio is None or producto is None:
        etiqueta_resultado.config(
            text="No hay productos registrados en esta categoría."
        )
        return

    etiqueta_resultado.config(
        text=(
            f"Precio promedio: ${promedio:,.0f}\n"
            f"Producto con menor stock: {producto[1]}\n"
            f"Stock disponible: {producto[3]} unidades"
        )
    )

def mostrar_total_inventario(etiqueta_resultado):
    total = bd.calcular_total_inventario()
    etiqueta_resultado.config(
        text=f"Valor total del inventario: ${total:,.0f}"
    )


def buscar(buscador, inventario_productos):
    valor = buscador.get()
    return inventario_productos.buscar_producto(2, valor)

def ingresar_log(usuario):
    '''hilo_server = threading.Thread(target= ServidorRed.iniciar_servidor)
    hilo_server.daemon = True
    hilo_server.start()'''
    if usuario==None:
        interfaz.ejecutar()
    else:
        
        return usuario



def agregar_producto_carrito(ProductoS, cantidad,usuarioA):
    carrito.agregar_producto(ProductoS,cantidad,usuarioA)

def identificador_usuario():
    """Con que se identifica al cliente en deseos, suscripciones y notificaciones.
    El enunciado permite RUN o nombre de usuario. Los clientes registrados hoy no tienen RUT
    (solo los admin), asi que se usa el RUT si existe y si no el nombre de usuario."""
    fila = BD.buscar_usuario(usuario_actual)  # columnas: id, nombre, contrasena, rut, rol
    return fila[3] or fila[1]

def agregar_a_deseos(id_producto, precio):
    if not hay_usuario_autenticado():
        messagebox.showwarning("Inicio de sesión requerido","Debes iniciar sesión para usar la lista de deseos.")
        return
    rut = identificador_usuario()
    # ya no se escribe en la BD desde el cliente: se manda al servidor por el socket y el responde por procesar_respuesta_deseos
    # (el precio no se envia: el servidor usa el precio real del producto)
    try:
        ClienteRed.dato_envia({'type':'agregar_deseo','rut':rut,'id_producto':id_producto})
    except OSError:
        messagebox.showwarning("Sin conexión","No se pudo comunicar con el servidor.")

def avisar_reposicion(id_producto, stock):
    if not hay_usuario_autenticado():
        messagebox.showwarning("Inicio de sesión requerido","Debes iniciar sesión para suscribirte al aviso de reposición.")
        return
    if stock > 0:
        messagebox.showinfo("Aviso de reposición","Este producto tiene stock disponible, el aviso es solo para productos agotados.")
        return
    rut = identificador_usuario()
    try:
        ClienteRed.dato_envia({'type':'suscribir_reposicion','rut':rut,'id_producto':id_producto})
    except OSError:
        messagebox.showwarning("Sin conexión","No se pudo comunicar con el servidor.")


def vaciarcarrito():
    carrito.vaciar_carrito()
    
def mostrar_info():
    subtotal= carrito.calcular_subtotal()
    iva = carrito.calcular_iva()
    total= carrito.calcular_total()
    return subtotal,iva,total
def eliminar_producto(ventana, i):
    ventana_cantidad = tk.Toplevel(ventana)
    ventana_cantidad.title("Carrito")
    ventana_cantidad.geometry("300x160")
    ventana_cantidad.grab_set()

    tk.Label(ventana_cantidad, text="CANTIDAD:").pack(pady=5)
    cantidad = tk.Entry(ventana_cantidad)
    cantidad.pack(pady=5)
    cantidad.focus()

    def eliminar():
        cant = cantidad.get()
        if cant.isdigit():
  
            carrito.eliminar_producto(i, int(cant))
            ventana_cantidad.destroy()
        else:
            print("Ingrese una cantidad válida")

    btn_confirmar = tk.Button(ventana_cantidad, text="Aceptar", command=eliminar)
    btn_confirmar.pack(pady=10)


    ventana.wait_window(ventana_cantidad)

menu_usuario = None   # frame del menu del icono de usuario; vive fuera de la funcion para recordar si esta abierto

def cerrar_menu():
    global menu_usuario
    if menu_usuario is not None and menu_usuario.winfo_exists():
        menu_usuario.destroy()
    menu_usuario = None

def lista_deseos(ventana):
    global menu_usuario
    # si el menu ya esta abierto, este segundo clic lo cierra y no crea otro
    if menu_usuario is not None and menu_usuario.winfo_exists():
        cerrar_menu()
        return
    lista=tk.Frame(ventana)
    menu_usuario = lista
    lista.place(
        relx=1,
        y=96,
        anchor="ne",
        width=250,
        height=220)
    def crear_linea(contenedor,fila):
        linea = tk.Frame(
        contenedor,
        bg="#dcdcdc",
        height=1
        )
        linea.grid(
            row=fila,
            column=0,
            padx=10,
            sticky="ew" 
        )
        linea.grid(row=fila,column=0, padx=10)
    lista.grid_columnconfigure(0, weight=1)
    ListaDeseos=tk.Label(lista,text="Lista de deseos",font=("Arial", 12, "bold"),cursor="hand2")
    Suscripcion=tk.Label(lista,text="Suscripcion",font=("Arial", 12, "bold"),cursor="hand2")
    Notificacion=tk.Label(lista,text="Notificacion",font=("Arial", 12, "bold"),cursor="hand2")
    iniciar_sesion=tk.Label(lista,text="iniciar sesion",font=("Arial", 12, "bold"),cursor="hand2")
    ListaDeseos.grid(row=0,column=0)
    crear_linea(lista,1)
    Suscripcion.grid(row=2,column=0)
    crear_linea(lista,3)
    Notificacion.grid(row=4,column=0)
    crear_linea(lista,5)
    iniciar_sesion.grid(row=6,column=0)

    # al elegir una opcion el menu se cierra y despues se abre la ventana correspondiente
    def elegir(accion):
        cerrar_menu()
        accion()

    iniciar_sesion.bind("<Button-1>",lambda event:elegir(lambda:ingresar_log(None)))
    ListaDeseos.bind("<Button-1>",lambda event:elegir(LD))
    Suscripcion.bind("<Button-1>",lambda event:elegir(Suscripciones))
    Notificacion.bind("<Button-1>",lambda event:elegir(Notificaciones))


# ---------------------------------------------------------------
# Ventanas del cliente: lista de deseos, suscripciones y notificaciones.
# Los datos NO se leen de la BD aqui: se piden al servidor por el socket (mensaje 'mi_lista')
# y cuando llega la respuesta se rellenan todas las ventanas que estan abiertas.
# ---------------------------------------------------------------
ventanas_lista = {}   # clave ('deseos','suscripciones','notificaciones') -> (ventana, tabla)

def _clp(valor):
    return f"${valor:,.0f}".replace(",", ".") if valor is not None else "-"

def _filas_deseos(datos):
    filas = []
    for p in datos.get("deseos", []):
        etiqueta = []
        if p["stock"] == 0:
            etiqueta.append("sin_stock")
        if p["precio"] < p["precio_guardado"]:
            etiqueta.append("rebaja")      # el precio actual es menor al que tenia al guardarlo
        filas.append(((p["id"], p["nombre"], _clp(p["precio_guardado"]), _clp(p["precio"]),
                       p["stock"], p["categoria"]), etiqueta))
    return filas

def _filas_suscripciones(datos):
    return [((p["id"], p["nombre"], _clp(p["precio"]), p["stock"], p["categoria"],
              "Ya hay stock" if p["stock"] > 0 else "Esperando reposición"),
             ["con_stock"] if p["stock"] > 0 else ["sin_stock"])
            for p in datos.get("suscripciones", [])]

def _filas_notificaciones(datos):
    return [((n["id"], n["nombre"], n["mensaje"]), []) for n in datos.get("notificaciones", [])]

# clave -> (titulo ventana, columnas {id: (texto, ancho, ancla)}, funcion que arma las filas, texto si esta vacia)
CONFIG_VENTANAS = {
    "deseos": ("Mi lista de deseos",
               {"id": ("ID", 50, "center"), "nombre": ("NOMBRE", 260, "w"),
                "guardado": ("PRECIO GUARDADO", 130, "e"), "actual": ("PRECIO ACTUAL", 130, "e"),
                "stock": ("STOCK", 70, "center"), "categoria": ("CATEGORÍA", 150, "w")},
               _filas_deseos, "Aún no tienes productos en tu lista de deseos."),
    "suscripciones": ("Mis avisos de reposición",
               {"id": ("ID", 50, "center"), "nombre": ("NOMBRE", 280, "w"),
                "precio": ("PRECIO", 110, "e"), "stock": ("STOCK", 70, "center"),
                "categoria": ("CATEGORÍA", 150, "w"), "estado": ("ESTADO", 170, "w")},
               _filas_suscripciones, "No estás suscrito a ningún producto agotado."),
    "notificaciones": ("Mis notificaciones",
               {"id": ("ID", 50, "center"), "nombre": ("PRODUCTO", 260, "w"),
                "mensaje": ("AVISO", 480, "w")},
               _filas_notificaciones, "No tienes notificaciones."),
}

def _rellenar_ventana(clave, datos):
    ventana, tabla, etiqueta_vacia = ventanas_lista[clave]
    _, _, armar_filas, texto_vacio = CONFIG_VENTANAS[clave]
    tabla.delete(*tabla.get_children())
    filas = armar_filas(datos)
    for i, (valores, etiquetas) in enumerate(filas):
        tabla.insert("", "end", values=valores, tags=["par" if i % 2 == 0 else "impar"] + etiquetas)
    etiqueta_vacia.config(text="" if filas else texto_vacio)

cola_respuestas_lista = queue.Queue()   # puente entre el hilo de red y el hilo de tkinter
revisando_cola = False

def procesar_respuesta_lista(datos):
    """Corre en el hilo que escucha al servidor: NO toca la interfaz, solo deja la respuesta en la cola.
    (tkinter no es seguro entre hilos; la ventana la lee desde su propio hilo con after)."""
    cola_respuestas_lista.put(datos)
ClienteRed.conectar_interfaz_lista(procesar_respuesta_lista)

def _revisar_cola_lista(raiz):
    """Corre en el hilo de tkinter cada 200 ms mientras haya alguna ventana abierta."""
    global revisando_cola
    try:
        while True:
            datos = cola_respuestas_lista.get_nowait()
            if not datos.get("ok"):
                messagebox.showwarning("Mis listas", datos.get("mensaje", "No se pudo cargar la información."))
                continue
            for clave in list(ventanas_lista):
                if ventanas_lista[clave][0].winfo_exists():
                    _rellenar_ventana(clave, datos)
    except queue.Empty:
        pass
    if ventanas_lista:
        raiz.after(200, lambda: _revisar_cola_lista(raiz))
    else:
        revisando_cola = False

def abrir_ventana_lista(clave):
    if not hay_usuario_autenticado():
        messagebox.showwarning("Inicio de sesión requerido", "Debes iniciar sesión para ver esta sección.")
        return
    # si ya esta abierta, se trae al frente y se refresca en vez de abrir otra igual
    if clave in ventanas_lista and ventanas_lista[clave][0].winfo_exists():
        ventanas_lista[clave][0].lift()
    else:
        titulo, columnas, _, _ = CONFIG_VENTANAS[clave]
        v = tk.Toplevel()
        v.title(titulo)
        v.geometry("900x480")
        v.configure(bg="white")
        tk.Label(v, text=titulo, font=("Arial", 14, "bold"), bg="white").pack(pady=(12, 4))
        etiqueta_vacia = tk.Label(v, text="Cargando...", bg="white", fg="#666666")
        etiqueta_vacia.pack()
        marco = tk.Frame(v)
        marco.pack(fill="both", expand=True, padx=20, pady=12)
        aplicar_estilo_tabla(marco)
        tabla = ttk.Treeview(marco, columns=tuple(columnas), show="headings", style="Productos.Treeview")
        for col, (texto, ancho, ancla) in columnas.items():
            tabla.heading(col, text=texto)
            tabla.column(col, width=ancho, anchor=ancla)
        tabla.tag_configure("par", background="#ffffff")
        tabla.tag_configure("impar", background="#e0e0e0")
        tabla.tag_configure("sin_stock", foreground="#e8283c")
        tabla.tag_configure("con_stock", foreground="#1a7f37")
        tabla.tag_configure("rebaja", foreground="#1a7f37")
        scroll = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)
        ventanas_lista[clave] = (v, tabla, etiqueta_vacia)
        v.bind("<Destroy>", lambda e: ventanas_lista.pop(clave, None) if e.widget is v else None)
    global revisando_cola
    if not revisando_cola:
        revisando_cola = True
        raiz = tk._default_root   # ventana principal de la tienda: no se cierra mientras se usa la app
        raiz.after(200, lambda: _revisar_cola_lista(raiz))
    rut = identificador_usuario()
    try:
        ClienteRed.dato_envia({'type': 'mi_lista', 'rut': rut})
    except OSError:
        messagebox.showwarning("Sin conexión", "No se pudo comunicar con el servidor.")

def LD():
    abrir_ventana_lista("deseos")

def Suscripciones():
    abrir_ventana_lista("suscripciones")

def Notificaciones():
    abrir_ventana_lista("notificaciones")