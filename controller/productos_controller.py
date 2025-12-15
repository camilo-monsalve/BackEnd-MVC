from models.model_productos import Producto
import json
import os

class ProductoController:
    def __init__(self):
        self.productos = []
        self.file_path = "productos.json"
        self.load_data()

    def load_data(self):
        """Load products from JSON file if it exists."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.productos = [Producto(**product) for product in data]
            except Exception as e:
                print(f"Error loading productos.json: {e}")

    def save_data(self):
        """Save products to JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump([{
                    'id': p.id,
                    'sku': p.sku,
                    'nombre': p.nombre,
                    'precio': p.precio,
                    'stock': p.stock,
                    'categoria': p.categoria
                } for p in self.productos], file, indent=4)
        except Exception as e:
            print(f"Error saving productos.json: {e}")

    def get_all(self):
        return self.productos

    def add(self, id, sku, nombre, precio, stock, categoria):
        for producto in self.productos:
            if producto.sku == sku:
                print(f"Este producto ya está en la lista: {sku}")
                return False
        if not all([sku, nombre, categoria]) or precio <= 0 or stock < 0:
            print("Datos inválidos para el producto")
            return False
        producto = Producto(id, sku, nombre, precio, stock, categoria)
        self.productos.append(producto)
        self.save_data()
        return True

    def update(self, id, sku, nombre, precio, stock, categoria):
        for producto in self.productos:
            if producto.id == id:
                if any(p.sku == sku and p.id != id for p in self.productos):
                    print(f"SKU {sku} ya existe")
                    return False
                if not all([sku, nombre, categoria]) or precio <= 0 or stock < 0:
                    print("Datos inválidos para actualizar producto")
                    return False
                producto.sku = sku
                producto.nombre = nombre
                producto.precio = precio
                producto.stock = stock
                producto.categoria = categoria
                self.save_data()
                return True
        return False

    def delete(self, id):
        self.productos = [p for p in self.productos if p.id != id]
        self.save_data()

    def find_by_id(self, id):
        return next((p for p in self.productos if p.id == id), None)