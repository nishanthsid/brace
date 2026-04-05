from enum import Enum, auto

class ResponseType(Enum):
    JSON = auto()
    TEXT = auto()
    HTML = auto()
    XML = auto()

class BaseResponse:
    def __init__(self, resp_obj, status_code):
        self.__obj = resp_obj
        self.__status_code = status_code
    
    def get_obj(self):
        return self.__obj

    def get_status_code(self):
        return self.__status_code
    
    def get_resp_type(self):
        raise NotImplementedError("Child classes must implement this method")

class JsonResponse(BaseResponse):
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