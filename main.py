import os
import platform

from gestion_productos import (ProductoAlimenticio, ProductoElectronico, GestionProductos
                               )


def limpiar_pantalla():
    '''Limpiar la pantalla según el sistema operativo'''
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')  # Para MacOs


def mostrar_menu():
    print("=======Menú de Gestión de Productos========")
    print("1. Agregar Producto Alimenticio")
    print("2. Agregar Producto Electrónico")
    print('3. Buscar Producto por código')


def agregar_producto(gestion, tipo_producto):
    try:
        nombre = input("Ingrese el nombre del producto: ")
        precio = input("Ingrese el precio del producto (unidad): ")
        cantidad = input("Ingrese la cantidad en stock del producto: ")
        proveedor = input("Ingrese el nombre del proveedor: ")

        if tipo_producto == '1':
            fecha_vencimiento = input(
                "Ingrese la fecha de vencimiento del producto en el formato dd/mm/yyyy: ")
            producto = ProductoAlimenticio(
                nombre, precio, cantidad, proveedor, fecha_vencimiento)
        elif tipo_producto == '2':
            garantia = input(
                "Ingrese la cantidad de años de garantía del producto: ")
            producto = ProductoElectronico(
                nombre, precio, cantidad, proveedor, garantia)
        else:
            print("Opción inválida")
            return

        gestion.crear_producto(producto)
        print('Presione Enter para continuar')

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


def buscar_producto_por_codigo(gestion):
    codigo_producto = input(
        'Ingrese el código del producto que desea buscar: ')
    gestion.leer_producto(codigo_producto)
    input('Presione Enter para continuar')


def actualizar_precio_producto(gestion):
    codigo_producto = input(
        'Ingrese el código del producto cuyo precio desea actualizar: ')
    precio = float(input('Ingrese el precio del preoducto'))
    gestion.actualizar_producto(codigo_producto, precio)
    input('Presione Enter para continuar')


def eliminar_producto_por_codigo(gestion):
    codigo_producto = input(
        'Ingrese el código del producto que desea eliminar: ')
    gestion.eliminar_producto(codigo_producto)
    input('Presione la tecla Enter para continuar')


def mostrar_todos_los_productos(gestion):
    for producto in gestion.leer_datos().values():
        if 'fecha_vencimiento' in producto:
            print(
                f"{producto['nombre']} - Fecha de vencimiento {producto['fecha_vencimiento']}")
        else:
            print(
                f"{producto['nombre']} - Años de Garantía: {producto['garantia']}")


if __name__ == "__main__":
    gestion = GestionProductos()
    while True:
        mostrar_menu()
        opcion = input('Seleccione una opción: ')

        if opcion == '1' or opcion == '2':
            agregar_producto(gestion, opcion)

        elif opcion == '3':
            buscar_producto_por_codigo(gestion)

        else:
            print('Opción no válida')
