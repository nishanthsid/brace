from brace.response import *
from werkzeug.wrappers import Request, Response
import json
from brace.urls import MethodUrls, HttpMethod
from brace.middlewares import MiddleWarePipeline

class Brace:
    def __init__(self):
        self.__url_aggregator = MethodUrls()
        self.__pre_req = MiddleWarePipeline(short_circuit_class=BaseResponse)
        self.__post_req = MiddleWarePipeline(short_circuit_class=BaseResponse)


    def pre_request(self):
        def wrapper(func):
            self.__pre_req.append_handler(func)
            return func
        return wrapper

    def post_request(self):
        def wrapper(func):
            self.__post_req.append_handler(func)
            return func
        return wrapper
    
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
    def response_sender(method_resp, environ, start_response):
        if not isinstance(method_resp, BaseResponse):
            resp = Response(
                method_resp,
                content_type = "text/plain",
                status = method_resp.get_status_code()
            )
            return resp(environ, start_response)
        response_body = method_resp.get_obj()

        resp_type = method_resp.get_resp_type()

        if resp_type == ResponseType.JSON:
            response_body = json.dumps(response_body)
            content_type = "application/json"
        elif resp_type == ResponseType.XML:
            content_type = "text/xml"
        elif resp_type == ResponseType.TEXT:
            content_type = "text/plain"
        else:
            content_type = "text/html"
        

        resp = Response(
            response_body,
            content_type = content_type,
            status = method_resp.get_status_code()
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
        pre_response = self.__pre_req.start(req)
        if not isinstance(pre_response, BaseResponse):
            method_resp = result.handler(req, **result.path_vars)
            post_response = self.__post_req.start((req, method_resp))
        else:
            post_response = self.__post_req.start((req, pre_response))

        _, post_response = post_response
        return Brace.response_sender(post_response, environ, start_response)

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
