from dataclasses import dataclass
from collections import defaultdict
import typing

from lexer import BUILTINS, BINOP

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
    op: str
    left: Expression
    right: Expression

    def eval(self, state: State):
        return BINOP[self.op][1](self.left.eval(state), self.right.eval(state))

    def compile(self) -> str:
        binop = BINOP[self.op][0]
        return rf"(\{STATEMONAD} -> (({self.left.compile()} {STATEMONAD}) {binop} ({self.right.compile()} {STATEMONAD})))"


@dataclass
class BuiltIn(Expression):
    function: str
    expression: Expression

    def eval(self, state: State):
        return BUILTINS[self.function][1](self.expression.eval(state))

    def compile(self) -> str:
        builtin = BUILTINS[self.function][0]
        return rf"(\{STATEMONAD} -> {builtin} ({self.expression.compile()} {STATEMONAD}))"

@dataclass
class Fields(Expression):
    value: Expression

    def exec(self, state: State) -> State:
        # All records/data types are modelled by python lists anyways, so just return them
        return self.value.eval(state)

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> ! ! SndPair (UnConstrData ({self.value.compile()} {STATEMONAD})))"


class Unit(Expression):

    def eval(self, state: State) -> typing.Any:
        return ()

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> ())"

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
            new_state = local_state.copy()
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

@dataclass
class List(Expression):
    args: typing.List[Number]

    def eval(self, state: State) -> typing.Any:
        return list(int(a.value) for a in self.args)

    def compile(self) -> str:
        compiled_args = ", ".join(a.value for a in self.args)
        return rf"(\{STATEMONAD} -> UnListData (data [{compiled_args}]))"

@dataclass
class IndexAccess(Expression):
    value: Expression
    index: Expression

    def eval(self, state: State) -> State:
        return self.value.eval(state)[self.index.eval(state)]

    def compile(self) -> str:
        compiled_v = self.value.compile()
        compiled_i = self.index.compile()
        return rf'(\{STATEMONAD} -> let g = (\i xs f -> if (!NullList xs) then (!Trace "OOB" (Error ())) else (if i ==i 0 then (!HeadList xs) else f (i -i 1) (!TailList xs) f)) in (g ({compiled_i} {STATEMONAD}) ({compiled_v} {STATEMONAD}) g))'

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
class Error(Statement):

    def exec(self, state: State) -> State:
        raise RuntimeError()

    def compile(self) -> str:
        # TODO: does this work??
        return rf"(\{STATEMONAD} -> Error ())"


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
class For(Statement):
    var: str
    expr: Expression
    stmt: Statement

    def exec(self, state: State) -> State:
        cur_state = state
        for elem in self.expr.eval(cur_state):
            cur_state[self.var.encode("utf8").hex()] = elem
            cur_state = self.stmt.exec(cur_state)
        return cur_state

    def compile(self) -> str:
        compiled_e = self.expr.compile()
        compiled_s = self.stmt.compile()
        assignment = rf"(\{STATEMONAD} -> (\x -> if (x ==b 0x{self.var.encode().hex()}) then (!HeadList xs) else ({STATEMONAD} x)))"
        conjuct_compiled = rf"(\{STATEMONAD} -> {compiled_s} ({assignment} {STATEMONAD}))"
        return rf"(\{STATEMONAD} -> let g = (\s xs f -> if (!NullList xs) then s else (f ({conjuct_compiled} s) (!TailList xs) f)) in (g {STATEMONAD} ({compiled_e} {STATEMONAD}) g))"

@dataclass
class Skip(Statement):

    def exec(self, state: State) -> State:
        return state

    def compile(self) -> str:
        return rf"(\{STATEMONAD} -> {STATEMONAD})"

@dataclass
class IfElse(Statement):
    cond: Expression
    if_stmt: Statement
    else_stmt: Statement

    def exec(self, state: State) -> State:
        cur_state = state
        if(self.cond.eval(cur_state)):
            cur_state = self.if_stmt.exec(cur_state)
        else:
            cur_state = self.else_stmt.exec(cur_state)
        return cur_state

    def compile(self) -> str:
        compiled_c = self.cond.compile()
        compiled_is = self.if_stmt.compile()
        compiled_es = self.else_stmt.compile()
        return rf"(\{STATEMONAD} -> if ({compiled_c} {STATEMONAD}) then ({compiled_is} {STATEMONAD}) else ({compiled_es} {STATEMONAD}))"


# program is an execution of all commands, then calling variable "main" with arguments
@dataclass
class Program(AST):
    stmt: Statement
    function_name = "main"

    def exec(self, *args) -> State:
        state = self.stmt.exec(defaultdict(int))
        state["__args__"] = args
        return state[self.function_name.encode().hex()](state)

    def compile(self):
        return rf'{self.stmt.compile()} (\x -> (!Trace "VNI" (Error ()))) 0x{self.function_name.encode().hex()}'

