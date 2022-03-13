from dataclasses import dataclass
import typing

State = typing.Dict[str, typing.Any]
RV = typing.Tuple[typing.Any, State]


class Expression:
    def eval(self, state: State) -> typing.Any:
        raise NotImplementedError()


@dataclass
class Number(Expression):
    value: str

    def eval(self, state):
        return int(self.value)


@dataclass
class Variable(Expression):
    name: str

    def eval(self, state):
        return state[self.name]


@dataclass
class BinaryOp(Expression):
    left: Expression
    right: Expression


@dataclass
class Sum(BinaryOp):
    def eval(self, state: State):
        return self.left.eval(state) + self.right.eval(state)


@dataclass
class Function(Expression):
    args: typing.List[str]
    body: "Statement"

    def eval(self, state: State) -> typing.Any:
        # at this point, the arguments are in the state
        # as variables with the special value "__args__"
        def fun(s: State):
            new_state = {a: v for a, v in zip(self.args, s["__args__"])}
            return self.body.exec(new_state)[0]
        return fun

@dataclass
class FunctionCall(Expression):
    function_name: str
    args: typing.List[Expression]

    def eval(self, state: State) -> typing.Any:
        state["__args__"] = (a.eval(state) for a in self.args)
        return state[self.function_name](state)


class Statement:
    def exec(self, state: State) -> RV:
        raise NotImplementedError()

@dataclass
class Assignment(Statement):
    variable: str
    value: Expression

    def exec(self, state: State) -> RV:
        state[self.variable] = self.value.eval(state)
        return ((), state)

@dataclass
class Ret(Statement):
    value: Expression

    def exec(self, state: State) -> RV:
        return (self.value.eval(state), state)

@dataclass
class Conjunction(Statement):
    first: Statement
    second: Statement

    def exec(self, state: State) -> RV:
        state2 = self.first.exec(state)[1]
        return self.second.exec(state)
