class PedidoItem:
    def __init__(self, producto_id, cantidad, precio_unitario, subtotal):
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal

class Pedido:
    def __init__(self, id, cliente_id, items, total):
        self.id = id
        self.cliente_id = cliente_id
        self.items = items  # List of PedidoItem
        self.total = total