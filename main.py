from datos import bd
from clases.inventario import Inventario


def main():
    bd.crear_tabla()

    inventario = Inventario()

    print("Sistema iniciado correctamente")
    print(f"Productos cargados: {len(inventario.productos)}")


if __name__ == "__main__":
    main()