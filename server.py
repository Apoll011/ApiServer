import json
import time
import shutil
import socket
import os

class Blueprint:
    """
    Blueprint class is used to define routes for the API.
    """

    route_functions = {}
    """
    The dictionary of the routes and the function to execute on that route.
    """

    builtin_routes = {}
    """
    The dictionary of the builtins routes and the function to execute on that route.
    """

    pre = ""

    def __init__(self, main_route: str = ""):
        """
        Initializes the Blueprint object.

        Args:
            main_route (str): The main route (default: "").
        """
        self.pre = main_route

    def route(self, route: str):
        """
        Defines a route.

        Args:
            route (str): The route to define.

        Returns:
            A decorator function.
        """
        def decorator(fun):
            p = "" if self.pre == "" else  "/"
            self.route_functions[self.pre + p + route] = fun
            def wrapper(*args, **kwargs):
                return fun(*args, **kwargs)
            return wrapper
        return decorator
    
    def register_blueprint_list(self, list_blueprint: list):
        """
        Registers a list of blueprints.

        Args:
            list_blueprint (list): A list of blueprints.
        """
        for blueprint in list_blueprint:
            self.register_blueprint(blueprint)

    def register_blueprint(self, blueprint: 'Blueprint'):
        """
        Registers a blueprint.

        Args:
            blueprint (Blueprint): A blueprint.
        """
        self.route_functions.update(blueprint.route_functions)

    def call(self, route: str, value: str):
        """
        Calls a route function.

        Args:
            route (str): The route to call.
            value (str): The value to pass to the route function.

        Returns:
            A JSON response.
        """
        time_s = time.time()
        try:
            if route in self.route_functions.keys():
                return json.dumps({"responce": self.route_functions[route](value), "code": 200, "time": time.time() - time_s})
            elif route in self.builtin_routes.keys():
                return json.dumps({"responce": self.builtin_routes[route](), "code": 200, "time": time.time() - time_s})
            else:
                return json.dumps({"responce": "invalid", "code": 404, "time": time.time() - time_s})
        except Exception as e:
            return json.dumps({"responce": str(e), "code": 500, "time": time.time() - time_s})

class API(Blueprint):
    """
    API class is used to create an API server.
    """
    server_socket: socket.socket
    HOST: str
    PORT: int
    closed: bool

    connected_client_text = "Host connected at #addr#."
    disconnected_client_text = "Host disconnected from #addr#."

    def __init__(self, host: str, port: int):
        """
        Initializes the API object.

        Args:
            host (str): The host address.
            port (int): The port number.
        """
        super().__init__()

        self.route_functions = {}
        
        self.__register_builtins()

        self.define_route(host, port)
        self.closed = False

    def __register_builtins(self):
        self.builtin_routes = {
            "auth": self.__auth,
            "close": self.close
        }
        
    def __auth(self):
        return {"on": True}
    
    def define_route(self, host: str, port: int):
        """
        Defines the host and port.

        Args:
            host (str): The host address.
            port (int): The port number.
        """
        self.HOST = host
        self.PORT = port

    def __print_header_text(self, text: str, size: int = 2):
        """
        Prints a header text.

        Args:
            text (str): The text to print.
            size (int): The size of the border (default: 2).
        """
        s = (size + 1)
        terminal_size = shutil.get_terminal_size().columns
        border_size = (terminal_size - len(text) - 2) // s  # 2 is for spaces
        print("\33[91m-" * border_size, f"\33[36m{text}\33[91m", "-" * border_size, "\33[97m")

    def serve(self):
        """
        Starts the API server.
        """
        os.system("clear")
        try:
            self.__start_server()
            self.__print_header_text(f"Started API Server on address \33[93m{self.HOST}:{self.PORT}", 1)
            self.__main_loop()
        except KeyboardInterrupt:
            self.close()
        finally:
            self.server_socket.close()
            self.__print_header_text(f"Closed API Server", 1)

    def __start_server(self):
        """
        Starts the server.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()

    def __main_loop(self):
        """
        Main loop of the API server.
        """
        while not self.closed:
            conn, addr = self.server_socket.accept()
            with conn:
                self.__connect_client(conn, addr)

    def __connect_client(self, conn: socket.socket, addr: tuple):
        """
        Handles a client connection.

        Args:
            conn (socket.socket): The client connection.
            addr (tuple): The client address.
        """
        print(f"\33[32m{self.connected_client_text.replace('#addr#', str(addr))}\33[0m")
        self.__client_main_loop(conn)
        print(f"\33[31m{self.disconnected_client_text.replace('#addr#', str(addr))}\33[0m")

    def __client_main_loop(self, conn: socket.socket):
        """
        Main loop of the client connection.

        Args:
            conn (socket.socket): The client connection.
        """
        while True:
            data = conn.recv(1024)
            if not data:
                break
            received_json = json.loads(data.decode("utf-8"))
            response = self.call(received_json["route"], received_json["value"])
            if not self.closed:
                conn.send(response.encode("utf-8"))
        conn.close()

    def close(self):
        """
        Closes the API server.
        """
        self.closed = True
        self.server_socket.close()