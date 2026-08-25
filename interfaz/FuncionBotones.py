#funciones a completar despues con sqlite3
import sqlite3
import tkinter as tk
from clases.usuario import usuario
from datos import bd_usuarios as BD
from . import Interfaz_pagina
# Codigo realizado por Cristobal Maulen
def ventana_admin(ventana):
    ventana3=tk.Toplevel(ventana)
    ventana3.geometry("350x350")
    ventana.iconify()
def ventana_usuario(ventana,texto,IngresoClave):
        Nombre=texto.get()
        contraseña=IngresoClave.get()
        resultado=BD.buscar_usuario(Nombre)
        if resultado==None:
            ventanaAdvertencia=tk.Toplevel(ventana)
            ventanaAdvertencia.geometry("100x60")
            texto=tk.Label(ventanaAdvertencia,text="EL usuario no existe")
            texto.pack()
            ventanaAdvertencia.after(3000,ventanaAdvertencia.destroy)
        elif contraseña!=resultado[2]:
            ventanaAdvertencia=tk.Toplevel(ventana)
            ventanaAdvertencia.geometry("100x60")
            texto=tk.Label(ventanaAdvertencia,text="la contraseña es incorrecta")
            texto.pack()
            ventanaAdvertencia.after(3000,ventanaAdvertencia.destroy)
        else:
            Interfaz_pagina.ejecutar(ventana)
        
def registro(texto,IngresoClave,ventana):
    Texto=texto.get()
    Clave=IngresoClave.get()
    resultado=BD.buscar_usuario(Texto)
    if resultado==None:
        nuevo_usuario=usuario(Texto,Clave)
        BD.insertar_usuario(nuevo_usuario)
    else:
         ventanaAdvertencia=tk.Toplevel(ventana)
         ventanaAdvertencia.geometry("50x50")
         texto=tk.Label(ventanaAdvertencia,text="EL usuario ya existe")
         texto.pack()
         ventanaAdvertencia.after(3000,ventanaAdvertencia.destroy)

    