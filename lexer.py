from rply import LexerGenerator

TOKENS = {
    "FUNCTION": "function",
    "RETURN": "return",
    "WHILE": "while",
    "PAREN_OPEN": "\(",
    "PAREN_CLOSE": "\)",
    "BRACK_OPEN": "\{",
    "BRACK_CLOSE": "\}",
    "SEMI_COLON": "\;",
    "PIPE": "\|",
    "PLUS": "\+",
    "MINUS": "\-",
    "MUL": "\*",
    "EQUAL": "=",
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
