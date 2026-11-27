import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from clases.usuario import usuario
from clases.producto import Producto
from clases.ListaDeseos import Suscripcion
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

pendientes_mover = set()   # ids que el usuario pidio mover desde su lista de deseos al carrito

def _tras_reserva(ok, mensaje, id_producto, cantidad, nombre, precio):
    '''Respuesta del servidor a reservar_stock. Si venia de "mover al carrito" y salio bien, lo saca de la lista de deseos.'''
    carrito.procesar_respuesta_reservar(ok, mensaje, id_producto, cantidad, nombre, precio)
    if id_producto in pendientes_mover:
        pendientes_mover.discard(id_producto)
        if ok:
            try:
                ClienteRed.dato_envia({'type':'quitar_deseo','rut':identificador_usuario(),'id_producto':id_producto})
            except OSError:
                pass
ClienteRed.conectar_interfaz_reserva(_tras_reserva)
ClienteRed.conectar_interfaz_reponer(carrito.procesar_respuesta_eliminar)
ClienteRed.conectar_interfaz_vaciar(carrito.procesar_respuesta_vaciar)
ClienteRed.conectar_interfaz_venta(carrito.procesar_respuesta_venta)
ClienteRed.conectar_interfaz_envios(carrito.procesar_respuesta_envios)

def procesar_respuesta_deseos(tipo, ok, mensaje):
    '''Llega desde el hilo que escucha al servidor; muestra el resultado de agregar a deseos / suscribirse.'''
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
            ClienteRed.identificarse(identificador_usuario())   # el servidor asocia este socket con su rut
            _iniciar_revision_avisos()
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

        columnas = ("id", "nombre", "precio", "stock", "categoria", "esperando", "editar", "borrar") #asignamos el orden de las columnas
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
            "esperando": ("ESPERANDO", 150, "w"),    # clientes suscritos al aviso de reposicion
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
            columna = tabla.identify_column(event.x)  # "#7" = editar y "#8" = borrar
            if not fila:
                return  # Si no se hizo click en una fila, no hacemos nada

            id_producto = int(fila) # convertimos el iid a int

            if columna == "#7":  # columna editar
                if hasattr(Frame_productos, "al_editar"):
                    Frame_productos.al_editar(id_producto)
                
            elif columna == "#8":  # columna borrar
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

        # los clientes se suscriben y los stocks cambian mientras el admin tiene la ventana abierta:
        # cada 3 s se revisa y solo se redibuja si algo cambio
        def auto_refrescar():
            if not tabla.winfo_exists():
                return
            try:
                if _filas_tabla_admin() != getattr(Frame_productos, "ultimas_filas", None):
                    mostrar_productos(Frame_productos)
            except Exception as e:
                print(f"[!] No se pudo refrescar la tabla de productos: {e}")
            tabla.after(3000, auto_refrescar)
        tabla.after(3000, auto_refrescar)

    tabla = Frame_productos.tabla
    tabla.delete(*tabla.get_children())

    filas = _filas_tabla_admin()
    Frame_productos.ultimas_filas = filas
    for i, (iid, valores, etiquetas) in enumerate(filas):
        tabla.insert("", "end", iid=iid, values=valores, tags=("par" if i % 2 == 0 else "impar",) + etiquetas)   # tags debe ser una tupla

def _texto_esperando(n):
    if n == 0:
        return ""
    return "1 cliente esperando" if n == 1 else f"{n} clientes esperando"

def _filas_tabla_admin():
    '''Filas (iid, valores, etiquetas) de la tabla de productos del admin, con el conteo de suscriptores de cada uno.'''
    esperando = Suscripcion.contar_por_producto()
    filas = []
    for producto in bd.mostrar_productos():    # producto = (id, nombre, precio, stock, categoria)
        etiquetas = ("sin_stock",) if int(producto[3]) == 0 else ()
        valores = tuple(producto) + (_texto_esperando(esperando.get(producto[0], 0)), ICONO_EDITAR, ICONO_BORRAR)
        filas.append((str(producto[0]), valores, etiquetas))
    return filas


def guardar_producto(id_producto, nombre, precio, stock, categoria, Frame_productos):
    '''
        Sirve para agregar y modificar los productos en la pestaña admin
        id_producto = None ; se agregara un producto
        id_producto = 5    ; se modifica producto con id 5 
    '''
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

def agregar_al_carrito_validado(id_producto, nombre, precio, categoria, stock, cantidad=1, descontar_carrito=True):

    if not validar_sesion():
        return False
    if not isinstance(cantidad, int) or cantidad <= 0:
        messagebox.showerror("Error", "Ingresa una cantidad valida")
        return False
    if stock is None or stock <= 0:
        messagebox.showwarning("Sin stock", f"'{nombre}' está agotado por ahora.")
        return False
    en_carrito = sum(i["cantidad"] for i in carrito.items if i["id"] == id_producto) if descontar_carrito else 0
    if cantidad + en_carrito > stock:
        messagebox.showerror("Error", "No hay stock suficiente")
        return False
    producto = Producto(nombre, precio, stock, categoria)
    producto.id = id_producto
    agregar_producto_carrito(producto, cantidad, usuario_actual)
    return True

def identificador_usuario():
    
    fila = BD.buscar_usuario(usuario_actual)  # columnas: id, nombre, contrasena, rut, rol
    return fila[3] or fila[1]

def agregar_a_deseos(id_producto, precio):
    if not hay_usuario_autenticado():
        messagebox.showwarning("Inicio de sesión requerido","Debes iniciar sesión para usar la lista de deseos.")
        return
    rut = identificador_usuario()
    
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



ventanas_lista = {}   

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

productos_deseos = {}   # ultimo estado de la lista de deseos recibido del servidor, por id de producto

def mover_deseo_al_carrito(tabla):

    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showinfo("Lista de deseos", "Selecciona un producto de la lista.")
        return
    p = productos_deseos.get(int(tabla.item(seleccion[0], "values")[0]))
    if p is None:
        return
    pendientes_mover.add(p["id"])      # se marca antes de enviar: la respuesta llega por otro hilo
    if not agregar_al_carrito_validado(p["id"], p["nombre"], p["precio"], p["categoria"], p["stock"],
                                       1, descontar_carrito=False):
        pendientes_mover.discard(p["id"])

cola_respuestas_lista = queue.Queue()   # puente entre el hilo de red y el hilo de tkinter
revisando_cola = False

def procesar_respuesta_lista(datos):

    cola_respuestas_lista.put(datos)
ClienteRed.conectar_interfaz_lista(procesar_respuesta_lista)


cola_avisos = queue.Queue()
revisando_avisos = False

def procesar_aviso(dato):

    cola_avisos.put(dato)
ClienteRed.conectar_interfaz_aviso(procesar_aviso)

def _mostrar_aviso(dato, raiz):
    
    titulo = "Producto repuesto" if dato.get("tipo") == "reposicion" else "Rebaja de precio"
    if dato.get("tipo") == "pedido":
        titulo = "Estado de tu pedido"
    v = tk.Toplevel(raiz)
    v.title(titulo)
    v.configure(bg="white")
    v.resizable(False, False)
    tk.Label(v, text=titulo, font=("Arial", 13, "bold"), bg="white", fg="#4a2a85").pack(padx=28, pady=(18, 4))
    tk.Label(v, text=dato.get("mensaje", "Hay novedades de un producto que sigues."),
             bg="white", wraplength=340, justify="center").pack(padx=28, pady=(0, 14))
    botones = tk.Frame(v, bg="white")
    botones.pack(pady=(0, 18))

    stock = dato.get("stock")
    ofrecer = (dato.get("id_producto") is not None and dato.get("precio") is not None
               and isinstance(stock, int) and stock > 0)
    def agregar():
        
        if agregar_al_carrito_validado(dato["id_producto"], dato.get("nombre"), dato["precio"],
                                       dato.get("categoria"), stock, 1, descontar_carrito=False):
            v.destroy()
    if ofrecer:
        tk.Button(botones, text="Agregar al carrito", font=("Arial", 10, "bold"), bg="#7422A8", fg="white",
                  cursor="hand2", command=agregar).pack(side="left", padx=6)
    tk.Button(botones, text="Cerrar", font=("Arial", 10), cursor="hand2", command=v.destroy).pack(side="left", padx=6)
    v.lift()
    v.focus_force()

def _revisar_avisos(raiz):
    
    global revisando_avisos
    hubo_avisos = False
    try:
        while True:
            dato = cola_avisos.get_nowait()
            hubo_avisos = True
            _mostrar_aviso(dato, raiz)
    except queue.Empty:
        pass
    if hubo_avisos and ventanas_lista:
        try:
            ClienteRed.dato_envia({'type': 'mi_lista', 'rut': identificador_usuario()})
        except OSError:
            pass
    if hay_usuario_autenticado():
        raiz.after(500, lambda: _revisar_avisos(raiz))
    else:
        revisando_avisos = False

def _iniciar_revision_avisos():
    global revisando_avisos
    if not revisando_avisos:
        revisando_avisos = True
        raiz = tk._default_root   # ventana principal de la tienda
        raiz.after(500, lambda: _revisar_avisos(raiz))

def _revisar_cola_lista(raiz):
   
    global revisando_cola
    try:
        while True:
            datos = cola_respuestas_lista.get_nowait()
            if not datos.get("ok"):
                messagebox.showwarning("Mis listas", datos.get("mensaje", "No se pudo cargar la información."))
                continue
            productos_deseos.clear()
            productos_deseos.update({p["id"]: p for p in datos.get("deseos", [])})
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
        if clave == "deseos":
            barra = tk.Frame(v, bg="white")
            barra.pack(side="bottom", fill="x", padx=20, pady=(0, 12))
            boton_mover = tk.Button(barra, text="Mover al carrito", font=("Arial", 10, "bold"), bg="#7422A8", fg="white",
                                    cursor="hand2")
            boton_mover.pack(side="right")
            tk.Label(barra, text="Selecciona un producto (o haz doble clic) para pasarlo al carrito.",
                     bg="white", fg="#666666").pack(side="left")
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
        if clave == "deseos":
            boton_mover.config(command=lambda: mover_deseo_al_carrito(tabla))
            tabla.bind("<Double-1>", lambda e: mover_deseo_al_carrito(tabla))
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