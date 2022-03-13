from lexer import Lexer
from parser import Parser

program = """
function (input) {
   foo = function(a){return a + 3};
   x = (1 + foo(input)) + 3;
   n = 3;
   while(n){
      x = x + 1;
      n = n - 1
   };
   return x
}"""

lexer = Lexer().get_lexer()
parser = Parser().get_parser()
tokens = lexer.lex(program)
ast = parser.parse(tokens)

print(ast.eval({})({"__args__": [5]}))
