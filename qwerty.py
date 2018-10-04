import traceback

class Function():
    def __init__(self,name=None,args=None,lines=None,builtin=None):
        if lines == None:
            self.lines = []
        else:
            self.lines = lines

        self.args = args
        self.name = name

        if builtin:
            self.call = builtin

    def call(self, args, vars):
        self.i = Interpreter(self.lines,self.name)
        #print(self.lines)
        for key,val in vars.items():
            self.i.vars[key]=val

        for key,val in zip(self.args, args):
            self.i.vars[key]=val

        o = self.i._run()
        return o



class Operator():
    def __init__(self,type):
        self.type = type
        self.value = OPERATORS[self.type][1]
        self.op = OPERATORS[self.type][0]

    def operate(self,x,y,i):
        if type(x) == var:

            if self.type == "=":
                if RE_VARNAME.match(x.name) and len(x.name) > 0 and x.name not in COMMANDS and x.name not in OPERATORS.keys():
                    if type(y) == var:
                        if not y.set:
                            i._error(2,y.name)
                        y = y.val
                    x.vars[x.name] = y
                    return x.vars[x.name]
                else:
                    i._error(3,x.name)

            elif x.set:
                x = x.val
            else:
                i._error(2,x.name)

        if type(y) == var:
            if y.set:
                y = y.val
            else:
                i._error(2,y.name)

        return self.op(x,y)

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

class var():
    def __init__(self,name,val,vars,set=True):
        self.name = name
        self.val = val
        self.set = set
        self.vars = vars


class Interpreter():
    def __init__(self,lines=None, name=None):
        self.line = 0
        self.name = name
        self.vars = BUILTINS
        self.running = True
        self.do_else_stack = []
        self.nest_stack = []
        self.fn_line_stack = []
        self.lines = lines

    def _run(self):
        while self.line < len(self.lines) and self.running:
            #print(self.lines[self.line])
            out = self._interpret(self.lines[self.line])
            self.line = self.line + 1
            if out != None:
                return out
        return 0




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
                        self.nest_stack.append(["", False])
                        self.do_else_stack.append(False)
                    elif command == "else":
                        self.do_else_stack.pop(len(self.do_else_stack)-1)
                    elif command == "while":
                        self.nest_stack.append(["", False])
                    elif command == "fn":
                        self.nest_stack.append(["", False])

                    if command == "]":
                        last = self.nest_stack.pop(len(self.nest_stack)-1)
                        if last[0] == "fn":
                            last[2].lines = self.fn_line_stack.pop(len(self.fn_line_stack)-1)
                            self.vars[last[2].name] = last[2]

                    if len(self.fn_line_stack) > 0:
                        self.fn_line_stack[-1].append(self.lines[self.line])



                    return

                elif self.nest_stack[-1][1] == True:
                    if command == "]":
                        last = self.nest_stack.pop(len(self.nest_stack)-1)
                        if last[0] == "while":
                            self.line = last[2]-1



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
            elif command == "while":
                self.c_while(line)
            elif command == "return":
                return self.c_return(line)
            elif command == "fn":
                self.c_fn(line)
        else:


            if len(self.fn_line_stack) > 0:
                self.fn_line_stack[-1].append(line)
                return

            if len(self.nest_stack) > 0 and self.nest_stack[-1][1] == False:
                return

            self._eval(line)



    def _error(self,id,info=None):
        if info == None:
            print("[ERROR] "+ERRORS[id]+" in "+self.name+" on line "+str(self.line+1))
        else:
            print("[ERROR] "+ERRORS[id]+" in "+self.name+" on line "+str(self.line+1)+": "+info)

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

                if item in self.vars:
                    item = var(item,self.vars[item],self.vars)
                else:
                    item = var(item,None,self.vars,set=False)

        return item


    def _eval(self,line):
        if line == "":
            return
        in_str = False
        in_args = False
        args_gen = []
        arg_name = ""
        str_items = self._lex(line)
        items = []
        i = 0
        pars = 0
        #print("STRS "+str(str_items))
        for item in str_items:

            if in_args:

                #print("PARS "+str(pars), item)
                if item == "(":
                    if pars > -1:
                        args_gen[-1] += ("(")
                    pars = pars + 1


                elif item == ")":
                    if pars == 0:
                        args_gen[-1] = self._eval(args_gen[-1])
                        in_args = False
                        items.append(self.vars[fn_name].call(args_gen,self.vars))

                    else:
                        pars = pars - 1
                        args_gen[-1] += (")")

                elif item == "," and pars == 0:
                    args_gen[-1] = self._eval(args_gen[-1])
                    args_gen.append("")

                else:
                    args_gen[-1] += (item)

            else:
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

                            if i < len(str_items)-1  and str_items[i+1] == "(" and item != " ":
                                in_args = True
                                args_gen = [""]
                                fn_name = item
                                pars = -1

                            elif item != " ":
                                items.append(self._string_to_obj(item))
                        else:

                            items.append(Operator(item))
                    else:
                        str_gen += str(item)

            i += 1

        if in_str:
            self._error(5)

        out = self._eval_rpn(self._tokens_to_rpn(items))

        return out





    def _eval_rpn(self,items):
        stack = []

        for item in items:
            if type(item) == Operator:
                rt = stack.pop()
                lt = stack.pop()
                try:
                    stack.append(item.operate(lt,rt,self))
                except TypeError as r:
                    self._error(7,type(lt).__name__+" "+str(item)+" "+type(rt).__name__)
            else:
                stack.append(item)

        out = stack.pop()

        if type(out) == var:
            if out.set:
                out = out.val
            else:
                self._error(2,out.name)

        if type(out) == bool:
            out = int(out)

        return out

    def _tokens_to_rpn(self,tokens):
        stack = []
        rpn = []
        items = []
        in_parentheses = False
        for i in range(len(tokens)):

            item = tokens[i]

            items.append(item)

        for c in items:
            if type(c) == float or type(c) == int or type(c) == str or type(c) == var:
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


    def c_log(self,line):
        print(self._eval(line))

    def c_exit(self,line):
        exit()

    def c_if(self,line):
        if line[-1] == "[":
            condition = line.split("[")[0]
        else:
            self._error(0)

        if self._eval(condition) != 0:
            self.nest_stack.append(["if",True])
            self.do_else_stack.append(False)
        else:
            self.nest_stack.append(["if",False])
            self.do_else_stack.append(True)

    def c_else(self,line):
        if len(line) == 0 or line[-1] != "[":
            self._error(0)

        if len(self.do_else_stack) > 0:
            self.nest_stack.append(["else", bool(self.do_else_stack.pop(len(self.do_else_stack)-1))])

        else:
            self._error(4)

    def c_while(self,line):
        if line[-1] == "[":
            condition = line.split("[")[0]
        else:
            self._error(0)

        self.nest_stack.append(["while",bool(self._eval(condition)), self.line, condition])

    def c_fn(self,line):
        name,args = line.split("(")
        args = args.strip(" ").strip("[").strip(" ").strip(")").replace(" ", "").split(",")
        args = [arg for arg in args if arg != ""]
        name=name.strip(" ")
        fn = Function(name,args)
        self.nest_stack.append(["fn", False, fn])
        self.fn_line_stack.append([])


    def c_cls(self,line):
        os.system("cls")

    def c_wait(self,line):
        time.sleep(float(self._eval(line))/1000)

    def c_return(self,line):
        return self._eval(line)


from config import *
import re
import os
import time
