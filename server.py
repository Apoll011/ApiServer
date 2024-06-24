import json
import time

class Blueprint:
    defs = {
        
    }
    pre = ""
    def __init__(self, main_route = "") -> None:
        self.pre = main_route

    def route(self, route):
        def decorator(fun): 
            self.defs[self.pre + "/" + route] = fun
            def wrapper(*args, **kwargs):
                return fun(*args, **kwargs)
            return wrapper
        return decorator

class API(Blueprint):
    def __init__(self) -> None:
        self.defs = {}

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


