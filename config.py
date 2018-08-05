import re

COMMANDS = [
    "let",
    "log",
    "goto",
    "exit",
    "if",
    "else",
    "cls",
    "wait",
    "end"
]

OPERATORS = {
 ")": [lambda x, y: (x,y), 0],
 "(": [lambda x, y: (x,y), 0],
 "and": [lambda x, y: x and y, 1],
 "or": [lambda x, y: x or y, 1],
 "==": [lambda x, y: x == y, 2],
 "!=": [lambda x, y: x != y, 2],
 ">=": [lambda x, y: x >= y, 3],
 "<=": [lambda x, y: x <= y, 3],
 ">": [lambda x, y: x > y, 3],
 "<": [lambda x, y: x < y, 3],
 "-": [lambda x, y: x - y, 4],
 "+": [lambda x, y: x + y, 4],
 "%": [lambda x, y: x % y, 5],
 "/": [lambda x, y: x / y, 5],
 "*": [lambda x, y: x * y, 5],
 "^": [lambda x, y: x ** y, 6]
}

ERRORS = {
    0: "invalid syntax",
    1: "invalid command",
    2: "undefined variable",
    3: "invalid variable name",
    4: "else without if",
    5: "unclosed string",
    6: "unclosed parentheses",
    7: "invalid operand"
}

PARENTHESES = ["(", ")"]

RE_LEX = re.compile(r'(\\"|"|\=\=|\-|\*|\\|\%|\+|\>\=|\<\=|\<|\>|\^|\)|\(|and|or| )')
RE_COMMENT = re.compile(r"(#.*)")
RE_VARNAME = re.compile(r"^[A-Za-z0-9_]*$")
