import socket
import json
import threading
import sys

HOST = '192.168.1.119'
PORT = 65433

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((HOST, PORT))
            print(f"[+] Conectado al servidor {HOST}:{PORT}")
            print("=" * 50)
            print("FORMATOS DE ENVÍO DISPONIBLES:")
            print("  1. Chat simple: escribe tu mensaje")
            print("  2. Datos (numero,texto): escribe 'datos:20,procesador,valor'")
            print("  3. Salir: escribe 'salir'")
            print("=" * 50)

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
                            if request.get('type') == 'data_exchange':
                                numero = request.get('numero')
                                texto = request.get('texto')
                                valor = request.get('valor')
                                print(f"\n[Servidor envió datos] Número: {numero}, Texto: '{texto}, valor:{valor}'")
                                print("Tu mensaje: ", end="", flush=True)

                            # Manejo de chat simple
                            elif request.get('type') == 'message':
                                print(f"\n[Servidor]: {request.get('content')}")
                                print("Tu mensaje: ", end="", flush=True)

                    except Exception:
                        break
                print("\n[-] Desconectado del servidor.")
                sys.exit()

            thread_recv = threading.Thread(target=receive_data)
            thread_recv.daemon = True
            thread_recv.start()

            while True:
                msg = input("Tu mensaje: ")

                if msg.lower() in ['salir', 'exit', 'quit']:
                    break

                # Detectar si es comando de datos
                if msg.lower().startswith('datos:'):
                    try:
                        # Formato esperado: datos:20,galleta
                        contenido = msg[6:]  # Quitamos 'datos:'
                        partes = contenido.split(',', 2) ## partes = contenido.split(',', 2)  # Cambiado a 2 para permitir tres partes

                        if len(partes) == 3:
                            numero = int(partes[0].strip())
                            texto = partes[1].strip()
                            valor = int(partes[2].strip())

                            payload = {
                                'type': 'data_exchange',
                                'numero': numero,
                                'texto': texto,
                                'valor' : valor
                            }

                            print(f"[Cliente envía] Número: {numero}, Texto: {texto}, valor: {valor}")
                            client_socket.sendall((json.dumps(payload) + '\n').encode('utf-8'))
                        else:
                            print("[!] Formato incorrecto. Usa: datos:numero,texto,valor")

                    except ValueError:
                        print("[!] Error: El número debe ser un entero válido.")

                else:
                    # Mensaje de chat simple
                    payload = {
                        'type': 'message',
                        'content': msg
                    }
                    client_socket.sendall((json.dumps(payload) + '\n').encode('utf-8'))

        except ConnectionRefusedError:
            print("[!] Error: No se pudo conectar al servidor. ¿Está encendido?")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_client()
