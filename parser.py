from rply import ParserGenerator
import imp_ast as ast
import lexer

PRECEDENCE = [
    ('left', ["PLUS", "MINUS"]),
    ('left', ["MUL"]),
]

class Parser():

    def __init__(self):
        self.pg = ParserGenerator(lexer.TOKENS.keys())

        @self.pg.production("program : statement")
        def program(p):
            return ast.Program(p[0])

        @self.pg.production("function : FUNCTION PAREN_OPEN arguments PAREN_CLOSE BRACE_OPEN statement RETURN expression BRACE_CLOSE")
        def function2(p):
            return ast.Function(p[2], p[5], p[7])

        @self.pg.production("expression : function")
        def fun_exp(p):
            return p[0]

        @self.pg.production("expression : TEXT")
        def text(p):
            return ast.Text(p[0].value)

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

        @self.pg.production("statement : WHILE PAREN_OPEN expression PAREN_CLOSE BRACE_OPEN statement BRACE_CLOSE")
        def loop(p):
            return ast.While(p[2], p[5])

        @self.pg.production("statement : FOR PAREN_OPEN NAME DOUBLE_COLON expression PAREN_CLOSE BRACE_OPEN statement BRACE_CLOSE")
        def forloop(p):
            return ast.For(p[2].value, p[4], p[7])

        @self.pg.production("statement : IF PAREN_OPEN expression PAREN_CLOSE BRACE_OPEN statement BRACE_CLOSE ELSE BRACE_OPEN statement BRACE_CLOSE")
        def if_else(p):
            return ast.IfElse(p[2], p[5], p[9])

        @self.pg.production("statement : IF PAREN_OPEN expression PAREN_CLOSE BRACE_OPEN statement BRACE_CLOSE NOELSE")
        def if_noelse(p):
            return ast.IfElse(p[2], p[5], ast.Skip())

        @self.pg.production("statement : TRACE PAREN_OPEN expression PAREN_CLOSE")
        def trace(p):
            return ast.Trace(p[2])

        @self.pg.production("statement : ERROR PAREN_OPEN PAREN_CLOSE")
        def error(p):
            return ast.Error()

        @self.pg.production("statement : NAME EQUAL expression")
        def assignment(p):
            return ast.Assignment(p[0].value, p[2])

        @self.pg.production("statement : statement SEMI_COLON statement")
        def conjunction(p):
            return ast.Conjunction(p[0], p[2])

        @self.pg.production("statement : ")
        def skip(p):
            return ast.Skip()

        @self.pg.production("expression : NUMBER")
        def number(p):
            return ast.Number(p[0].value)

        @self.pg.production("expression : NAME")
        def variable(p):
            return ast.Variable(p[0].value)

        @self.pg.production("expression : expression BINOP expression")
        def binop(p):
            op = p[1].value
            return ast.BinaryOp(op, p[0], p[2])

        @self.pg.production("expression : BUILTIN PAREN_OPEN expression PAREN_CLOSE")
        def builtin(p):
            return ast.BuiltIn(p[0].value, p[2])

        @self.pg.production("expression : BRACK_OPEN parameters BRACK_CLOSE")
        def native_list(p):
            return ast.List(p[1])

        @self.pg.production("expression : FIELDS PAREN_OPEN expression PAREN_CLOSE")
        def fields(p):
            return ast.Fields(p[2])

        @self.pg.production("expression : expression BRACK_OPEN expression BRACK_CLOSE")
        def index_access(p):
            return ast.IndexAccess(p[0], p[2])

        @self.pg.production("expression : PAREN_OPEN expression PAREN_CLOSE")
        def paren(p):
            return p[1]

        @self.pg.production("expression : PAREN_OPEN PAREN_CLOSE")
        def unit(p):
            return ast.Unit()

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
