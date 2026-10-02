import socket
import json
import threading
import sys
from datos import bd
HOST = '192.168.1.119'
PORT = 65433


def handle_client(conn, addr):
    print(f"\n[+] Conectado por {addr}")
    
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
                    if request.get('type') == 'reserva':
                        id_producto = request.get('id_producto')
                        cantidad = request.get('cantidad')
                        print(f"[Servidor recibe] Reserva solicitada: ID Producto: {id_producto}, Cantidad: {cantidad}")
                    
                    #exito = bd.reservar_stock(id_producto, cantidad)
                    exito = True 
                    if exito:
                        response = {
                            'type': 'respuesta_reserva',
                            'estado': 'ok'
                        } 
                    else:
                        response = {
                            'type': 'respuesta_reserva',
                            'estado': 'sin_stock'
                        }

            except json.JSONDecodeError:
                print("\n[!] Error decodificando JSON.")
            except ConnectionResetError:
                break
            except Exception as e:
                break

        conn.close()
        print("\n[-] El cliente se ha desconectado.")

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
