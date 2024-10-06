'''
Desafío 1: Sistema de Gestión de Productos
    Objetivo: Desarrollar un sistema para manejar productos en un inventario
    Requisitos:
    - Crear una clase base Producto con atributos como nombre, precio, cantidad en stock, etc.
    - Definir al menos 2 clases derivadas para diferentes categorías de productos (por ejemplo, ProductoElectronico, ProductoAlimenticio) con atributos y métodos específicos.
    - Implementar operaciones CRUD para gestionar productos del inventario.
    - Manejar errores con bloques try-except para validar entradas y gestionar excepciones.
    - Persistir los datos en archivo JSON.
'''
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error
from decouple import config
import json
# Clase Producto


class Producto:
    def __init__(self, nombre, precio, cantidad, proveedor):
        self.__nombre = nombre
        self.__precio = self.validar_precio(precio)
        self.__cantidad = int(cantidad)
        self.__proveedor = proveedor

    @property
    def nombre(self):
        return self.__nombre

    @property
    def precio(self):
        return self.__precio

    @property
    def cantidad(self):
        return self.__cantidad

    @property
    def proveedor(self):
        return self.__proveedor

    @precio.setter
    def precio(self, nuevo_precio):
        self.__precio = self.validar_precio(nuevo_precio)

    def validar_precio(self, precio):
        try:
            precio_num = float(precio)
            if precio_num < 0:
                raise ValueError("El precio debe ser un número positivo")
            return precio_num
        except ValueError as exc:
            raise ValueError("El precio debe ser un número válido") from exc

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "precio": self.precio,
            "cantidad": self.cantidad,
            "proveedor": self.proveedor
        }

    def __str__(self):
        return f"{self.nombre} {self.precio}"


# Clase Producto Electrónico
class ProductoElectronico(Producto):
    def __init__(self, nombre, precio, cantidad, proveedor, garantia):
        super().__init__(nombre, precio, cantidad, proveedor)
        self.__garantia = garantia

    @property
    def garantia(self):
        return self.__garantia

    def validar_garantia(self, garantia):
        try:
            anio_garantia = int(garantia)
            if anio_garantia < 0:
                raise ValueError(
                    "Los años de garantía deben ser un número positivo")
            return anio_garantia
        except ValueError as exc:
            raise ValueError(
                "La garantía debe estar expresada en años y ser un número entero") from exc

    def to_dict(self):
        data = super().to_dict()
        data['garantia'] = self.garantia
        return data

    def __str__(self):
        return f"{super().__str__()} - Garantía: {self.__garantia}"


# Clase Producto Alimenticio

class ProductoAlimenticio(Producto):
    def __init__(self, nombre, precio, cantidad, proveedor, fecha_vencimiento):
        super().__init__(nombre, precio, cantidad, proveedor)
        self.__fecha_vencimiento = self.validar_fecha_vencimiento(
            fecha_vencimiento)

    @property
    def fecha_vencimiento(self):
        return self.__fecha_vencimiento

    def validar_fecha_vencimiento(self, fecha_vencimiento):
        try:
            if isinstance(fecha_vencimiento, str):

                dia, mes, año = map(int, fecha_vencimiento.split('/'))
                fecha_venc = datetime(año, mes, dia).date()
            elif isinstance(fecha_vencimiento, date):

                fecha_venc = fecha_vencimiento
            else:
                raise ValueError("El formato de fecha no es válido")

            if fecha_venc < datetime.now().date():
                raise ValueError(
                    "La fecha de vencimiento debe ser una fecha futura")
            return fecha_venc
        except ValueError as exc:
            raise ValueError("La fecha de vencimiento no es válida") from exc

    def to_dict(self):
        data = super().to_dict()
        data['fecha_vencimiento'] = self.fecha_vencimiento.strftime('%Y-%m-%d')
        return data

# Clase Gestión de Productos


class GestionProductos:
    def __init__(self):
        self.host = config('DB_HOST')
        self.database = config('DB_NAME')
        self.user = config('DB_USER')
        self.password = config('DB_PASSWORD')
        self.port = config('DB_PORT')

    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            if connection.is_connected():
                return connection

        except Error as e:
            print(f'Error al conectar a la Base de Datos: {e}')
            return None

    def leer_datos(self):
        try:
            with open(self.archivo, 'r') as file:
                datos = json.load(file)
        except FileNotFoundError:
            return {}
        except Exception as error:
            raise Exception(f'Error al leer datos del archivo: {error}')
        else:
            return datos

    def guardar_datos(self, datos):
        try:
            with open(self.archivo, 'w', encoding='utf-8') as file:
                json.dump(datos, file, indent=4)
        except IOError as error:
            print(
                f'Error al intentar guardar los datos en {self.archivo}: {error}')
        except Exception as error:
            print(f'Error inesperado: {error}')

    def crear_producto(self, producto):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor() as cursor:
                    query = '''
                    INSERT INTO productos (nombre, precio, cantidad, proveedor)
                    VALUES (%s, %s, %s, %s)
                    '''
                    cursor.execute(
                        query, (producto.nombre, producto.precio, producto.cantidad, producto.proveedor))

                    codigo_producto = cursor.lastrowid

                    if isinstance(producto, ProductoAlimenticio):
                        query = '''
                        INSERT INTO productoAlimenticio (codigo_producto, fecha_vencimiento)
                        VALUES (%s, %s)
                        '''
                        cursor.execute(
                            query, (codigo_producto, producto.fecha_vencimiento))

                    elif isinstance(producto, ProductoElectronico):
                        query = '''
                        INSERT INTO productoElectronico (codigo_producto, garantia)
                        VALUES (%s, %s)
                        '''
                        cursor.execute(
                            query, (codigo_producto, producto.garantia))

                connection.commit()
                print(f'Producto {producto.nombre} creado correctamente')

        except Exception as error:
            print(f'Error inesperado al crear producto: {error}')

    def leer_producto(self, codigo_producto):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        'SELECT * FROM productos WHERE codigo_producto = %s', (codigo_producto,))
                    producto_data = cursor.fetchone()

                    if producto_data:
                        if 'codigo_producto' in producto_data:
                            del producto_data['codigo_producto']
                        cursor.execute(
                            'SELECT fecha_vencimiento FROM productoAlimenticio WHERE codigo_producto = %s ', (codigo_producto,))
                        fecha_vencimiento = cursor.fetchone()

                        if fecha_vencimiento:
                            producto_data['fecha_vencimiento'] = fecha_vencimiento['fecha_vencimiento']
                            producto = ProductoAlimenticio(**producto_data)

                        else:
                            cursor.execute(
                                'SELECT garantia FROM productoElectronico WHERE codigo_producto = %s ', (codigo_producto,))
                            garantia = cursor.fetchone()
                            if garantia:
                                producto_data['garantia'] = garantia['garantia']
                                producto = ProductoElectronico(**producto_data)
                            else:
                                producto = Producto(**producto_data)

                        print(f'Producto encontrado: {producto}')

                    else:
                        print(
                            f'No se encotró el producto de código: {codigo_producto}')
        except Exception as e:
            print(
                f'Error al leer el producto con código {codigo_producto}: {e}')
        finally:
            if connection.is_connected():
                connection.close()

    def actualizar_producto(self, codigo_producto, nuevo_precio):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'SELECT * FROM productos WHERE codigo_producto: %s', (codigo_producto))
                    if not cursor.fetchone():
                        print(
                            f'No se encontró el producto con código: {codigo_producto}')
                        return

                    cursor.execute(
                        "UPDATE productos SET precio = %s WHERE codigo_producto = %s", (nuevo_precio, codigo_producto))
                    if cursor.rowcount > 0:
                        connection.commit()
                        print(
                            f'Precio actualizado para el producto de código: {codigo_producto}')
                    else:
                        print(
                            f'No se encontró el producto con código: {codigo_producto}')

        except Exception as e:
            print(f"Error al actualizar el producto: {e}")
        finally:
            if connection.is_connected():
                connection.close()

    def eliminar_producto(self, codigo_producto):
        try:
            connection = self.connect()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'SELECT * FROM productos WHERE codigo_producto = %s', (codigo_producto,))
                    if not cursor.fetchone():
                        print(
                            f'No se encontró el producto con código: {codigo_producto}')
                        return

                    cursor.execute(
                        'DELETE FROM productoAlimenticio WHERE codigo_producto = %s', (codigo_producto,))
                    cursor.execute(
                        'DELETE FROM productoElectronico WHERE codigo_producto = %s', (codigo_producto,))
                    cursor.execute(
                        'DELETE FROM productos WHERE codigo_producto = %s', (codigo_producto,))
                    if cursor.rowcount > 0:
                        connection.commit()
                        print(
                            f'Producto con código {codigo_producto} eliminado correctamente')
                    else:
                        print(
                            f'Producto con código {codigo_producto} no encontrado')
        except Exception as e:
            print(f'Error al eliminar el producto: {e}')
        finally:
            if connection.is_connected():
                connection.close()
