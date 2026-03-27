from brace.response import *
from werkzeug.wrappers import Request, Response
import json
from brace.urls import UrlStorage

class Brace:
    def __init__(self):
        self.endpoints = {
            "GET":{},
            "POST":{}
        }
        self.url_storage = UrlStorage()
    
    def get(self, endpoint : str):
        def wrapper(func):
            if "<" in endpoint and ">" in endpoint:
                self.url_storage.insert(endpoint, func)
            else:
                self.endpoints["GET"][endpoint] = func
            return func
        return wrapper
    
    def handle_get_response(self, req, environ, start_response):
        path = req.path
        func = self.endpoints["GET"].get(path, None)
        path_vars = {}
        if func == None:
            succ, path_vars, func = self.url_storage.search(path)
            if succ == False:
                func = None
        if func is None:
            resp = Response(
                "<h1> Not Found </h1>",
                content_type = "text/html",
                status = 404
            )
            return resp(environ, start_response)
        
        status, method_resp = func(req, **path_vars)
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

    def __call__(self, environ, start_response):
        req = Request(environ)
    
        if req.method == "GET":
            return self.handle_get_response(req, environ, start_response)
        
        resp = Response(
            "<h1> Method not allowed </h1>",
            content_type = "text/html",
            status = 405
        )
        
        return resp(environ, start_response)
