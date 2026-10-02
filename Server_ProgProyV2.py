import socket
import json
import threading
import sys
from clases.producto import Producto
from clases.inventario import Inventario

HOST = '192.168.1.119'
PORT = 65433


def handle_client(conn, addr):
    print(f"\n[+] Conectado por {addr}")
    print("=" * 50)
    print("FORMATOS DE ENVÍO DISPONIBLES:")
    print("  1. Chat simple: escribe tu mensaje")
    print("  2. Datos (numero,texto): escribe 'datos:30,procesador,valor'")
    print("  3. Salir: escribe 'salir'")
    print("=" * 50)

    def receive_data():
        buffer = ""
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break

                buffer += data.decode('utf-8')

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if not line.strip():
                        continue

                    request = json.loads(line)

                    # Manejo de intercambio de datos (numero + texto)
                    if request.get('type') == 'data_exchange':
                        numero = request.get('numero')
                        texto = request.get('texto')
                        valor = request.get('valor')
                        print(f"\n[Cliente envió datos] Número: {numero}, Texto: '{texto}, valor: {valor}'")
                        print("Tu mensaje: ", end="", flush=True)

                    # Manejo de chat simple
                    elif request.get('type') == 'message':
                        print(f"\n[Cliente]: {request.get('content')}")
                        print("Tu mensaje: ", end="", flush=True)

            except json.JSONDecodeError:
                print("\n[!] Error decodificando JSON.")
            except ConnectionResetError:
                break
            except Exception as e:
                break

        conn.close()
        print("\n[-] El cliente se ha desconectado.")
        sys.exit()

    thread_recv = threading.Thread(target=receive_data)
    thread_recv.daemon = True
    thread_recv.start()

    try:
        while True:
            msg = input("Tu mensaje: ")

            if msg.lower() in ['salir', 'exit', 'quit']:
                print("Cerrando conexión...")
                break

            # Detectar si es comando de datos
            if msg.lower().startswith('datos:'):
                try:
                    # Formato esperado: datos:30,pan
                    contenido = msg[6:]  # Quitamos 'datos:'
                    partes = contenido.split(',',2)

                    if len(partes) == 2:
                        numero = int(partes[0].strip())
                        texto = partes[1].strip()
                        valor = int(partes[2].strip())

                        response = {
                            'type': 'data_exchange',
                            'numero': numero,
                            'texto': texto,
                            'valor' : valor
                        }

                        print(f"[Servidor envía] Número: {numero}, Texto: '{texto}', valor {valor}")
                        conn.sendall((json.dumps(response) + '\n').encode('utf-8'))
                    else:
                        print("[!] Formato incorrecto. Usa: datos:numero,texto")

                except ValueError:
                    print("[!] Error: El número debe ser un entero válido.")

            else:
                # Mensaje de chat simple
                response = {
                    'type': 'message',
                    'content': msg
                }
                conn.sendall((json.dumps(response) + '\n').encode('utf-8'))

    except KeyboardInterrupt:
        print("\nInterrupción detectada.")
    finally:
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Servidor Python escuchando en {HOST}:{PORT} ...")
        print("Esperando conexión de un cliente...")

        conn, addr = server_socket.accept()
        handle_client(conn, addr)

if __name__ == "__main__":
    start_server()
