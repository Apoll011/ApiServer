import json
import socket
from promise.promise import Promise

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
        promise = self.call_route_async("alive")
        promise.then(lambda data: self.__auth(data))

    def __auth(self, data: 'ApiResponse'):
        """
        Authenticates the client.

        Args:
            data (ApiResponse): The authentication response.
        """
        if data.response["on"]:
            self.active = True

    def call_route_async(self, route, value: str | dict[str, str] = ""):
        """
        Calls a route asynchronously.

        Args:
            route (str): The route to call.
            value (str | dict[str, str]): The value to pass to the route (default: "").

        Returns:
            A Promise object.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.HOST, self.PORT))
        d = {"route": route, "value": value}
        s.send(bytes(json.dumps(d).encode("utf-8")))
        promise = Promise()
        promise.resolve(lambda: self.__get_info(s, promise))
        return promise

    def call_route(self, route, value: str | dict[str, str] = ""):
        """
        Calls a route synchronously.

        Args:
            route (str): The route to call.
            value (str | dict[str, str]): The value to pass to the route (default: "").

        Returns:
            An ApiResponse object.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.HOST, self.PORT))
        d = {"route": route, "value": value}
        s.send(bytes(json.dumps(d).encode("utf-8")))
        data = s.recv(1024).decode("utf-8")
        return ApiResponse(json.loads(data))

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


class ApiResponse:
    response: dict
    code: int
    time: float

    def __init__(self, data: dict) -> None:
        """
        Initializes the API response.

        Args:
            data (dict): The response data.
        """
        self.response = data["response"]
        self.code = data["code"]
        self.time = data["time"]