from rply import ParserGenerator
import imp_ast as ast
import lexer

class Parser():

    def __init__(self):
        self.pg = ParserGenerator(lexer.TOKENS.keys())

        @self.pg.production("program : function")
        def program(p):
            return ast.Program(p[0])

        @self.pg.production("function : FUNCTION PAREN_OPEN arguments PAREN_CLOSE BRACK_OPEN RETURN expression BRACK_CLOSE")
        def function(p):
            return ast.Function(p[2], ast.Skip(), p[6])

        @self.pg.production("function : FUNCTION PAREN_OPEN arguments PAREN_CLOSE BRACK_OPEN statement PIPE RETURN expression BRACK_CLOSE")
        def function2(p):
            return ast.Function(p[2], p[5], p[8])

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

        @self.pg.production("statement : WHILE PAREN_OPEN expression PAREN_CLOSE BRACK_OPEN statement BRACK_CLOSE")
        def loop(p):
            return ast.While(p[2], p[5])

        @self.pg.production("statement : TRACE PAREN_OPEN expression PAREN_CLOSE")
        def trace(p):
            return ast.Trace(p[2])

        @self.pg.production("statement : NAME EQUAL expression")
        def assignment(p):
            return ast.Assignment(p[0].value, p[2])

        @self.pg.production("statement : statement SEMI_COLON statement")
        def conjunction(p):
            return ast.Conjunction(p[0], p[2])

        @self.pg.production("expression : NUMBER")
        def number(p):
            return ast.Number(p[0].value)

        @self.pg.production("expression : NAME")
        def variable(p):
            return ast.Variable(p[0].value)

        @self.pg.production("expression : expression PLUS expression")
        @self.pg.production("expression : expression MINUS expression")
        @self.pg.production("expression : expression MUL expression")
        @self.pg.production("expression : expression EQUAL expression")
        @self.pg.production("expression : expression LESS expression")
        def binop(p):
            op = p[1].gettokentype()
            if(op == "PLUS"):
                return ast.Sum(p[0], p[2])
            if(op == "MINUS"):
                return ast.Sub(p[0], p[2])
            if(op == "MUL"):
                return ast.Mul(p[0], p[2])
            if(op == "EQUAL"):
                return ast.Eq(p[0], p[2])
            if(op == "LESS"):
                return ast.Less(p[0], p[2])

        @self.pg.production("expression : INT expression")
        def intcast(p):
            return ast.IntCast(p[1])

        @self.pg.production("expression : PAREN_OPEN expression PAREN_CLOSE")
        def paren(p):
            return p[1]

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
