import argparse
import enum
import sys

import imp_ast as ast
from lexer import Lexer
from parser import Parser


class Command(enum.Enum):
    compile = "compile"
    eval = "eval"
    parse = "parse"


def main():
    a = argparse.ArgumentParser(description="An evaluator and compiler for the imperator programming language. Translate imperative programs into functional quasi-assembly.")
    a.add_argument("command", type=str, choices=Command.__members__.keys(), help="The command to execute on the input file.")
    a.add_argument("input_file", type=str, help="The input program to parse. Set to - for stdin.")
    a.add_argument("args", nargs="*", default=[], help="Input parameters for the function, in case the command is eval.")
    args = a.parse_args()
    command = Command(args.command)
    input_file = args.input_file if args.input_file != "-" else sys.stdin
    with open(input_file, "r") as f:
        source_code = "".join(l for l in f)

    lexer = Lexer().get_lexer()
    parser = Parser().get_parser()
    tokens = lexer.lex(source_code)

    if command == Command.parse:
        print("Parsed successfully.")
        return
    program: ast.Program = parser.parse(tokens)

    if command == Command.compile:
        print(program.compile())
    elif command == Command.eval:
        print(program.exec(*args.args))

if __name__ == '__main__':
    main()
