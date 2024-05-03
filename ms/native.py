from typing import List, Any
from ms.objects import MNativeFunction, MValue, MObject
from ms.interpreter import Interpreter, Environment
from ms.types import TypeChecker
from ms.schema import JSONSchema

# Native functions.

# class IsType(NativeFunction):
#     def __init__(self, ip: Interpreter):
#         super(IsType, self).__init__(ip)
#         self.ip = ip
#         self.checker = ValueAsType()

#     def call(self, args: List[Any]):
#         data = args[0]
#         typedata = args[1]
#         return self.checker.check(typedata, data)


class Import(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(filename: Str) -> Object")

    def func(self, args: List[MObject]):
        filename = args[0].value
        try:
            with open(filename, "r") as fh:
                code = fh.read()

            ip = interpreter()
            ip.env = Environment(enclosing=ip.env)
            ip.eval(code)
            module = dict()
            env = ip.env
            while env is not None:
                for key, val in env.vars.items():
                    if key not in module:
                        module[key] = val
                env = env.enclosing
        except FileNotFoundError as e:
            print(f"File not found: {filename}")
            return None
        except Exception as e:
            print(e)
            return None
        return MValue(module, None)


class Str(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(value: Any) -> Str")
        self.ip = ip

    def func(self, args: List[MObject]):
        arg = args[0]
        repr = self.ip.printer.print(arg)
        return MValue(repr, None)


class Print(MNativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "function(value: Any) -> Any"
        super().__init__(ip, definition)

    def func(self, args: List[MObject]):
        arg = args[0]
        if type(arg) == MValue and type(arg.value) == str:
            print(arg.value)
        else:
            repr = self.interpreter.printer.print(arg)
            print(repr)
        return arg


class Dump(MNativeFunction):
    def __init__(self, ip: Interpreter):
        definition = "function() -> Null"
        super().__init__(ip, definition)

    def func(self, args: List[MObject]):
        env = self.ip.env
        pre = "=> "
        print("=== STATE DUMP START")
        while env is not None:
            print(pre)
            txt = self.interpreter.printer.print(MValue(env.vars, None))
            print(txt)
            pre = "==" + pre
            env = env.enclosing
        print("=== STATE DUMP END")
        return MValue(None, None)


class GetEnv(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function() -> Object")

    def func(self, args: List[MObject]):
        return MValue(self.interpreter.env.vars, None)


class TypeOf(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(value: Any) -> Type")

    def func(self, args: List[MObject]):
        arg = args[0]
        return self.interpreter.typeof(arg)

class Assert(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(value: Bool) -> Bool")

    def func(self, args: List[MObject]):
        arg = args[0]
        if not arg.value:
            self.error("Assertion failed.")
        return MValue(True, None)


class IsSubtype(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(subtype: Type, supertype: Type) -> Bool")

    def func(self, args: List[MObject]):
        confirmed = self.interpreter.issubtype(args[0], args[1])
        return MValue(confirmed, None)

class Schema(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "function(value: Type) -> Str")
        self.printer = JSONSchema()

    def func(self, args: List[MObject]):
        arg = args[0]
        valtype = self.printer.print_schema(arg)
        return MValue(valtype, None)


def interpreter(interactive=False):
    ip = Interpreter(interactive=interactive)
    ip.define("import", Import(ip=ip))
    ip.define("str", Str(ip=ip))
    ip.define("print", Print(ip=ip))
    ip.define("dump", Dump(ip=ip))
    ip.define("get_env", GetEnv(ip=ip))
    ip.define("typeof", TypeOf(ip=ip))
    ip.define("issubtype", IsSubtype(ip=ip))
    ip.define("schema", Schema(ip=ip))
    ip.define("assert", Assert(ip=ip))

    # Clean the lexer's code buffer.
    ip.parser.lexer.reset()
    return ip
