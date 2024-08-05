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
from datetime import datetime
import json
# Clase Producto


class Producto:
    def __init__(self, codigo_producto, nombre, precio, cantidad, proveedor):
        self.__codigo_producto = self.validar_codigo_producto(codigo_producto)
        self.__nombre = nombre
        self.__precio = self.validar_precio(precio)
        self.__cantidad = int(cantidad)
        self.__proveedor = proveedor

    @property
    def codigo_producto(self):
        return self.__codigo_producto

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

    def validar_codigo_producto(self, codigo_producto):
        try:
            codigo_str = str(codigo_producto)
            if not codigo_str.isdigit():
                raise ValueError("El código del producto debe ser numérico")
            num_codigo_producto = int(codigo_str)

            if len(codigo_str) != 6:
                raise ValueError("El código de producto debe tener 6 dígitos")

            return num_codigo_producto
        except ValueError as exc:
            raise ValueError(
                "El código debe ser un numérico y compuesto por 6 dígitos") from exc

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
            "codigo": self.codigo_producto,
            "nombre": self.nombre,
            "precio": self.precio,
            "cantidad": self.cantidad,
            "proveedor": self.proveedor
        }

    def __str__(self):
        return f"{self.nombre} {self.precio}"


# Clase Producto Electrónico
class ProductoElectronico(Producto):
    def __init__(self, codigo_producto, nombre, precio, cantidad, proveedor, garantia):
        super().__init__(codigo_producto, nombre, precio, cantidad, proveedor)
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
    def __init__(self, codigo_producto, nombre, precio, cantidad, proveedor, fecha_vencimiento):
        super().__init__(codigo_producto, nombre, precio, cantidad, proveedor)
        self.__fecha_vencimiento = self.validar_fecha_vencimiento(
            fecha_vencimiento)

    @property
    def fecha_vencimiento(self):
        return self.__fecha_vencimiento

    def validar_fecha_vencimiento(self, fecha_vencimiento):
        try:
            dia, mes, año = map(int, fecha_vencimiento.split('/'))
            fecha_venc = datetime(año, mes, dia)
            if fecha_venc < datetime.now():
                raise ValueError(
                    "La fecha de vencimiento debe ser una fecha futura")
            return fecha_venc
        except ValueError as exc:
            raise ValueError("La fecha de vencimiento no es válida") from exc

    def to_dict(self):
        data = super().to_dict()
        data['fecha_vencimiento'] = self.fecha_vencimiento.strftime('%d/%m/%Y')
        return data

# Clase Gestión de Productos


class GestionProductos:
    def __init__(self, archivo):
        self.archivo = archivo

    def leer_datos(self):
        try:
            with open(self.archivo, 'r', encoding='utf-8') as file:
                datos = json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as error:
            raise ValueError(f'Error al decodificar JSON: {error}')
        except Exception as error:
            raise Exception(f'Error al leer datos del archivo: {error}')
        else:
            if not isinstance(datos, dict):
                raise ValueError(
                    'El archivo JSON debe contener un diccionario.')
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
            datos = self.leer_datos()
            codigo_producto = producto.codigo_producto
            if not str(codigo_producto) in datos.keys():
                datos[codigo_producto] = producto.to_dict()
                self.guardar_datos(datos)
                print("Guardado exitoso")
            else:
                print(f'Producto de código {codigo_producto} ya existe')
        except Exception as error:
            print(f'Error inseperado al crear producto: {error}')

    def leer_producto(self, codigo_producto):
        try:
            datos = self.leer_datos()
            codigo_producto = str(codigo_producto)
            print(f'Código de producto buscado: {codigo_producto}')

            if codigo_producto in datos:
                producto_data = datos[codigo_producto]
                print(f'Datos del producto encontrado: {producto_data}')

                if 'fecha_vencimiento' in producto_data:
                    producto = ProductoAlimenticio(
                        codigo_producto=producto_data.get("codigo", None),
                        nombre=producto_data.get("nombre", ""),
                        precio=producto_data.get("precio", 0.0),
                        cantidad=producto_data.get("cantidad", "0"),
                        proveedor=producto_data.get("proveedor", ""),
                        fecha_vencimiento=producto_data.get(
                            "fecha_vencimiento", "")
                    )
                else:
                    producto = ProductoElectronico(
                        codigo_producto=producto_data.get("codigo", None),
                        nombre=producto_data.get("nombre", ""),
                        precio=producto_data.get("precio", 0.0),
                        cantidad=producto_data.get("cantidad", "0"),
                        proveedor=producto_data.get("proveedor", ""),
                        garantia=producto_data.get("garantia", "0")
                    )
                print(f'Producto creado: {producto}')
                return producto
            else:
                print(
                    f'No se encontró el producto con código: {codigo_producto}')
                return None
        except Exception as e:
            print(
                f'Error al leer el producto con código {codigo_producto}: {e}')
            return None

    def actualizar_producto(self, codigo_producto, nuevo_precio):
        try:
            datos = self.leer_datos()
            codigo_producto = str(codigo_producto)
            if str(codigo_producto) in datos.keys():
                datos[codigo_producto]['precio'] = nuevo_precio
                self.guardar_datos(datos)
                print(
                    f'Precio actualizado para el producto código {codigo_producto}')
            else:
                print(f'No se encotró el producto de código {codigo_producto}')
        except Exception as e:
            print(f"Error al actualizar el producto: {e}")

    def eliminar_producto(self, codigo_producto):
        try:
            datos = self.leer_datos()
            codigo_producto = str(codigo_producto)
            if str(codigo_producto) in datos.keys():
                del datos[codigo_producto]
                self.guardar_datos(datos)
                print(
                    f'Producto código: {codigo_producto} eliminado exitosamente')
            else:
                print(f'Producto de código {codigo_producto} no encontrado')
        except Exception as e:
            print(f'Error al eliminar el producto: {e}')
