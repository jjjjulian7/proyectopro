import tkinter as tk
import queue
from tkinter import messagebox
from . import FuncionBotones as F
from . import Client_ProyProgV2 as ClienteRed
# Codigo del chat con el asistente IA, la consulta se manda al servidor igual que el carrito

COLOR_MORADO = "#7422A8"
COLOR_FONDO = "#F7F7F7"
COLOR_BURBUJA_IA = "#e0e0e0"
FUENTE = ("Segoe UI", 10)

ventana_chat = None                 # vive fuera de la funcion para recordar si el chat ya esta abierto
cola_respuestas_ia = queue.Queue()  # puente entre el hilo de red y el hilo de tkinter

def procesar_respuesta_ia(ok, respuesta):
    '''Llega desde el hilo que escucha al servidor, solo la deja en la cola (tkinter no se toca desde otro hilo).'''
    cola_respuestas_ia.put((ok, respuesta))
ClienteRed.conectar_interfaz_ia(procesar_respuesta_ia)

def limpiar_texto(texto):
    # gemini responde con formato markdown, aca se deja mas limpio para mostrarlo en un label
    lineas = []
    for linea in texto.split("\n"):
        if linea.strip().startswith("* "):
            linea = linea.replace("* ", "• ", 1)
        lineas.append(linea)
    return "\n".join(lineas).replace("**", "").replace("##", "").strip()

def abrir_chat():
    global ventana_chat
    if not F.hay_usuario_autenticado():
        messagebox.showwarning("Inicio de sesión requerido", "Debes iniciar sesión para hablar con el asistente.")
        return
    # si ya esta abierto no se crea otro, solo se trae al frente
    if ventana_chat is not None and ventana_chat.winfo_exists():
        ventana_chat.lift()
        ventana_chat.focus_force()
        return

    # se vacia la cola por si quedo una respuesta vieja de un chat anterior
    while not cola_respuestas_ia.empty():
        cola_respuestas_ia.get_nowait()

    v = tk.Toplevel()
    ventana_chat = v
    v.title("Asistente MaulenMarket")
    v.geometry("500x620")
    v.minsize(360, 400)
    v.configure(bg=COLOR_FONDO)

    # variables que cambian dentro de las funciones de abajo
    estado = {"esperando": False, "escribiendo": None, "consulta": 0}
    burbujas = []   # se guardan para poder ajustar el ancho del texto cuando cambia el tamaño de la ventana

    # BARRA SUPERIOR
    barra = tk.Frame(v, bg=COLOR_MORADO, height=50)
    barra.pack(side="top", fill="x")
    tk.Label(barra, text="Asistente IA", font=("Segoe UI", 13, "bold"), bg=COLOR_MORADO, fg="white").pack(pady=12)

    # ZONA DE ESCRIBIR (se empaqueta antes del scroll para que siempre quede abajo)
    zona_entrada = tk.Frame(v, bg="white")
    zona_entrada.pack(side="bottom", fill="x")
    entrada = tk.Entry(zona_entrada, font=("Segoe UI", 11))
    entrada.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=12, ipady=6)
    boton_enviar = tk.Button(zona_entrada, text="Enviar", font=("Arial", 10, "bold"), bg=COLOR_MORADO, fg="white",
                             relief="flat", cursor="hand2", padx=14, pady=6)
    boton_enviar.pack(side="right", padx=(0, 12), pady=12)

    # SCROLL DEL CHAT (mismo metodo que la pagina principal: Canvas + Scrollbar + Frame interior)
    frame_scroll = tk.Frame(v, bg=COLOR_FONDO)
    frame_scroll.pack(side="top", fill="both", expand=True)
    canvas = tk.Canvas(frame_scroll, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame_interior = tk.Frame(canvas, bg=COLOR_FONDO)
    ventana_frame = canvas.create_window((0, 0), window=frame_interior, anchor="nw")

    def actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame_interior.bind("<Configure>", actualizar_scroll)

    def ajustar_ancho(event):
        canvas.itemconfig(ventana_frame, width=event.width)
        for burbuja in burbujas:
            if burbuja.winfo_exists():
                burbuja.config(wraplength=max(150, int(event.width * 0.7)))
    canvas.bind("<Configure>", ajustar_ancho)

    # rueda del mouse: solo funciona mientras el mouse esta sobre el chat
    def rueda(event):
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")
        else:
            canvas.yview_scroll(int(-event.delta / 120), "units")
    def activar_rueda(event):
        v.bind_all("<MouseWheel>", rueda)
        v.bind_all("<Button-4>", rueda)   # linux
        v.bind_all("<Button-5>", rueda)
    def desactivar_rueda(event):
        v.unbind_all("<MouseWheel>")
        v.unbind_all("<Button-4>")
        v.unbind_all("<Button-5>")
    frame_scroll.bind("<Enter>", activar_rueda)
    frame_scroll.bind("<Leave>", desactivar_rueda)

    def bajar():
        canvas.update_idletasks()
        canvas.yview_moveto(1.0)   # deja el scroll al final para ver el ultimo mensaje

    def agregar_mensaje(texto, quien):
        fila = tk.Frame(frame_interior, bg=COLOR_FONDO)
        fila.pack(fill="x", padx=10, pady=4)
        if quien == "usuario":
            color_fondo, color_texto, lado = COLOR_MORADO, "white", "e"   # lo que escribe el cliente va a la derecha
        elif quien == "error":
            color_fondo, color_texto, lado = "#fde8ea", "#e8283c", "w"
        else:
            color_fondo, color_texto, lado = COLOR_BURBUJA_IA, "#222222", "w"
        burbuja = tk.Label(fila, text=texto, bg=color_fondo, fg=color_texto, font=FUENTE, justify="left",
                           wraplength=max(150, int(canvas.winfo_width() * 0.7)) if canvas.winfo_width() > 1 else 340,
                           padx=12, pady=8)
        burbuja.pack(anchor=lado)
        burbujas.append(burbuja)
        bajar()
        return fila

    def terminar_espera():
        estado["esperando"] = False
        boton_enviar.config(state="normal")
        if estado["escribiendo"] is not None:
            estado["escribiendo"].destroy()
            estado["escribiendo"] = None

    def tiempo_agotado(numero):
        # si el servidor nunca contesta se libera el chat para que no quede pegado
        if estado["esperando"] and estado["consulta"] == numero:
            terminar_espera()
            agregar_mensaje("El asistente no respondió a tiempo, intenta de nuevo.", "error")

    def enviar_pregunta(event=None):
        pregunta = entrada.get().strip()
        if not pregunta or estado["esperando"]:
            return
        if ClienteRed.conexion is None:
            agregar_mensaje("No hay conexión con el servidor, intenta de nuevo en un momento.", "error")
            return
        agregar_mensaje(pregunta, "usuario")
        entrada.delete(0, tk.END)
        try:
            ClienteRed.dato_envia({'type': 'consulta_ia', 'pregunta': pregunta, 'nombre_u': F.usuario_actual})
        except OSError:
            agregar_mensaje("No se pudo comunicar con el servidor.", "error")
            return
        estado["esperando"] = True
        estado["consulta"] += 1
        boton_enviar.config(state="disabled")
        estado["escribiendo"] = agregar_mensaje("Escribiendo...", "ia")
        v.after(60000, lambda n=estado["consulta"]: tiempo_agotado(n))

    boton_enviar.config(command=enviar_pregunta)
    entrada.bind("<Return>", enviar_pregunta)

    def revisar_cola():
        # revisa cada 200ms si llego una respuesta del servidor (mismo metodo que la lista de deseos)
        try:
            while True:
                ok, respuesta = cola_respuestas_ia.get_nowait()
                if not estado["esperando"]:
                    continue   # llego tarde, ya se habia mostrado el error de tiempo
                terminar_espera()
                if ok:
                    agregar_mensaje(limpiar_texto(respuesta), "ia")
                else:
                    agregar_mensaje(respuesta or "No se pudo obtener respuesta del asistente.", "error")
        except queue.Empty:
            pass
        if v.winfo_exists():
            v.after(200, revisar_cola)
    v.after(200, revisar_cola)

    agregar_mensaje("Hola, soy Maulencito, el asistente de MaulenMarket. Pregúntame por productos, precios o stock.", "ia")
    entrada.focus_set()
