from rply import ParserGenerator
import ast
import lexer

class Parser():

    def __init__(self):
        self.pg = ParserGenerator(lexer.TOKENS.keys())

        @self.pg.production("program : expression")
        def program(p):
            return p[0]

        @self.pg.production("expression : FUNCTION PAREN_OPEN arguments PAREN_CLOSE BRACK_OPEN statement BRACK_CLOSE")
        def function(p):
            return ast.Function(p[2], p[5])

        @self.pg.production("expression : NAME PAREN_OPEN parameters PAREN_CLOSE")
        def function_call(p):
            return ast.FunctionCall(p[0].value, p[2])

        @self.pg.production("parameters : expression")
        def parameter(p):
            return [p[0]]

        @self.pg.production("parameters : expression COMMA parameters")
        def parameters(p):
            return [p[0]] + p[2]

        @self.pg.production("arguments : NAME")
        def argument(p):
            return [p[0].value]

        @self.pg.production("arguments : NAME COMMA arguments")
        def arguments(p):
            return [p[0].value] + p[2]

        @self.pg.production("statement : NAME EQUAL expression")
        def assignment(p):
            return ast.Assignment(p[0].value, p[2])

        @self.pg.production("statement : statement SEMI_COLON statement")
        def conjunction(p):
            return ast.Conjunction(p[0], p[2])

        @self.pg.production("statement : RETURN expression")
        def ret(p):
            return ast.Ret(p[1])

        @self.pg.production("expression : NUMBER")
        def number(p):
            return ast.Number(p[0].value)

        @self.pg.production("expression : NAME")
        def variable(p):
            return ast.Variable(p[0].value)

        @self.pg.production("expression : expression PLUS expression")
        def binop(p):
            return ast.Sum(p[0], p[2])

        @self.pg.production("expression : expression PLUS expression")
        def binop(p):
            return ast.Sum(p[0], p[2])

        @self.pg.production("expression : PAREN_OPEN expression PAREN_CLOSE")
        def binop(p):
            return p[1]

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
