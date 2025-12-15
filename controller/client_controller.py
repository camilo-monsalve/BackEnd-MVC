from models.client_model import Client
import json
import os

class ClienteController:
    def __init__(self):
        self.clientes = []
        self.file_path = "clientes.json"
        self.load_data()

    def load_data(self):
        """Load clients from JSON file if it exists."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.clientes = [Client(**client) for client in data]
            except Exception as e:
                print(f"Error loading clientes.json: {e}")

    def save_data(self):
        """Save clients to JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump([{
                    'id': c.id,
                    'rut': c.rut,
                    'nombre': c.nombre,
                    'apellido': c.apellido,
                    'email': c.email,
                    'telefono': c.telefono,
                    'direccion': c.direccion
                } for c in self.clientes], file, indent=4)
        except Exception as e:
            print(f"Error saving clientes.json: {e}")

    def get_client(self):
        return self.clientes

    def add_client(self, id, nombre, email, telefono, direccion, apellido, rut):
        for cliente in self.clientes:
            if cliente.rut == rut:
                print(f"Este cliente ya está en la lista: {cliente.rut} {cliente.nombre} {cliente.apellido}")
                return False
        client = Client(id, nombre, email, telefono, direccion, apellido, rut)
        self.clientes.append(client)
        self.save_data()
        return True

    def delete_client(self, id):
        self.clientes = [client for client in self.clientes if client.id != id]
        self.save_data()

    def update_client(self, id, nombre, email, telefono, direccion, apellido, rut):
        for cliente in self.clientes:
            if cliente.id == id:
                cliente.rut = rut
                cliente.nombre = nombre
                cliente.apellido = apellido
                cliente.email = email
                cliente.telefono = telefono
                cliente.direccion = direccion
                self.save_data()
                return True
        return False
