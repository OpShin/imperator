from dataclasses import dataclass
import typing

State = typing.Dict[str, typing.Any]
STATEMONAD = "s"

class AST:
    def compile(self) -> str:
        raise NotImplementedError()

class Expression(AST):
    def eval(self, state: State) -> typing.Any:
        raise NotImplementedError()


@dataclass
class Number(Expression):
    value: str

    def eval(self, state):
        return int(self.value)

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> {self.value})"

@dataclass
class Text(Expression):
    value: str

    def eval(self, state):
        return str(self.value[1:-1])

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> {self.value})"

@dataclass
class Variable(Expression):
    name: str

    def eval(self, state):
        return state[self.name.encode().hex()]

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> {STATEMONAD} 0x{self.name.encode().hex()})"


@dataclass
class BinaryOp(Expression):
    left: Expression
    right: Expression


@dataclass
class Sum(BinaryOp):
    def eval(self, state: State):
        return self.left.eval(state) + self.right.eval(state)

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> (({self.left.compile()} {STATEMONAD}) +i ({self.right.compile()} {STATEMONAD})))"

@dataclass
class Sub(BinaryOp):
    def eval(self, state: State):
        return self.left.eval(state) - self.right.eval(state)

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> (({self.left.compile()} {STATEMONAD}) -i ({self.right.compile()} {STATEMONAD})))"

@dataclass
class Mul(BinaryOp):
    def eval(self, state: State):
        return self.left.eval(state) * self.right.eval(state)

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> (({self.left.compile()} {STATEMONAD}) *i ({self.right.compile()} {STATEMONAD})))"

@dataclass
class Eq(BinaryOp):
    def eval(self, state: State):
        return self.left.eval(state) == self.right.eval(state)

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> (({self.left.compile()} {STATEMONAD}) ==i ({self.right.compile()} {STATEMONAD})))"

@dataclass
class Less(BinaryOp):
    def eval(self, state: State):
        return self.left.eval(state) < self.right.eval(state)

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> (({self.left.compile()} {STATEMONAD}) <i ({self.right.compile()} {STATEMONAD})))"

@dataclass
class IntCast(Expression):
    expression: Expression

    def eval(self, state: State):
        return int(self.expression.eval(state))

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> UnIData ({self.expression.compile()} {STATEMONAD}))"

@dataclass
class Function(Expression):
    args: typing.List[str]
    body: "Statement"
    rv: Expression

    def eval(self, state: State) -> typing.Any:
        # at this point, the arguments are in the state
        # as variables with the special value "__args__"
        local_state = state.copy()
        def fun(s: State):
            new_state = local_state
            new_state.update({a.encode().hex(): v for a, v in zip(self.args, s["__args__"])})
            final_state = self.body.exec(new_state)
            return self.rv.eval(final_state)
        return fun

    def compile(self):
        body_c = self.body.compile()
        ret_c = self.rv.compile()
        args_state = r"(\x -> "
        for i, a in enumerate(self.args):
            args_state += f"if (x ==b 0x{a.encode().hex()}) then p{i} else ("
        args_state += f" ({STATEMONAD} x))" + len(self.args) * ")"
        params = "\\" + " ".join(f"p{i}" for i, _ in enumerate(self.args))
        return rf"(\{STATEMONAD} -> ({params} -> {ret_c} ({body_c} {args_state})))"

@dataclass
class FunctionCall(Expression):
    function_name: str
    args: typing.List[Expression]

    def eval(self, state: State) -> typing.Any:
        state["__args__"] = (a.eval(state) for a in self.args)
        return state[self.function_name.encode().hex()](state)

    def compile(self) -> str:
        compiled_args = " ".join(f"({a.compile()} {STATEMONAD})" for a in self.args)
        return rf"(\{STATEMONAD} -> ({STATEMONAD} 0x{self.function_name.encode().hex()}) {compiled_args})"


class Statement(AST):
    def exec(self, state: State) -> State:
        raise NotImplementedError()

@dataclass
class Assignment(Statement):
    variable: str
    value: Expression

    def exec(self, state: State) -> State:
        state[self.variable.encode().hex()] = self.value.eval(state)
        return state

    def compile(self) -> str:
        compiled_e = self.value.compile()
        return rf"(\{STATEMONAD} -> (\x -> if (x ==b 0x{self.variable.encode().hex()}) then ({compiled_e} {STATEMONAD}) else ({STATEMONAD} x)))"


@dataclass
class Conjunction(Statement):
    first: Statement
    second: Statement

    def exec(self, state: State) -> State:
        state2 = self.first.exec(state)
        return self.second.exec(state2)

    def compile(self) -> str:
        compiled_f = self.first.compile()
        compiled_s = self.second.compile()
        return rf"(\{STATEMONAD} -> {compiled_s} ({compiled_f} {STATEMONAD}))"

@dataclass
class Trace(Statement):
    value: Expression

    def exec(self, state: State) -> State:
        print(self.value.eval(state))
        return state

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> ! Trace ({self.value.compile()} {STATEMONAD}) {STATEMONAD} )"


@dataclass
class While(Statement):
    cond: Expression
    stmt: Statement

    def exec(self, state: State) -> State:
        cur_state = state
        while(self.cond.eval(cur_state)):
            cur_state = self.stmt.exec(cur_state)
        return cur_state

    def compile(self) -> str:
        compiled_c = self.cond.compile()
        compiled_s = self.stmt.compile()
        return rf"(\{STATEMONAD} -> let g = (\s f -> if ({compiled_c} s) then f ({compiled_s} s) f else s) in (g {STATEMONAD} g))"

@dataclass
class Skip(Statement):

    def exec(self, state: State) -> State:
        return state

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> {STATEMONAD})"

@dataclass
class Program(AST):
    function: Function

    def exec(self, *args) -> State:
        state = {"__args__": args}
        return self.function.eval({})(state)

    def compile(self):
        return rf"({self.function.compile()} (\x -> 0))"

