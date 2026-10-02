import socket
import json
import threading
import sys

HOST = '192.168.1.119'
PORT = 65433

client_socket = None

def conectar_servidor():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print(f"[+] Conectado al servidor {HOST}:{PORT}")

        def receive_data():
            buffer = ""
            while True:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break

                    buffer += data.decode('utf-8')
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if not line.strip():
                            continue

                        request = json.loads(line)

                        # Manejo de intercambio de datos (numero + texto)
                        if request.get('type') == 'respuesta_reserva':
                            estado = request.get('estado')
                            print (f"[Red] Estado de la reserva: {estado}")

                except Exception:
                    break
            print("\n[-] Desconectado del servidor.")
            sys.exit()

        thread_recv = threading.Thread(target=receive_data)
        thread_recv.daemon = True
        thread_recv.start()

    except ConnectionRefusedError:
        print(f"[!] No se pudo conectar al servidor {HOST}:{PORT}. Asegúrate de que el servidor esté en ejecución.")

def enviar_reserva(id_producto, cantidad):
    if client_socket:
        payload = {
            'type': 'reserva',
            'id_producto': id_producto,
            'cantidad': cantidad
        }
        client_socket.sendall((json.dumps(payload) + '\n').encode('utf-8'))
        print(f"[Cliente envía] Reserva solicitada: ID Producto: {id_producto}, Cantidad: {cantidad}")
