import re
import os
import time
from config import *


class Operator():
    def __init__(self,type):
        self.type = type
        self.value = OPERATORS[self.type][1]
        self.operate = OPERATORS[self.type][0]
    def __str__(self):
        return self.type
    def __repr__(self):
        return self.type
    def __gt__(self,other):
        return self.value > other.value
    def __lt__(self,other):
        return self.value < other.value
    def __le__(self,other):
        return self.value <= other.value
    def __ge__(self,other):
        return self.value >= other.value



class Interpreter():
    def __init__(self,text):
        self.line = 0
        self.vars = {}
        self.running = True
        self.lines = text.split("\n")
        self.do_else_stack = []
        self.nest_stack = []
        while self.line < len(self.lines) and self.running:
            self._interpret(self.lines[self.line])
            self.line = self.line + 1


    def _interpret(self,line):
        line = line.strip(" ")
        line = line.replace("\\n", "\n")
        comments = RE_COMMENT.search(line)

        if comments:
            line = line.replace(comments.group(1), "")
        if line == "":
            return

        command = line.split(" ")[0]
        if command in COMMANDS:

            line = line.lstrip(command)

            if len(self.nest_stack) > 0:
                if self.nest_stack[-1][1] == False:
                    if command == "if":
                        self.nest_stack.append(["if", False])
                        self.do_else_stack.append(False)
                    elif command == "else":
                        self.do_else_stack.pop(len(self.do_else_stack)-1)
                    elif command == "end":
                        last = self.nest_stack.pop(len(self.nest_stack)-1)
                    return

                elif self.nest_stack[-1][1] == True:
                    if command == "end":
                        last = self.nest_stack.pop(len(self.nest_stack)-1)
                        return


            if command == "let":
                self.c_let(line)
            elif command == "log":
                self.c_log(line)
            elif command == "goto":
                self.c_goto(line)
            elif command == "exit":
                self.c_exit(line)
            elif command == "cls":
                self.c_cls(line)
            elif command == "wait":
                self.c_wait(line)
            elif command == "if":
                self.c_if(line)
            elif command == "else":
                self.c_else(line)
        else:
            self._error(1,command)

    def _error(self,id,info=None):
        if info == None:
            print("[ERROR] "+ERRORS[id]+" on line "+str(self.line+1))
        else:
            print("[ERROR] "+ERRORS[id]+" on line "+str(self.line+1)+": "+info)
        exit()

    def _lex(self,line):
        lexed =  RE_LEX.split(line)
        lexed = list(filter(("").__ne__, lexed))
        return lexed


    def _string_to_obj(self,item):
        try:
            item = int(item)
        except:
            try:
                item = float(item)
            except:
                try:
                    item = self.vars[item]
                except KeyError:
                    self._error(2,item)
        return item


    def _eval(self,line):
        in_str = False
        str_items = self._lex(line)
        items = []
        for item in str_items:
            if item == "\"":
                if not in_str:
                    str_gen = ""
                    in_str = True
                else:
                    str_gen = str_gen.replace('\\"',"\"")
                    items.append(str_gen)
                    in_str = False
            else:
                if not in_str:
                    if item not in OPERATORS:
                        if item != " ":
                            items.append(self._string_to_obj(item))
                    else:
                        items.append(Operator(item))
                else:
                    str_gen += str(item)

        if in_str:
            self._error(5)

        return self._eval_rpn(self._tokens_to_rpn(items))

    def _eval_rpn(self,items):

        stack = []

        for item in items:
            if type(item) == Operator:
                rt = stack.pop()
                lt = stack.pop()
                try:

                    if (type(rt) == str and type(lt)) == int or (type(lt) == str and type(rt) == int) and item.type == "+":
                        if type(rt) == int:
                            rt = str(rt)
                        elif type(lt) == int:
                            lt = str(lt)

                    stack.append(item.operate(lt,rt))
                except TypeError:
                    self._error(7,type(lt).__name__+" "+str(item)+" "+type(rt).__name__)
            else:
                stack.append(item)

        return stack.pop()


    def _tokens_to_rpn(self,tokens):
        stack = []
        rpn = []
        items = []
        in_parentheses = False

        for i in range(len(tokens)):
            item = tokens[i]
            if (type(item) == Operator and item.type == "-") and (i == 0 or (type(tokens[i-1]) == Operator and not tokens[i-1].type in PARENTHESES)) and (type(tokens[i+1]) == float or type(tokens[i+1]) == int):
                tokens[i+1] = tokens[i+1] * -1

            else:
                items.append(item)

        for c in items:
            if type(c) == float or type(c) == int or type(c) == str:
                rpn.append(c)

            elif type(c) == Operator:
                if c.type == "(":
                    stack.append(c)
                    in_parentheses = True
                elif c.type == ")":
                    op = stack.pop()
                    in_parentheses = False
                    while not op.type == "(":
                        rpn.append(op)
                        op = stack.pop()
                else:
                    while len(stack) > 0 and c<=stack[-1]:
                        rpn.append(stack.pop())
                    stack.append(c)

        while len(stack) > 0:
            rpn.append(stack.pop())

        if in_parentheses:
            self._error(6)
        return rpn


    def c_let(self,line):
        var, val = line.split("=")
        var = var.replace(" ", "")
        val = self._eval(val)
        if RE_VARNAME.match(var) and len(var) > 0 and var not in COMMANDS:
            self.vars[var] = val
        else:
            self._error(3,var)

    def c_log(self,line):
        print(self._eval(line))

    def c_goto(self,line):
        self.line = self._eval(line)-2

    def c_exit(self,line):
        exit()

    def c_if(self,line):
        condition = line
        if self._eval(condition) != 0:
            self.nest_stack.append(["if",True])
            self.do_else_stack.append(False)
        else:
            self.nest_stack.append(["if",False])
            self.do_else_stack.append(True)

    def c_else(self,line):
        if len(self.do_else_stack) > 0:
            if self.do_else_stack.pop(len(self.do_else_stack)-1):
                self.nest_stack.append(["else", True])
            else:
                self.nest_stack.append(["else", False])
        else:
            self._error(4)

    def c_cls(self,line):
        os.system("cls")

    def c_wait(self,line):
        time.sleep(float(self._eval(line))/1000)


i = Interpreter(open("bottlesofbeer.qwe").read())
