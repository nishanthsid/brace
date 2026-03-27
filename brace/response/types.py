from enum import Enum, auto

class ResponseType(Enum):
    JSON = auto()
    TEXT = auto()
    HTML = auto()
    XML = auto()

class BaseResponse:
    def __init__(self, resp_obj):
        self.obj = resp_obj
    
    def get_obj(self):
        return self.obj
    
    def get_resp_type(self):
        raise NotImplementedError("Child classes must implement this method")

class JsonRespone(BaseResponse):
    def get_resp_type(self):
        return ResponseType.JSON

class PlainTextResponse(BaseResponse):
    def get_resp_type(self):
        return ResponseType.TEXT

class XmlResponse(BaseResponse):
    def get_resp_type(self):
        return ResponseType.XML

class HtmlResponse(BaseResponse):
    def get_resp_type(self):
        return ResponseType.HTML