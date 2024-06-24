# API Server Documentation
This API server is designed to be a flexible and easy-to-use framework for building RESTful APIs. It provides a simple way to define routes, handle requests, and return responses.

## Features
- Blueprint System: The API server uses a blueprint system to define routes. A blueprint is an instance of the Blueprint class, which can be used to define multiple routes. Blueprints can be registered with the API server using the register_blueprint method.

- Route Definition: Routes can be defined using the route decorator provided by the Blueprint class. The decorator takes a route string as an argument and returns a decorator function that can be used to decorate a route function.

- Request Handling: The API server handles requests by calling the corresponding route function and passing the request value as an argument. The route function can return a response, which is then serialized to JSON and sent back to the client.

- Client Connection Handling: The API server can handle multiple client connections simultaneously. When a client connects, the connect_client method is called, which starts a new thread to handle the client connection.

- Error Handling The API server provides built-in error handling. If an exception occurs while handling a request, the API server catches the exception and returns a JSON response with a `500` status code.

## Usage
Creating an API Server
To create an API server, create an instance of the API class and pass the host and port as arguments:

```python
api = API("localhost", 8080)
```
Defining Routes
To define a route, create a blueprint and use the route decorator to define a route function:

```python
blueprint = Blueprint()

@blueprint.route("hello")
def hello_world(value):
    return f"Hello, {value}!"
```
Registering Blueprints
To register a blueprint with the API server, use the register_blueprint method:

```python
api.register_blueprint(blueprint)
```
Registering Multiple Blueprints
To register multiple blueprints with the API server, use the register_blueprint_list method:

```python
blueprint1 = Blueprint()
blueprint2 = Blueprint()

api.register_blueprint_list([blueprint1, blueprint2])
```

Starting the API Server
To start the API server, call the serve method:

```python
api.serve()
```
Making Requests
To request the API server, connect to the server using a socket and send a JSON request:

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 8080))

request = {"route": "hello", "value": "World"}
sock.send(json.dumps(request).encode("utf-8"))

response = sock.recv(1024)
print(response.decode("utf-8"))  # Output: {"response": "Hello, World!", "code": 200, "time": 0.01}
```
## Example
Here is an example of creating an API server with a single route:

```python
from api_server import API, Blueprint

blueprint = Blueprint()

@blueprint.route("hello")
def hello_world(value):
    return f"Hello, {value}!"

api = API("localhost", 8080)
api.register_blueprint(blueprint)
api.serve()
```
This example creates an API server that listens on `localhost:8080` and defines a single route `/hello` that takes a value parameter and returns a greeting message.


# API Client Documentation
This API client is designed to be a flexible and easy-to-use framework for interacting with RESTful APIs. It provides a simple way to call routes, handle responses, and authenticate with the API server.

## Features
- Asynchronous Route Calling: The API client provides a way to call routes asynchronously using the call_route_async method. This method returns a Promise object that resolves with the response data.

- Synchronous Route Calling: The API client also provides a way to call routes synchronously using the call_route method. This method returns an ApiResponse object.

- Authentication: The API client provides a way to authenticate with the API server using the authenticate method. This method calls the alive route and sets the active flag based on the response.

## Usage
Creating an API Client To create an API client, create an instance of the ApiClient class and pass the host and port as arguments:

```python
client = ApiClient("localhost", 8080)
```

Calling Routes To call a route, use the call_route or call_route_async method:

```python
# Synchronous call
response = client.call_route("hello", "World")
print(response.response)  # Output: "Hello, World!"

# Asynchronous call
promise = client.call_route_async("hello", "World")
promise.then(lambda data: print(data.response))  # Output: "Hello, World!"
```

Example
Here is an example of creating an API client and calling a route:

```python
client = ApiClient("localhost", 8080)
if client.active:
    response = client.call_route("hello", "World")
    print(response.response)  # Output: "Hello, World!"
```
This example creates an API client that connects to localhost:8080, authenticates with the API server, and calls the /hello route with the value World

## License
This API server and client is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! If you want to contribute to the API server and client, please fork the repository and submit a pull request.

## Acknowledgments
This API server and client was originally developed for (Alex)[github.com/Apoll011/Alex] but can be used for any application.