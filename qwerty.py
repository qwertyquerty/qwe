import re
from config import *

class Interpreter():
    def __init__(self,text):
        self.line = 0
        self.vars = {}
        self.running = True
        self.lines = text.split("\n")
        self.lines = list(filter(lambda a: a != "", self.lines))
        self.do_else = None
        while self.line < len(self.lines) and self.running:
            self._interpret(self.lines[self.line])
            self.line = self.line + 1


    def _interpret(self,line):
        line = line.strip(" ")
        command = line.split(" ")[0]
        if command in COMMANDS:
            line = line.lstrip(command)

            if command != "else":
                self.do_else = None

            if command == "let":
                self.c_let(line)
            elif command == "log":
                self.c_log(line)
            elif command == "goto":
                self.c_goto(line)
            elif command == "exit":
                self.c_exit(line)
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
        lexed = list(filter((" ").__ne__, lexed))
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
        str_items = self._lex(line)
        items = []
        for item in str_items:
            if item not in OPERATORS:
                items.append(self._string_to_obj(item))
            else:
                items.append(item)

        return self._eval_rpn(self._tokens_to_rpn(items))

    def _eval_rpn(self,items):

        stack = []

        for item in items:
            if item in OPERATORS:
                rt = stack.pop()
                lt = stack.pop()
                stack.append(self._operate(lt,rt,item))
            else:
                stack.append(item)

        return stack.pop()


    def _op_less_than(self,op1,op2):
        return OPERATORS.index(op1)<=OPERATORS.index(op2)

    def _tokens_to_rpn(self,items):
        stack = []
        rpn = []

        for c in items:
            if type(c) == float or type(c) == int:
                rpn.append(c)
            elif c in OPERATORS:
                if c == "(":
                    stack.append(c)
                elif c == ")":
                    op = stack.pop()
                    while not op == "(":
                        rpn.append(op)
                        op = stack.pop()
                else:
                    while len(stack) > 0 and self._op_less_than(c,stack[-1]):
                        rpn.append(stack.pop())
                    stack.append(c)

        while len(stack) > 0:
            rpn.append(stack.pop())
        return rpn

    def _operate(self,lt,rt,op):
        if op == "+":
            return lt + rt
        elif op == "-":
            return lt + rt
        elif op == "/":
            return lt / rt
        elif op == "*":
            return lt * rt
        elif op == "%":
            return lt % rt
        elif op == "^":
            return lt ** rt
        elif op == "==":
            return int(lt == rt)
        elif op == "!=":
            return int(lt != rt)
        elif op == ">=":
            return int(lt >= rt)
        elif op == "<=":
            return int(lt <= rt)
        elif op == ">":
            return int(lt > rt)
        elif op == "<":
            return int(lt < rt)
        elif op == "and":
            return lt and rt
        elif op == "or":
            return lt or rt

    def c_let(self,line):
        var, val = line.split("=")
        var = var.replace(" ", "")
        val = self._eval(val)
        if RE_VARNAME.match(var) and len(var) > 0:
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
        condition, action = line.split("then")
        if self._eval(condition) != 0:
            self._interpret(action)
            self.do_else = False
        else:
            self.do_else = True

    def c_else(self,line):
        action = line
        if self.do_else != None:
            if self.do_else:
                self._interpret(action)
        else:
            self._error(4)
        self.do_else = None

i = Interpreter(open("test.qwe").read())
