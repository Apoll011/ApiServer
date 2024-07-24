import json
import time
import shutil
import socket
import os
import threading

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
            self.set_route(route, fun)        
            def wrapper(*args, **kwargs):
                return fun(*args, **kwargs)
            return wrapper
        return decorator
    
    def set_route(self, route, fun):
        p = "" if self.pre == "" else  "/"
        self.route_functions[self.pre + p + route] = fun

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

    client_name = "Host"
    conections = 0
    active = 0

    max: int

    conections_func_send = {}

    def __init__(self, host: str, port: int, max_conections = 5):
        """
        Initializes the API object.

        Args:
            host (str): The host address.
            port (int): The port number.
        """
        super().__init__()

        self.route_functions = {}

        self.max = max_conections
        
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
        try:
            self.__start_server()
            self.screen()
            self.__main_loop()
        except KeyboardInterrupt:
            self.close()
        finally:
            self.server_socket.close()
            self.__print_header_text(f"Closed API Server", 1)
    
    def screen(self):
        os.system("clear")
        self.__print_header_text(f"Started API Server on address \33[93m{self.HOST}:{self.PORT}", 1)
        print(f"Till now there was \33[32m{self.conections}\33[0m from \33[94m{self.client_name}.\33[0m")
        print(f"There are \33[32m{self.active}\33[0m active conections")
        print("Active Routes Are: ")
        for route in self.route_functions:
            print("\t- \33[33mRoute:\33[32m", route, "\33[36mUp and running\33[0m")

    def __start_server(self):
        """
        Starts the server.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(5)

    def __main_loop(self):
        """
        Main loop of the API server.
        """
        while not self.closed:
            conn, addr = self.server_socket.accept()
            client_thread = threading.Thread(target=self.__connect_client, args=(conn, addr))
            client_thread.start()

    def __connect_client(self, conn: socket.socket, addr: tuple):
        """
        Handles a client connection.

        Args:
            conn (socket.socket): The client connection.
            addr (tuple): The client address.
        """
        self.conections += 1
        self.active += 1
        self.screen()
        self.conections_func_send[addr] = conn
        self.__client_main_loop(conn)
        self.conections_func_send[addr] = None
        self.active -= 1
        self.screen()

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
