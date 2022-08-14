from rply import LexerGenerator
import re

BUILTINS = {
    "int": ("UnIData", int),
    "list": ("UnListData", list),
    "head": ("HeadList", lambda x: x[0]),
    "tail": ("TailList", lambda x: x[1:]),
    "null": ("NullList", bool),
}
BINOP = {
    "<i": ("<i", lambda x, y: x < y),
    "=i": ("==i", lambda x, y: x == y),
    "=s": ("==s", lambda x, y: x == y),
    "=d": ("==d", lambda x, y: x == y),
    "+": ("+i", lambda x, y: x + y),
    "-": ("-i", lambda x, y: x - y),
    "*": ("*i", lambda x, y: x * y),
}

TOKENS = {
    "FUNCTION": "function",
    "RETURN": "return",
    "WHILE": "while",
    "FOR": "for",
    "TRACE": "trace",
    "ERROR": "error",
    "IF": "if",
    "ELSE": "else",
    "NOELSE": "noelse",
    "FIELDS": "fields",
    "BUILTIN": f"({'|'.join(map(re.escape, BUILTINS.keys()))})",
    "PAREN_OPEN": "\(",
    "PAREN_CLOSE": "\)",
    "BRACE_OPEN": "\{",
    "BRACE_CLOSE": "\}",
    "BRACK_OPEN": "\[",
    "BRACK_CLOSE": "\]",
    "SEMI_COLON": "\;",
    "DOUBLE_COLON": "\:\:",
    "TEXT": r'"[^\r\n"]*"',
    "EQUAL": "\:=",
    "BINOP": f"({'|'.join(map(re.escape, BINOP.keys()))})",
    "COMMA": ",",
    "NUMBER": "\d+",
    "NAME": "\w(\w|\d)*",
}


class Lexer:
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        for k, v in TOKENS.items():
            self.lexer.add(k, v)
        self.lexer.ignore("\s+")

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
