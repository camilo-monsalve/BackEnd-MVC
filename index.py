from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import urllib.parse
import socket
from controller.client_controller import ClienteController
from controller.productos_controller import ProductoController
from controller.pedidos_controller import PedidoController

clienteControlador = ClienteController()
productoControlador = ProductoController()
pedidoControlador = PedidoController(clienteControlador, productoControlador)

class MyHandler(BaseHTTPRequestHandler):
    def render_template(self, template_name, context):
        with open(f'view/{template_name}', 'r', encoding='utf-8') as file:
            html_content = file.read()
            for key, value in context.items():
                html_content = html_content.replace(f"{{{{{key}}}}}", value)
            return html_content

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            clientes = clienteControlador.get_client()
            lista_clientes = "".join(
                f"<tr>"
                f"<td>{cliente.id}</td>"
                f"<td>{cliente.rut}</td>"
                f"<td>{cliente.nombre}</td>"
                f"<td>{cliente.apellido}</td>"
                f"<td>{cliente.email}</td>"
                f"<td>{cliente.telefono}</td>"
                f"<td>{cliente.direccion}</td>"
                f"<td>"
                f"<a href='/delete?id={cliente.id}'>Eliminar</a> | "
                f"<a href='/update?id={cliente.id}'>Actualizar</a>"
                f"</td>"
                f"</tr>"
                for cliente in clientes
            )
            html_content = self.render_template('index.html', {'clientes': lista_clientes})
            self.wfile.write(html_content.encode())
            return

        elif path == "/update":
            query = urllib.parse.parse_qs(parsed_path.query)
            id = int(query['id'][0])
            client = next((c for c in clienteControlador.get_client() if c.id == id), None)
            if client:
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                html_content = self.render_template('update.html', {
                    'client_id': str(client.id),
                    'client_name': client.nombre,
                    'client_email': client.email,
                    'client_fono': client.telefono,
                    'client_direc': client.direccion,
                    'client_apell': client.apellido,
                    'client_rut': client.rut
                })
                self.wfile.write(html_content.encode())
            else:
                self.send_response(404)
                self.end_headers()
            return

        elif path == "/delete":
            query = urllib.parse.parse_qs(parsed_path.query)
            id = int(query['id'][0])
            clienteControlador.delete_client(id)
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            return

        elif path == "/productos":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            productos = productoControlador.get_all()
            lista_productos = "".join(
                f"<tr>"
                f"<td>{producto.id}</td>"
                f"<td>{producto.sku}</td>"
                f"<td>{producto.nombre}</td>"
                f"<td>{producto.precio}</td>"
                f"<td>{producto.stock}</td>"
                f"<td>{producto.categoria}</td>"
                f"<td>"
                f"<a href='/productos/delete?id={producto.id}'>Eliminar</a> | "
                f"<a href='/productos/update?id={producto.id}'>Actualizar</a>"
                f"</td>"
                f"</tr>"
                for producto in productos
            )
            html_content = self.render_template('productos.html', {'productos': lista_productos})
            self.wfile.write(html_content.encode())
            return

        elif path == "/productos/update":
            query = urllib.parse.parse_qs(parsed_path.query)
            id = int(query['id'][0])
            producto = productoControlador.find_by_id(id)
            if producto:
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                html_content = self.render_template('productos_update.html', {
                    'producto_id': str(producto.id),
                    'producto_sku': producto.sku,
                    'producto_nombre': producto.nombre,
                    'producto_precio': str(producto.precio),
                    'producto_stock': str(producto.stock),
                    'producto_categoria': producto.categoria
                })
                self.wfile.write(html_content.encode())
            else:
                self.send_response(404)
                self.end_headers()
            return

        elif path == "/productos/delete":
            query = urllib.parse.parse_qs(parsed_path.query)
            id = int(query['id'][0])
            productoControlador.delete(id)
            self.send_response(303)
            self.send_header('Location', '/productos')
            self.end_headers()
            return

        elif path == "/pedidos":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            pedidos = pedidoControlador.get_all()
            clientes = clienteControlador.get_client()
            lista_pedidos = "".join(
                f"<tr>"
                f"<td>{pedido.id}</td>"
                f"<td>{next((c.nombre + ' ' + c.apellido for c in clientes if c.id == pedido.cliente_id), 'Desconocido')}</td>"
                f"<td>{len(pedido.items)}</td>"
                f"<td>{pedido.total}</td>"
                f"<td>"
                f"<a href='/pedidos/delete?id={pedido.id}'>Eliminar</a> | "
                f"<a href='/pedidos/update?id={pedido.id}'>Actualizar</a>"
                f"</td>"
                f"</tr>"
                for pedido in pedidos
            )
            productos_options = "".join(
                f"<option value='{p.id}'>{p.nombre} (SKU: {p.sku})</option>"
                for p in productoControlador.get_all()
            )
            html_content = self.render_template('pedidos.html', {
                'pedidos': lista_pedidos,
                'productos_options': productos_options
            })
            self.wfile.write(html_content.encode())
            return

        elif path == "/pedidos/update":
            query = urllib.parse.parse_qs(parsed_path.query)
            id = int(query['id'][0])
            pedido = pedidoControlador.find_by_id(id)
            if pedido:
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                productos_options = "".join(
                    f"<option value='{p.id}'>{p.nombre} (SKU: {p.sku})</option>"
                    for p in productoControlador.get_all()
                )
                item_1_cantidad = str(pedido.items[0].cantidad) if len(pedido.items) > 0 else ""
                item_2_cantidad = str(pedido.items[1].cantidad) if len(pedido.items) > 1 else ""
                item_3_cantidad = str(pedido.items[2].cantidad) if len(pedido.items) > 2 else ""
                html_content = self.render_template('pedidos_update.html', {
                    'pedido_id': str(pedido.id),
                    'pedido_cliente_id': str(pedido.cliente_id),
                    'productos_options': productos_options,
                    'item_1_cantidad': item_1_cantidad,
                    'item_2_cantidad': item_2_cantidad,
                    'item_3_cantidad': item_3_cantidad
                })
                self.wfile.write(html_content.encode())
            else:
                self.send_response(404)
                self.end_headers()
            return

        elif path == "/pedidos/delete":
            query = urllib.parse.parse_qs(parsed_path.query)
            id = int(query['id'][0])
            pedidoControlador.delete(id)
            self.send_response(303)
            self.send_header('Location', '/pedidos')
            self.end_headers()
            return

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = urllib.parse.parse_qs(post_data)

        if path == "/":
            id = len(clienteControlador.get_client()) + 1
            nombre = parsed_data['nombre'][0]
            email = parsed_data['email'][0]
            telefono = parsed_data['telefono'][0]
            direccion = parsed_data['direccion'][0]
            apellido = parsed_data['apellido'][0]
            rut = parsed_data['rut'][0]
            clienteControlador.add_client(id, nombre, email, telefono, direccion, apellido, rut)
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            return

        elif path == "/update":
            id = int(parsed_data['id'][0])
            nombre = parsed_data['nombre'][0]
            email = parsed_data['email'][0]
            telefono = parsed_data['telefono'][0]
            direccion = parsed_data['direccion'][0]
            apellido = parsed_data['apellido'][0]
            rut = parsed_data['rut'][0]
            clienteControlador.update_client(id, nombre, email, telefono, direccion, apellido, rut)
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            return

        elif path == "/productos":
            id = len(productoControlador.get_all()) + 1
            sku = parsed_data['sku'][0]
            nombre = parsed_data['nombre'][0]
            precio = float(parsed_data['precio'][0])
            stock = int(parsed_data['stock'][0])
            categoria = parsed_data['categoria'][0]
            productoControlador.add(id, sku, nombre, precio, stock, categoria)
            self.send_response(303)
            self.send_header('Location', '/productos')
            self.end_headers()
            return

        elif path == "/productos/update":
            id = int(parsed_data['id'][0])
            sku = parsed_data['sku'][0]
            nombre = parsed_data['nombre'][0]
            precio = float(parsed_data['precio'][0])
            stock = int(parsed_data['stock'][0])
            categoria = parsed_data['categoria'][0]
            productoControlador.update(id, sku, nombre, precio, stock, categoria)
            self.send_response(303)
            self.send_header('Location', '/productos')
            self.end_headers()
            return

        elif path == "/pedidos":
            id = len(pedidoControlador.get_all()) + 1
            cliente_id = int(parsed_data['cliente_id'][0])
            items = []
            for i in range(1, 4):
                producto_key = f'producto_{i}'
                cantidad_key = f'cantidad_{i}'
                if producto_key in parsed_data and cantidad_key in parsed_data:
                    producto_id = int(parsed_data[producto_key][0])
                    cantidad = int(parsed_data[cantidad_key][0])
                    if cantidad > 0:
                        items.append({'producto_id': producto_id, 'cantidad': cantidad})
            if items:
                pedidoControlador.add(id, cliente_id, items)
            self.send_response(303)
            self.send_header('Location', '/pedidos')
            self.end_headers()
            return

        elif path == "/pedidos/update":
            id = int(parsed_data['id'][0])
            cliente_id = int(parsed_data['cliente_id'][0])
            items = []
            for i in range(1, 4):
                producto_key = f'producto_{i}'
                cantidad_key = f'cantidad_{i}'
                if producto_key in parsed_data and cantidad_key in parsed_data:
                    producto_id = int(parsed_data[producto_key][0])
                    cantidad = int(parsed_data[cantidad_key][0])
                    if cantidad > 0:
                        items.append({'producto_id': producto_id, 'cantidad': cantidad})
            if items:
                pedidoControlador.update(id, items)
            self.send_response(303)
            self.send_header('Location', '/pedidos')
            self.end_headers()
            return

PORT = 8000

def _lan_ip_fallback_loopback() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# No need to populate example data, as it will be loaded from JSON files if they exist

with HTTPServer(("", PORT), MyHandler) as httpd:
    served_dir = os.getcwd()
    local_url = f"http://localhost:{PORT}/"
    lan_url = f"http://{_lan_ip_fallback_loopback()}:{PORT}/"
    print("Servidor HTTP iniciado (Ctrl+C para detener):")
    print(f"  Local:   {local_url}")
    print(f"  En LAN:  {lan_url}")
    print(f"  Carpeta base (cwd): {served_dir}")
    print("  Rutas útiles:")
    print("   - Clientes:         /")
    print("   - Productos:        /productos")
    print("   - Pedidos:          /pedidos")
    print("   - Actualizar Cliente: /update?id=1")
    print("   - Eliminar Cliente:  /delete?id=1")
    print("   - Actualizar Producto: /productos/update?id=1")
    print("   - Eliminar Producto:  /productos/delete?id=1")
    print("   - Actualizar Pedido: /pedidos/update?id=1")
    print("   - Eliminar Pedido:  /pedidos/delete?id=1")
    httpd.serve_forever()

# === Documento breve: Decisiones de validación y manejo de stock ===
"""
Decisiones de validación y manejo de stock:
1. **Validaciones**:
   - Productos: Se valida que el SKU sea único y que precio > 0, stock >= 0, y los campos de texto no estén vacíos.
   - Pedidos: Se verifica la existencia del cliente, la validez de los productos, y que el stock sea suficiente. Cantidades deben ser > 0.
2. **Manejo de stock**:
   - Al crear o actualizar un pedido, se decrementa el stock de los productos correspondientes.
   - Al actualizar un pedido, se repone el stock de los ítems originales antes de aplicar los nuevos.
   - Al eliminar un pedido, se repone el stock de todos los ítems asociados.
3. **Casos de prueba**:
   - Crear 15 productos con SKUs únicos y verificar lista en /productos.
   - Crear 10 pedidos con 1-2 ítems, comprobando que el stock se reduce y el total se calcula correctamente.
   - Actualizar un producto y verificar que los datos persisten.
   - Actualizar un pedido, cambiando cantidades y productos, y verificar el ajuste de stock.
   - Eliminar productos y pedidos, asegurando que el stock se repone correctamente.
   - Intentar crear pedidos con stock insuficiente o datos inválidos para confirmar que se rechazan.
"""