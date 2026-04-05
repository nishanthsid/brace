from typing import Callable

class ShortCircuit:
    def __init__(self, response):
        self.response = response


class MiddleWareEntry:
    def __init__(self, short_circuit_class=ShortCircuit):
        self.__handler = MiddleWareEntry.echo
        self.__EOP = True
        self.__next = None
        self.__short_circuit_class = short_circuit_class

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
        if isinstance(handler_result, self.__short_circuit_class) or self.is_eop():
                return handler_result
        else:
            return self.__next(handler_result)

    def attach_next(self, next_entry):
        self.__next = next_entry

    def get_next(self):
        return self.__next

class MiddleWarePipeline:
    def __init__(self, short_circuit_class=ShortCircuit):
        self.__pipe_head = MiddleWareEntry()
        self.__curr = self.__pipe_head
        self.__short_circuit_class = short_circuit_class
    
    def append_handler(self, handler : Callable):
        self.__curr.set_handler(handler)
        self.__curr.set_eop(False)
        self.__curr.attach_next(MiddleWareEntry(short_circuit_class=self.__short_circuit_class))
        self.__curr = self.__curr.get_next()

    def start(self, *args, **kwargs):
        return self.__pipe_head(*args, **kwargs)

