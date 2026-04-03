from brace.response import *
from werkzeug.wrappers import Request, Response
import json
from brace.urls import MethodUrls, HttpMethod, EndpointQueryResult

class Brace:
    def __init__(self):
        self.__url_aggregator = MethodUrls()
    
    def get(self, endpoint : str):
        def wrapper(func):
            self.__url_aggregator.insert_endpoint(HttpMethod.GET, endpoint, func)
            return func
        return wrapper
    
    def post(self, endpoint : str):
        def wrapper(func):
            self.__url_aggregator.insert_endpoint(HttpMethod.POST, endpoint, func)
            return func
        return wrapper
    
    def put(self, endpoint : str):
        def wrapper(func):
            self.__url_aggregator.insert_endpoint(HttpMethod.PUT, endpoint, func)
            return func
        return wrapper
    
    def delete(self, endpoint : str):
        def wrapper(func):
            self.__url_aggregator.insert_endpoint(HttpMethod.DELETE, endpoint, func)
            return func
        return wrapper
    
    @staticmethod
    def response_sender(status, method_resp, environ, start_response):
        if isinstance(method_resp, BaseResponse) == False:
            resp = Response(
                method_resp,
                content_type = "text/plain",
                status = status
            )
            return resp(environ, start_response)
        
        content_type = ""
        response_body = method_resp.get_obj()

        type = method_resp.get_resp_type()

        if type == ResponseType.JSON:
            response_body = json.dumps(response_body)
            content_type = "application/json"
        elif type == ResponseType.XML:
            content_type = "text/xml"
        elif type == ResponseType.TEXT:
            content_type = "text/plain"
        else:
            content_type = "text/html"
        

        resp = Response(
            response_body,
            content_type = content_type,
            status = status
        )

        return resp(environ, start_response)

    def handle_request(self, req, environ, start_response):
        result = self.__url_aggregator.get_handler(HttpMethod[req.method], req.path)
        if result.handler is None:
            resp = Response(
                "<h1> Not Found </h1>",
                content_type = "text/html",
                status = 404
            )
            return resp(environ, start_response)
        status, method_resp = result.handler(req, **result.path_vars)

        return Brace.response_sender(status, method_resp, environ, start_response)

    def __call__(self, environ, start_response):
        req = Request(environ)
    
        if HttpMethod.__members__.get(req.method) is not None:
            return self.handle_request(req, environ, start_response)
        
        resp = Response(
            "<h1> Method not allowed </h1>",
            content_type = "text/html",
            status = 405
        )
        
        return resp(environ, start_response)
