from typing import Callable
def logger(func : Callable):
    def wrapper():
        print("Executing funcion {}".format(func.__name__))
        func()
        print("Done")
    return wrapper

@logger
def hello():
    print("Hello Nishanth")



hello()
