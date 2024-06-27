import json
import socket
from .promise.promise import Promise

class ApiResponse:
    response: dict
    """
    This is the responce returned by the server
    """
    code: int
    """
    The code returned by the server:
        `200`: `Ok`
        `400`: `Route Not Found`
        `500`: `Server error`. (Description on responce)
    """
    time: float
    """
    Time in `seconds` that it took to return an answer
    """

    def __init__(self, data: dict) -> None:
        """
        Initializes the API response.

        Args:
            data (dict): The response data.
        """
        self.response = data["responce"]
        self.code = data["code"]
        self.time = data["time"]

class ApiClient:
    HOST: str
    PORT: int

    active = False

    def __init__(self, host, port):
        """
        Initializes the API client.

        Args:
            host (str): The host address.
            port (int): The port number.
        """
        self.HOST = host
        self.PORT = port

        self.authenticate()

    def authenticate(self):
        """
        Authenticates the client.
        """
        data = self.call_route("auth")
        self.__auth(data)
    
    def __auth(self, data: ApiResponse):
        """
        Authenticates the client.

        Args:
            data (ApiResponse): The authentication response.
        """
        if data.response["on"]:
            self.active = True
    
    def close_server(self):
        """
        Close the server
        """
        self.__conect_and_send("close")
        self.active = False
  
    def call_route_async(self, route, value: str | dict[str, str] = ""):
        """
        Calls a route asynchronously.

        Args:
            route (str): The route to call.
            value (str | dict[str, str]): The value to pass to the route (default: "").

        Returns:
            A Promise object.
        """
        s = self.__conect_and_send(route, value)
        promise = Promise()
        promise.resolve(lambda: self.__get_info(s, promise))
        return promise

    def call_route(self, route: str, value: str | dict[str, str] = ""):
        """
        Calls a route synchronously.

        Args:
            route (str): The route to call.
            value (str | dict[str, str]): The value to pass to the route (default: "").

        Returns:
            An ApiResponse object.
        """
        s = self.__conect_and_send(route, value)
        data = s.recv(1024).decode("utf-8")
        return ApiResponse(json.loads(data))

    def __conect_and_send(self, route: str, value: str | dict[str, str] = ""):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.HOST, self.PORT))
        d = {"route": route, "value": value}
        s.send(bytes(json.dumps(d).encode("utf-8")))
        return s
    
    def __get_info(self, s, promise: Promise):
        """
        Gets the response from the server.

        Args:
            s (socket.socket): The socket object.
            promise (Promise): The promise object.
        """
        try:
            data = s.recv(1024).decode("utf-8")
            promise.resolve(lambda: ApiResponse(json.loads(data)))
            s.close()  # Close the socket object
        except socket.error as e:
            promise.reject(e)
            s.close()  # Close the socket object
        except json.JSONDecodeError as e:
            promise.reject(e)
            s.close()  # Close the socket object


