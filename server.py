import json
import time
import shutil
import socket
import os

class Blueprint:
    defs = {}
    pre = ""

    def __init__(self, main_route=""):
        self.pre = main_route

    def route(self, route):
        def decorator(fun):
            self.defs[self.pre + "/" + route] = fun
            def wrapper(*args, **kwargs):
                return fun(*args, **kwargs)
            return wrapper
        return decorator

class API(Blueprint):
    server_socket: socket.socket
    HOST: str
    PORT: int
    closed: bool

    connected_client_text = "Host conected at #addr#."
    disconnected_client_text = "Host disconected from #addr#."

    def __init__(self, host: str, port: int):
        self.defs = {}
        self.define_route(host, port)
        self.closed = False

    def register_blueprint_list(self, list_blueprint):
        for blueprint in list_blueprint:
            self.register_blueprint(blueprint)

    def register_blueprint(self, blueprint: Blueprint):
        self.defs.update(blueprint.defs)

    def call(self, route, value):
        time_s = time.time()
        try:
            if route in self.defs.keys():
                return json.dumps({"responce": self.defs[route](value),"code": 200, "time": time.time() - time_s})
            else:
                return json.dumps({"responce": "invalid", "code": 404, "time":  time.time() - time_s})
        except Exception as e:
            return json.dumps({"responce": e.__str__(), "code": 500, "time":  time.time() - time_s})

    def define_route(self, host, port):
        self.HOST = host
        self.PORT = port

    def print_header_text(self, text, size=2):
        s = (size + 1)
        terminal_size = shutil.get_terminal_size().columns
        border_size = (terminal_size - len(text) - 2) // s  # 2 is for spaces
        print("\33[91m-" * border_size, f"\33[36m{text}\33[91m", "-" * border_size, "\33[97m")

    def serve(self):
        os.system("clear")
        try:
            self.start_server()
            self.print_header_text(f"Started API Server on address \33[93m{self.HOST}:{self.PORT}", 1)
            self.main_loop()
            self.server_socket.close()
        except KeyboardInterrupt:
            self.server_socket.close()

        self.print_header_text(f"Closed API Server", 1)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()

    def main_loop(self):
        while not self.closed:
            conn, addr = self.server_socket.accept()
            with conn:
                self.conect_client(conn, addr)

    def conect_client(self, conn, addr):
        print(f"\33[32m{self.connected_client_text.replace('#addr#', str(addr))}\33[0m")
        self.client_main_loop(conn)
        print(f"\33[31m{self.disconnected_client_text.replace('#addr#', str(addr))}\33[0m")

    def client_main_loop(self, conn):
        while True:
            data = conn.recv(1024)
            if not data:
                continue
            received_json = json.loads(data.decode("utf-8"))
            response = self.call(received_json["route"], received_json["value"])
            conn.send(response.encode("utf-8"))
            conn.close()
            break

    def close(self):
        self.closed = True