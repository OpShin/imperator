import enum
import logging
from dataclasses import dataclass
from functools import partial

import frozendict

_LOGGER = logging.getLogger(__name__)


class ConstantType(enum.Enum):
    integer = int
    bytestring = lambda x: bytes.fromhex(x[1:])
    str = lambda x: str(x).encode("utf8")
    unit = lambda _: ()
    bool = lambda x: x == "True"


class BuiltInFun(enum.Enum):
    AddInteger = lambda x, y: x + y
    Trace = lambda x, y: print(x) or y
    IfThenElse = lambda x, y, z: y if x else z


class AST:
    def eval(self, state: frozendict.frozendict):
        raise NotImplementedError()

    def compile(self) -> str:
        raise NotImplementedError()


@dataclass
class Program(AST):
    version: str
    term: AST

    def eval(self, state):
        return self.term.eval(state)

    def compile(self) -> str:
        return f"(program {self.version} {self.term.compile()})"


@dataclass
class Variable(AST):
    name: str

    def eval(self, state):
        try:
            return state[self.name]
        except KeyError as e:
            _LOGGER.error(
                f"Access to uninitialized variable {self.name} in {self.compile()}"
            )
            raise e

    def compile(self) -> str:
        return self.name


@dataclass
class Constant(AST):
    type: ConstantType
    value: str

    def eval(self, state):
        return self.type.value(self.value)

    def compile(self) -> str:
        return f"(con {self.type.name} {self.value})"


@dataclass
class Lambda(AST):
    var_name: str
    term: AST

    def eval(self, state):
        def f(x):
            return self.term.eval(state | {self.var_name: x})

        return partial(f)

    def compile(self) -> str:
        return f"(lam {self.var_name} {self.term.compile()})"


@dataclass
class Delay(AST):
    term: AST

    def eval(self, state):
        def f():
            return self.term.eval(state)

        return f

    def compile(self) -> str:
        return f"(delay {self.term.compile()})"


@dataclass
class Force(AST):
    term: AST

    def eval(self, state):
        try:
            return self.term.eval(state)()
        except TypeError as e:
            _LOGGER.error(
                f"Trying to force an uncallable object, probably not delayed? in {self.compile()}"
            )
            raise e

    def compile(self) -> str:
        return f"(force {self.term.compile()})"


@dataclass
class BuiltIn(AST):
    builtin: BuiltInFun

    def eval(self, state):
        return partial(self.builtin.value)

    def compile(self) -> str:
        return f"(builtin {self.builtin.name})"


@dataclass
class Error(AST):
    def eval(self, state):
        raise RuntimeError(f"Execution called {self.compile()}")

    def compile(self) -> str:
        return f"(error)"


@dataclass
class Apply(AST):
    f: AST
    x: AST

    def eval(self, state):
        f = self.f.eval(state)
        x = self.x.eval(state)
        try:
            res = partial(f, x)
            # If this function has as many arguments bound as it takes, reduce i.e. call
            if len(f.args) == f.func.__code__.co_argcount:
                res = f()
            return res
        except AttributeError as e:
            _LOGGER.warning(f"Tried to apply value to non-function in {self.compile()}")
            raise e

    def compile(self) -> str:
        return f"[{self.f.compile()} {self.x.compile()}]"
