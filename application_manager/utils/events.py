from typing import Callable

class Event():
    """A convenience class to register callbacks"""
    def __init__(self, *arg_types) -> None:
        self._handlers: set[Callable] = set()
        self._arg_types = arg_types

    def subscribe(self, handler: Callable):
        self._handlers.add(handler)

    def unsubscribe(self, handler: Callable):
        self._handlers.discard(handler)
    
    def clear(self):
        self._handlers.clear()

    def fire(self, *args):
        assert len(args) == len(self._arg_types)
        for i, (arg, expected_type) in enumerate(zip(args, self._arg_types)):
            if(not isinstance(arg, expected_type)):
                raise TypeError(f'argument at index {i} has type {type(arg)}, does not match the expected type {expected_type}.')
        
        for handler in self._handlers:
            handler(*args)
