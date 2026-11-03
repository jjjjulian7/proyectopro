import json
import os
import queue
import shutil
import tempfile
import threading
import unittest
from unittest.mock import MagicMock, patch

from datos import bd, bd_carrito, bd_usuarios, bd_ventas
from clases.producto import Producto
from clases.inventario import Inventario
from clases.usuario import usuario
from clases.carrito import Carrito
from clases.Venta import venta
import Server_ProgProyV2 as servidor
from interfaz import Client_ProyProgV2 as cliente_red
from interfaz import validar_tarjeta
from interfaz import FuncionBotones


class FakeSocket:
    def __init__(self, cola_entrada, cola_salida):
        self._in = cola_entrada
        self._out = cola_salida
        self.cerrado = False

    def sendall(self, data):
        if self.cerrado:
            raise OSError("Socket cerrado")
        self._out.put(data)

    def recv(self, bufsize=4096):
        dato = self._in.get()
        if dato is None:
            return b""
        return dato[:bufsize]

    def close(self):
        if not self.cerrado:
            self.cerrado = True
            self._out.put(None)


def crear_par_sockets():
    q1 = queue.Queue()
    q2 = queue.Queue()
    return FakeSocket(q2, q1), FakeSocket(q1, q2)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        self._orig_bd = bd.ruta_bd
        self._orig_bd_usuarios = bd_usuarios.ruta_bd
        self._orig_bd_carrito = bd_carrito.ruta_bd
        self._orig_bd_ventas = bd_ventas.ruta_bd

        bd.ruta_bd = os.path.join(self.temp_dir, "productos.db")
        bd_usuarios.ruta_bd = os.path.join(self.temp_dir, "usuarios.db")
        bd_carrito.ruta_bd = os.path.join(self.temp_dir, "carrito.db")
        bd_ventas.ruta_bd = os.path.join(self.temp_dir, "ventas.db")

        bd.crear_tabla()
        bd_usuarios.crear_tabla()
        bd_carrito.crear_tabla()
        bd_ventas.crear_tabla()

        self.patch1 = patch("clases.carrito.messagebox")
        self.patch2 = patch("interfaz.Client_ProyProgV2.messagebox")
        self.patch3 = patch("interfaz.FuncionBotones.messagebox")
        self.patch1.start()
        self.patch2.start()
        self.patch3.start()

        self.recibos_creados = []

    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()

        bd.ruta_bd = self._orig_bd
        bd_usuarios.ruta_bd = self._orig_bd_usuarios
        bd_carrito.ruta_bd = self._orig_bd_carrito
        bd_ventas.ruta_bd = self._orig_bd_ventas

        for ruta in self.recibos_creados:
            if ruta and os.path.exists(ruta):
                try:
                    os.remove(ruta)
                except OSError:
                    pass

        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestProductoEInventario(BaseTest):

    def test_creacion_objeto_producto(self):
        p = Producto("Mouse Gamer", 15990, 10, "Mouse")
        self.assertIsNone(p.id)
        self.assertEqual(p.nombre, "Mouse Gamer")
        self.assertEqual(p.precio, 15990)
        self.assertEqual(p.stock, 10)
        self.assertEqual(p.categoria, "Mouse")

    def test_validaciones_inventario(self):
        inv = Inventario()
        self.assertTrue(inv.validar_stock(0))
        self.assertTrue(inv.validar_stock(15))
        self.assertFalse(inv.validar_stock(-1))

        self.assertTrue(inv.validar_precio(0))
        self.assertTrue(inv.validar_precio(25000))
        self.assertFalse(inv.validar_precio(-500))

        self.assertTrue(inv.validar_texto("Monitores"))
        self.assertFalse(inv.validar_texto(""))
        self.assertFalse(inv.validar_texto("   "))

        self.assertTrue(inv.validar_producto("Teclado", 35000, 5, "Teclados"))
        self.assertFalse(inv.validar_producto("", 35000, 5, "Teclados"))
        self.assertFalse(inv.validar_producto("Teclado", -100, 5, "Teclados"))
        self.assertFalse(inv.validar_producto("Teclado", 35000, -1, "Teclados"))
        self.assertFalse(inv.validar_producto("Teclado", 35000, 5, "  "))

    def test_agregar_y_buscar_producto(self):
        inv = Inventario()
        p1 = Producto("Monitor 144Hz", 150000, 8, "Monitores")
        p2 = Producto("Mouse Inalambrico", 20000, 15, "Mouse")

        self.assertTrue(inv.agregar_producto(p1))
        self.assertTrue(inv.agregar_producto(p2))
        self.assertIsNotNone(p1.id)
        self.assertIsNotNone(p2.id)

        p_invalido = Producto("", -10, -5, "")
        self.assertFalse(inv.agregar_producto(p_invalido))

        encontrado = inv.buscar_producto(1, p1.id)
        self.assertEqual(encontrado.nombre, "Monitor 144Hz")

        por_nombre = inv.buscar_producto(2, "144hz")
        self.assertEqual(len(por_nombre), 1)
        self.assertEqual(por_nombre[0].id, p1.id)

        por_categoria = inv.buscar_producto(2, "mouse")
        self.assertEqual(len(por_categoria), 1)
        self.assertEqual(por_categoria[0].id, p2.id)

    def test_actualizar_y_quitar_producto(self):
        inv = Inventario()
        p = Producto("RAM 8GB", 25000, 12, "RAM")
        inv.agregar_producto(p)

        ok = inv.actualizar_producto(p.id, "RAM 16GB", 45000, 20, "RAM")
        self.assertTrue(ok)
        actualizado = inv.buscar_producto(1, p.id)
        self.assertEqual(actualizado.nombre, "RAM 16GB")
        self.assertEqual(actualizado.precio, 45000)
        self.assertEqual(actualizado.stock, 20)

        self.assertFalse(inv.actualizar_producto(p.id, "", -100, -5, ""))
        self.assertFalse(inv.actualizar_producto(99999, "X", 1000, 1, "Cat"))

        self.assertTrue(inv.quitar_producto(p.id))
        self.assertIsNone(inv.buscar_producto(1, p.id))
        self.assertFalse(inv.quitar_producto(p.id))


class TestBaseDatosProductos(BaseTest):

    def setUp(self):
        super().setUp()
        self.p1 = Producto("Ryzen 5", 150000, 5, "Procesadores")
        self.p2 = Producto("Ryzen 7", 250000, 2, "Procesadores")
        self.p3 = Producto("Mouse Logitech", 30000, 10, "Mouse")
        bd.insertar_producto(self.p1)
        bd.insertar_producto(self.p2)
        bd.insertar_producto(self.p3)

    def test_estadisticas_y_filtros(self):
        self.assertEqual(bd.calcular_total_inventario(), 1550000)

        en_rango = bd.filtrar_rango_precios(25000, 160000)
        self.assertEqual(len(en_rango), 2)

        procesadores = bd.filtrar_categoria("Procesadores")
        self.assertEqual(len(procesadores), 2)

        promedio = bd.promedio_precio_categoria(" procesadores ")
        self.assertEqual(promedio, 200000.0)

        menor = bd.menor_stock("Procesadores")
        self.assertEqual(menor[1], "Ryzen 7")
        self.assertEqual(menor[3], 2)

    def test_reservar_y_restaurar_stock(self):
        ok, msg, precio = bd.reservar_stock(self.p1.id, 3, self.p1.nombre)
        self.assertTrue(ok)
        self.assertEqual(precio, 150000)

        productos = {fila[0]: fila[3] for fila in bd.mostrar_productos()}
        self.assertEqual(productos[self.p1.id], 2)

        ok_fail, msg_fail, precio_fail = bd.reservar_stock(self.p1.id, 5, self.p1.nombre)
        self.assertFalse(ok_fail)
        self.assertIsNone(precio_fail)

        bd.restaurar_stock(self.p1.id, 3)
        productos = {fila[0]: fila[3] for fila in bd.mostrar_productos()}
        self.assertEqual(productos[self.p1.id], 5)

    def test_vaciar_categoria_e_inventario(self):
        bd.vaciar_categoria("Procesadores")
        restantes = bd.mostrar_productos()
        self.assertEqual(len(restantes), 1)
        self.assertEqual(restantes[0][1], "Mouse Logitech")

        bd.vaciar_inventario()
        self.assertEqual(len(bd.mostrar_productos()), 0)


class TestUsuariosYPermisos(BaseTest):

    def test_registro_y_prevencion_duplicados(self):
        u1 = usuario("julian", "clave123")
        self.assertTrue(u1.guardar_en_bd())

        u_dup = usuario("julian", "otra_clave")
        self.assertFalse(u_dup.guardar_en_bd())

    def test_validar_credenciales(self):
        u = usuario("cristobal", "secreto456", rol="usuario")
        u.guardar_en_bd()

        valido = usuario.validar_credenciales("cristobal", "secreto456")
        self.assertIsNotNone(valido)
        self.assertEqual(valido.nombre, "cristobal")
        self.assertEqual(valido.rol, "usuario")

        self.assertIsNone(usuario.validar_credenciales("cristobal", "malaclave"))
        self.assertIsNone(usuario.validar_credenciales("no_existe", "secreto456"))

    def test_admin_por_defecto_y_convertir_en_admin(self):
        bd_usuarios.crear_admin_por_defecto()
        admin_fila = bd_usuarios.buscar_usuario_por_rut("12.345.678-9")
        self.assertIsNotNone(admin_fila)
        self.assertEqual(admin_fila[1], "admin")
        self.assertEqual(admin_fila[4], "admin")

        u = usuario("sebastian", "pass123")
        u.guardar_en_bd()
        bd_usuarios.convertir_en_admin("sebastian", "19.876.543-2")

        fila_admin = bd_usuarios.buscar_usuario_por_tipo("admin", "19.876.543-2")
        self.assertIsNotNone(fila_admin)
        self.assertEqual(fila_admin[1], "sebastian")
        self.assertEqual(fila_admin[4], "admin")

    def test_control_sesion_en_funcion_botones(self):
        FuncionBotones.cerrar_sesion()
        self.assertFalse(FuncionBotones.hay_usuario_autenticado())
        self.assertFalse(FuncionBotones.validar_sesion())

        FuncionBotones.usuario_actual = "julian"
        self.assertTrue(FuncionBotones.hay_usuario_autenticado())
        self.assertTrue(FuncionBotones.validar_sesion())

        FuncionBotones.cerrar_sesion()
        self.assertIsNone(FuncionBotones.usuario_actual)


class TestBaseDatosCarrito(BaseTest):

    def test_ciclo_completo_bd_carrito(self):
        id_c1 = bd_carrito.obtener_o_crear_carrito("jose")
        id_c2 = bd_carrito.obtener_o_crear_carrito("jose")
        self.assertEqual(id_c1, id_c2)

        bd_carrito.agregar_item("jose", 1, "Teclado", 2, 20000)
        bd_carrito.agregar_item("jose", 1, "Teclado", 1, 20000)
        bd_carrito.agregar_item("jose", 2, "Mouse", 2, 10000)

        items = bd_carrito.items_de_carrito(id_c1)
        self.assertEqual(len(items), 2)

        listado = bd_carrito.listar_carritos()
        self.assertEqual(len(listado), 1)
        self.assertEqual(listado[0][1], "jose")
        self.assertEqual(listado[0][3], "activo")
        self.assertEqual(listado[0][4], 5)
        self.assertEqual(listado[0][5], 80000)

        bd_carrito.quitar_item("jose", 1, 2)
        items_post = dict((i[0], i[2]) for i in bd_carrito.items_de_carrito(id_c1))
        self.assertEqual(items_post[1], 1)

        bd_carrito.quitar_item("jose", 1, 1)
        items_post2 = bd_carrito.items_de_carrito(id_c1)
        self.assertEqual(len(items_post2), 1)
        self.assertEqual(items_post2[0][0], 2)

        bd_carrito.marcar_pagado("jose")
        nuevo_id = bd_carrito.obtener_o_crear_carrito("jose")
        self.assertNotEqual(id_c1, nuevo_id)


class TestClaseCarrito(BaseTest):

    def test_calculos_subtotal_iva_total(self):
        c = Carrito()
        c.procesar_respuesta_reservar(True, "OK", 10, 2, "Monitor", 100000)
        c.procesar_respuesta_reservar(True, "OK", 20, 1, "Teclado", 50000)

        self.assertEqual(c.calcular_subtotal(), 250000)
        self.assertAlmostEqual(c.calcular_iva(), 250000 * 0.19)
        self.assertAlmostEqual(c.calcular_total(), 250000 * 1.19)

    def test_acumular_eliminar_y_vaciar_en_memoria(self):
        c = Carrito()
        c.procesar_respuesta_reservar(True, "OK", 5, 2, "RAM 8GB", 30000)
        c.procesar_respuesta_reservar(True, "OK", 5, 3, "RAM 8GB", 30000)
        self.assertEqual(len(c.items), 1)
        self.assertEqual(c.items[0]["cantidad"], 5)

        c.procesar_respuesta_eliminar(True, 5, 2, "Stock repuesto")
        self.assertEqual(c.items[0]["cantidad"], 3)

        c.procesar_respuesta_eliminar(True, 5, 3, "Stock repuesto")
        self.assertEqual(len(c.items), 0)

        c.procesar_respuesta_reservar(True, "OK", 8, 1, "Mouse", 15000)
        c.procesar_respuesta_vaciar(True, "Carrito vaciado")
        self.assertEqual(len(c.items), 0)


class TestServidorYClienteSockets(BaseTest):

    def setUp(self):
        super().setUp()
        self.prod = Producto("GPU RTX", 400000, 4, "Gaming")
        bd.insertar_producto(self.prod)

    def test_procesar_solicitudes_servidor(self):
        sock_mock = MagicMock()

        def ultima_respuesta():
            raw = sock_mock.sendall.call_args[0][0].decode("utf-8").strip()
            return json.loads(raw)

        servidor.procesar_solicitud(sock_mock, {
            "type": "reservar_stock",
            "id_producto": self.prod.id,
            "cantidad": 3,
            "nombre": self.prod.nombre,
            "nombre_u": "cliente1"
        })
        resp = ultima_respuesta()
        self.assertEqual(resp["type"], "reservar_stock")
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["precio"], 400000)
        self.assertEqual(bd.mostrar_productos()[0][3], 1)

        servidor.procesar_solicitud(sock_mock, {
            "type": "reservar_stock",
            "id_producto": self.prod.id,
            "cantidad": 2,
            "nombre": self.prod.nombre,
            "nombre_u": "cliente1"
        })
        resp_sin_stock = ultima_respuesta()
        self.assertFalse(resp_sin_stock["ok"])

        servidor.procesar_solicitud(sock_mock, {
            "type": "reponer_stock",
            "id_producto": self.prod.id,
            "cantidad": 1,
            "nombre_u": "cliente1"
        })
        resp_rep = ultima_respuesta()
        self.assertTrue(resp_rep["ok"])
        self.assertEqual(bd.mostrar_productos()[0][3], 2)

        servidor.procesar_solicitud(sock_mock, {
            "type": "vaciar_carrito",
            "productos": [{"id_producto": self.prod.id, "cantidad": 2}],
            "nombre_u": "cliente1"
        })
        resp_vac = ultima_respuesta()
        self.assertTrue(resp_vac["ok"])
        self.assertEqual(bd.mostrar_productos()[0][3], 4)
        self.assertEqual(bd_carrito.listar_carritos()[0][4], 0)

    def test_flujo_completo_cliente_servidor_con_hilos(self):
        sock_cliente, sock_servidor = crear_par_sockets()
        carrito_prueba = Carrito()

        cliente_red.conexion = sock_cliente
        cliente_red.conectar_interfaz_reserva(carrito_prueba.procesar_respuesta_reservar)
        cliente_red.conectar_interfaz_reponer(carrito_prueba.procesar_respuesta_eliminar)
        cliente_red.conectar_interfaz_vaciar(carrito_prueba.procesar_respuesta_vaciar)

        hilo_srv = threading.Thread(
            target=servidor.atender_cliente,
            args=(sock_servidor, ("127.0.0.1", 50000)),
            daemon=True
        )
        hilo_cli = threading.Thread(
            target=cliente_red.recibir,
            args=(sock_cliente,),
            daemon=True
        )
        hilo_srv.start()
        hilo_cli.start()

        carrito_prueba.agregar_producto(self.prod, 2, "usuario_red")

        sock_cliente.close()
        hilo_srv.join(timeout=2)
        hilo_cli.join(timeout=2)
        cliente_red.conexion = None

        self.assertEqual(len(carrito_prueba.items), 1)
        self.assertEqual(carrito_prueba.items[0]["id"], self.prod.id)
        self.assertEqual(carrito_prueba.items[0]["cantidad"], 2)
        self.assertEqual(bd.mostrar_productos()[0][3], 2)


class TestValidacionTarjeta(BaseTest):

    def test_solo_digitos_y_reglas_tarjeta(self):
        self.assertTrue(validar_tarjeta.solo_digitos("4345123456789012"))
        self.assertTrue(validar_tarjeta.solo_digitos("123"))
        self.assertFalse(validar_tarjeta.solo_digitos(""))
        self.assertFalse(validar_tarjeta.solo_digitos("4345-1234"))
        self.assertFalse(validar_tarjeta.solo_digitos("4345abcd"))

        self.assertEqual(validar_tarjeta.PREFIJO_TARJETA, "4345")
        self.assertEqual(validar_tarjeta.LARGO_TARJETA, 16)
        self.assertEqual(validar_tarjeta.LARGO_CVV, 3)


class TestVentasYRecibos(BaseTest):

    def test_bd_ventas_insertar_listar_y_detalle(self):
        items_1 = [{"id": 1, "nombre": "Mouse", "cantidad": 2, "precio": 25000.0}]
        items_2 = [{"id": 2, "nombre": "Monitor", "cantidad": 1, "precio": 100000.0}]

        id1 = bd_ventas.insertar_venta("2026-10-23T12:00:00", "juan", 59500.0, items_1)
        id2 = bd_ventas.insertar_venta("2026-10-23T13:30:00", "maria", 119000.0, items_2)

        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)

        ventas = bd_ventas.listar_ventas()
        self.assertEqual(len(ventas), 2)
        self.assertEqual(ventas[0][2], "maria")
        self.assertEqual(ventas[1][2], "juan")

        detalle_1 = bd_ventas.items_de_venta(id1)
        self.assertEqual(len(detalle_1), 1)
        self.assertEqual(detalle_1[0][1], "Mouse")
        self.assertEqual(detalle_1[0][2], 2)
        self.assertEqual(detalle_1[0][4], 50000.0)

    def test_clase_venta_diccionario_bd_y_json(self):
        items_compra = [
            {"id": 1, "nombre": "Mouse Gamer", "cantidad": 2, "precio": 10000},
            {"id": 2, "nombre": "Teclado RGB", "cantidad": 1, "precio": 30000},
        ]
        v = venta("cliente_prueba", items_compra, 50000, 9500, 59500)
        self.assertIsNotNone(v.fecha)
        v.guardar_en_bd()
        self.assertIsNotNone(v.recibo_id)

        dic = v.a_diccionario()
        self.assertEqual(dic["recibo_id"], v.recibo_id)
        self.assertEqual(dic["cliente"], "cliente_prueba")
        self.assertEqual(dic["subtotal"], 50000)
        self.assertEqual(dic["iva"], 9500)
        self.assertEqual(dic["total"], 59500)
        self.assertEqual(len(dic["items"]), 2)
        self.assertEqual(dic["items"][0]["subtotal"], 20000)
        self.assertEqual(dic["items"][1]["subtotal"], 30000)

        ruta_json = v.guardar_json()
        self.recibos_creados.append(ruta_json)
        self.assertTrue(os.path.exists(ruta_json))

        with open(ruta_json, "r", encoding="utf-8") as f:
            datos_leidos = json.load(f)

        self.assertEqual(datos_leidos["recibo_id"], v.recibo_id)
        self.assertEqual(datos_leidos["cliente"], "cliente_prueba")
        self.assertEqual(datos_leidos["total"], 59500)
        self.assertEqual(len(datos_leidos["items"]), 2)

    def test_procesar_compra_desde_carrito_con_servidor(self):
        c = Carrito()
        c.usuario = "cliente_vip"

        ok_vacio, msg_vacio, ruta_vacia = c.procesar_compra("cliente_vip")
        self.assertFalse(ok_vacio)
        self.assertIsNone(ruta_vacia)

        sock_cliente, sock_servidor = crear_par_sockets()
        cliente_red.conexion = sock_cliente
        cliente_red.conectar_interfaz_reserva(c.procesar_respuesta_reservar)
        cliente_red.conectar_interfaz_venta(c.procesar_respuesta_venta)

        hilo_srv = threading.Thread(
            target=servidor.atender_cliente,
            args=(sock_servidor, ("127.0.0.1", 50001)),
            daemon=True
        )
        hilo_cli = threading.Thread(
            target=cliente_red.recibir,
            args=(sock_cliente,),
            daemon=True
        )
        hilo_srv.start()
        hilo_cli.start()

        bd_carrito.agregar_item("cliente_vip", 1, "Monitor LED", 2, 100000)
        c.procesar_respuesta_reservar(True, "OK", 1, 2, "Monitor LED", 100000)

        ok, mensaje, ruta = c.procesar_compra("cliente_vip")
        self.recibos_creados.append(ruta)

        sock_cliente.close()
        hilo_srv.join(timeout=2)
        hilo_cli.join(timeout=2)
        cliente_red.conexion = None

        self.assertTrue(ok)
        self.assertIn("Recibo N°", mensaje)
        self.assertTrue(os.path.exists(ruta))
        self.assertEqual(len(c.items), 0)

        ventas_admin = bd_ventas.listar_ventas()
        self.assertEqual(len(ventas_admin), 1)
        self.assertEqual(ventas_admin[0][2], "cliente_vip")
        items_admin = bd_ventas.items_de_venta(ventas_admin[0][0])
        self.assertEqual(len(items_admin), 1)
        self.assertEqual(items_admin[0][1], "Monitor LED")


if __name__ == "__main__":
    unittest.main()
