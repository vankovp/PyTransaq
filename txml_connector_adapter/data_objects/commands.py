from typing import  TypeVar, Type
from pydantic import BaseModel

T = TypeVar('T', bound=object)

class Command:
    def __init__(self, name: (str | None) = None):
        self._name = name

    @staticmethod
    def classNameToCommandName(name: str) -> str:
        return name

    def getName(self, cls: Type[T]) -> str:
        if self._name is not None: 
            return self._name
        return self.classNameToCommandName(cls.__name__)

    def __call__(self, cls: Type[T]) -> Type[T]:
        setattr(cls, "_command_name", self.getName(cls))
        return cls

@Command("some_name")
class SomeCommand(BaseModel):
    field1: str
    field2: int
