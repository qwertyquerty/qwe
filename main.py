from qwerty import Interpreter

i = Interpreter(open("test.qwe").read().split("\n"), "main")
i._run()
