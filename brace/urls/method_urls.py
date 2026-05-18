from .storage import UrlStorage
from enum import Enum, auto
from typing import Callable
from brace.exceptions import InvalidEndpointException

class HttpMethod(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()


class EndpointValidator(Enum):
    LOOK_OPEN = auto()   # waiting to see <
    LOOK_COLON = auto()  # inside <..., waiting for :
    LOOK_CLOSE = auto()  # after :, waiting for >

    @staticmethod
    def is_param(endpoint: str):
        context = EndpointValidator.LOOK_OPEN
        for i in endpoint:
            if i == "<":
                if context == EndpointValidator.LOOK_OPEN:
                    context = EndpointValidator.LOOK_COLON
                else:
                    raise InvalidEndpointException()
            elif i == ":":
                if context == EndpointValidator.LOOK_COLON:
                    context = EndpointValidator.LOOK_CLOSE
                else:
                    raise InvalidEndpointException()
            elif i == ">":
                if context == EndpointValidator.LOOK_CLOSE:
                    return True
                else:
                    raise InvalidEndpointException()
            else:
                if context == EndpointValidator.LOOK_CLOSE:
                    if not i.isalnum():
                        raise InvalidEndpointException()

        return False

class EndpointQueryResult:
    def __init__(self, success = False, path_vars = None, handler = None):
        self.success = success
        self.path_vars = {} if path_vars is None else path_vars
        self.handler = handler

class EndpointAggregator:
    def __init__(self):
        self.__plain_endpoints = {}
        self.__param_endpoints = UrlStorage()
    
    def insert_url(self, endpoint : str, handler : Callable):
        is_par = EndpointValidator.is_param(endpoint)
        if is_par:
            self.__param_endpoints.insert(endpoint, handler)
        else:
            self.__plain_endpoints[endpoint] = handler
    
    def search_handler(self, endpoint : str):
        #First try faster dict
        ret = EndpointQueryResult()
        match1 = self.__plain_endpoints.get(endpoint, None)
        if match1 is not None:
            ret.success = True
            ret.handler = match1
            return ret
        
        #second try O(n) Trie search
        success, path_vars, handler = self.__param_endpoints.search(endpoint)
        ret.success = success
        ret.path_vars = path_vars
        ret.handler = handler

        return ret
    

class MethodUrls:
    def __init__(self):
        self.__aggregates = {}

        for method in HttpMethod:
            self.__aggregates[method.name] = EndpointAggregator()
    
    def insert_endpoint(self, method : HttpMethod, endpoint : str, handler : Callable):
        self.__aggregates[method.name].insert_url(endpoint, handler)
    

    def get_handler(self, method: HttpMethod, endpoint : str):
        return self.__aggregates[method.name].search_handler(endpoint)

