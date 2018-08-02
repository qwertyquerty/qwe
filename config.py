import re

COMMANDS = [
    "let",
    "log",
    "goto",
    "exit",
    "if"
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


RE_LEX = re.compile(r"(\=\=|\-|\*|\\|\%|\+|\>\=|\<\=|\<|\>|\^|\)|\(|and|or| )")
