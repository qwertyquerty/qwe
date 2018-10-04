from qwerty import Interpreter

i = Interpreter(open("fizzbuzz.qwe").read().split("\n"), "main")
i._run()
