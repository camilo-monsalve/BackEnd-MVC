from models.model_pedidos import Pedido, PedidoItem
from controller.client_controller import ClienteController
from controller.productos_controller import ProductoController
import json
import os

class PedidoController:
    def __init__(self, cliente_controller, producto_controller):
        self.pedidos = []
        self.cliente_controller = cliente_controller
        self.producto_controller = producto_controller
        self.file_path = "pedidos.json"
        self.load_data()

    def load_data(self):
        """Load pedidos from JSON file if it exists."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.pedidos = [
                        Pedido(
                            p['id'],
                            p['cliente_id'],
                            [PedidoItem(**item) for item in p['items']],
                            p['total']
                        ) for p in data
                    ]
            except Exception as e:
                print(f"Error loading pedidos.json: {e}")

    def save_data(self):
        """Save pedidos to JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump([{
                    'id': p.id,
                    'cliente_id': p.cliente_id,
                    'items': [{
                        'producto_id': item.producto_id,
                        'cantidad': item.cantidad,
                        'precio_unitario': item.precio_unitario,
                        'subtotal': item.subtotal
                    } for item in p.items],
                    'total': p.total
                } for p in self.pedidos], file, indent=4)
        except Exception as e:
            print(f"Error saving pedidos.json: {e}")

    def get_all(self):
        return self.pedidos

    def add(self, id, cliente_id, items):
        cliente = next((c for c in self.cliente_controller.get_client() if c.id == cliente_id), None)
        if not cliente:
            print("Cliente no encontrado")
            return False
        total = 0
        validated_items = []
        for item in items:
            producto = self.producto_controller.find_by_id(item['producto_id'])
            if not producto:
                print(f"Producto {item['producto_id']} no encontrado")
                return False
            if producto.stock < item['cantidad'] or item['cantidad'] <= 0:
                print(f"Stock insuficiente o cantidad inválida para producto {producto.nombre}")
                return False
            subtotal = item['cantidad'] * producto.precio
            total += subtotal
            validated_items.append(PedidoItem(producto.id, item['cantidad'], producto.precio, subtotal))
            producto.stock -= item['cantidad']
        pedido = Pedido(id, cliente_id, validated_items, total)
        self.pedidos.append(pedido)
        self.producto_controller.save_data()  # Save updated product stock
        self.save_data()
        return True

    def update(self, id, items):
        pedido = next((p for p in self.pedidos if p.id == id), None)
        if not pedido:
            print("Pedido no encontrado")
            return False
        for item in pedido.items:
            producto = self.producto_controller.find_by_id(item.producto_id)
            if producto:
                producto.stock += item.cantidad
        total = 0
        new_items = []
        for item in items:
            producto = self.producto_controller.find_by_id(item['producto_id'])
            if not producto:
                print(f"Producto {item['producto_id']} no encontrado")
                return False
            if producto.stock < item['cantidad'] or item['cantidad'] <= 0:
                print(f"Stock insuficiente o cantidad inválida para producto {producto.nombre}")
                return False
            subtotal = item['cantidad'] * producto.precio
            total += subtotal
            new_items.append(PedidoItem(producto.id, item['cantidad'], producto.precio, subtotal))
            producto.stock -= item['cantidad']
        pedido.items = new_items
        pedido.total = total
        self.producto_controller.save_data()  # Save updated product stock
        self.save_data()
        return True

    def delete(self, id):
        pedido = next((p for p in self.pedidos if p.id == id), None)
        if pedido:
            for item in pedido.items:
                producto = self.producto_controller.find_by_id(item.producto_id)
                if producto:
                    producto.stock += item.cantidad
            self.pedidos = [p for p in self.pedidos if p.id != id]
            self.producto_controller.save_data()  # Save updated product stock
            self.save_data()

    def find_by_id(self, id):
        return next((p for p in self.pedidos if p.id == id), None)