from lexer import Lexer
from parser import Parser

program = """
function (input) {
   input = int input;
   foo = function(a){return a + 3};
   x = (1 + foo(input)) + 3;
   n = 3;
   while(0 < n){
      x = x + 1;
      n = n - 1
   }|
   return x
}"""
# program = """
# function(b){
#   a = function(c){return b}|
#   return a(0)
# }"""

lexer = Lexer().get_lexer()
parser = Parser().get_parser()
tokens = lexer.lex(program)
ast  = parser.parse(tokens)

print(ast.exec(5))
print(ast.compile())
