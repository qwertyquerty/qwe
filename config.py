import re

COMMANDS = [
    "let",
    "log",
    "goto",
    "exit",
    "if",
    "else",
    "cls",
    "wait"
]

OPERATORS = [
 ")",
 "(",
 "and",
 "or",
 "==",
 "!=",
 ">=",
 "<=",
 ">",
 "<",
 "-",
 "+",
 "%",
 "/",
 "*",
 "^"
]

ERRORS = {
    0: "invalid syntax",
    1: "invalid command",
    2: "undefined variable",
    3: "invalid variable name",
    4: "else without if"
}


RE_LEX = re.compile(r"(\=\=|\-|\*|\\|\%|\+|\>\=|\<\=|\<|\>|\^|\)|\(|and|or| )")
RE_VARNAME = re.compile(r"^[A-Za-z0-9_]*$")
