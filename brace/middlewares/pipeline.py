from typing import Callable

class MiddleWareEntry:
    def __init__(self):
        self.__handler = MiddleWareEntry.echo
        self.__EOP = True
        self.__next = None

    def set_handler(self, handler):
        self.__handler = handler

    @staticmethod
    def echo(*args, **kwargs):
        if kwargs:
            return args[0] if len(args) == 1 else args
        return args[0] if len(args) == 1 else args

    def is_eop(self):
        return self.__EOP

    def set_eop(self, eop):
        self.__EOP = eop

    def __call__(self, *args, **kwargs):
        handler_result = self.__handler(*args, **kwargs)
        if isinstance(handler_result, tuple) and len(handler_result) == 2:
            should_continue, value = handler_result
            if not should_continue:
                return value
            handler_result = value
        if self.is_eop():
            return handler_result
        else:
            return self.__next(handler_result)

    def attach_next(self, next_entry):
        self.__next = next_entry

    def get_next(self):
        return self.__next

class MiddleWarePipeline:
    def __init__(self):
        self.__pipe_head = MiddleWareEntry()
        self.__curr = self.__pipe_head
    
    def append_handler(self, handler : Callable):
        self.__curr.set_handler(handler)
        self.__curr.set_eop(False)
        self.__curr.attach_next(MiddleWareEntry())
        self.__curr = self.__curr.get_next()

    def start(self, *args, **kwargs):
        return self.__pipe_head(*args, **kwargs)

