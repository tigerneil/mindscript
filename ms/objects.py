from typing import Optional, List, Union
from abc import abstractmethod
import ms.ast as ast

# Value types

# Primitive value.
class MObject():
    @property
    @abstractmethod
    def annotation(self):
        pass

class MValue(MObject):
    def __init__(self, value, annotation=None):
        self._value = value
        self._annotation = annotation

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val
    
    @property
    def annotation(self):
        return self._annotation

    @annotation.setter
    def annotation(self, val):
        self._annotation = val






# Types.


class MType(MObject):

    def __init__(self, ip: 'Interpreter', definition: ast.TypeExpr):  # type: ignore
        self._ip = ip
        self._env = ip.env
        self._definition = definition

    def __expr__(self):
        text = self.interpreter.printer.print(self.definition)
        return text

    def __str__(self):
        text = self.interpreter.printer.print(self.definition)
        return text

    @property
    def interpreter(self):
        return self._ip
    
    @property
    def environment(self):
        return self._env

    @property
    def definition(self):
        return self._definition
    
    @property
    def annotation(self):
        self._definition.annotation

    @annotation.setter
    def annotation(self, note):
        self._definition.annotation = note




# Callables.

class MFunction(MObject):

    def __init__(self, ip: 'Interpreter', definition: ast.Function):  # type: ignore
        self._ip = ip
        self._env = ip.env
        self._definition = definition
        self._param = definition.parameter

        # Create input types.
        ptype = definition.types.left
        self._intype = MType(ip, ptype)

        # Create output type.
        ptype = definition.types.right
        self._outtype = MType(ip, ptype)

    @property
    def interpreter(self) -> 'Interpreter':  # type: ignore
        return self._ip

    @property
    def environment(self) -> 'Environment':  # type: ignore
        return self._env

    @property
    def param(self) -> List[str]:
        return self._param

    @property
    def intype(self) -> List[MObject]:
        return self._intype

    @property
    def outtype(self) -> List[MObject]:
        return self._outtype

    @property
    def definition(self) -> ast.Function:
        return self._definition

    @property
    def annotation(self):
        return self._definition.types.annotation
    
    @annotation.setter
    def annotation(self, note):
        self._definition.types.annotation = note

    def call(self, arg: MObject) -> MObject:
        if not self.interpreter.checktype(arg, self.intype):
            raise ast.TypeError(f"Wrong type of function argument.")

        value = self.func(arg)

        if not self.interpreter.checktype(value, self.outtype):
            raise ast.TypeError(f"Wrong type of function output.")

        return value

    @abstractmethod
    def func(self, args: List[MObject]) -> MObject:
        pass

    def __repr__(self):
        # print(f"UserFunction.repr: definition = {self.definition}")
        return self.interpreter.printer.print(self.definition)

    def __str__(self):
        # print(f"UserFunction.str: definition = {self.definition}")
        return self.interpreter.printer.print(self.definition)


class MNativeFunction(MFunction):

    # type: ignore
    def __init__(self, ip: 'Interpreter', definition: Union[ast.Function, str]): # type: ignore
        if type(definition) == str:
            definition = ip.parser.parse(
                definition + " do null end").program[0]
        super().__init__(ip, definition)
        self._definition.expr = ast.Terminal(
            token=ast.Token(
                ttype=ast.TokenType.TYPE,
                literal="<native function>"
            )
        )

    @abstractmethod
    def func(self, arg: MObject) -> MObject:
        pass
