from . import tokens


class InterpreterError(Exception):
    pass

class NotEnoughArgumentsError(InterpreterError):
    pass

class TooManyArgumentsError(InterpreterError):
    pass

class BadArgumentError(InterpreterError):
    pass

class NotCallableError(InterpreterError):
    pass

class ImproperListCallError(InterpreterError):
    pass

class UnknownIdentifier(InterpreterError):
    pass


@tokens.PythonProcedure
def ADD(argument_list):
    result = 0
    for arg in argument_list:
        result += arg.value
    return tokens.Number(result)

@tokens.PythonProcedure
def SUB(argument_list):
    if len(argument_list) == 0:
        raise NotEnoughArgumentsError("Subtraction requires at least one argument")
    elif len(argument_list) == 1:
        # One argument means negation
        return tokens.Number(-argument_list[0].value)
    else:
        result = argument_list[0].value
        for arg in argument_list[1:]:
            result -= arg.value
        return tokens.Number(result)

@tokens.PythonProcedure
def MUL(argument_list):
    result = 1
    for arg in argument_list:
        result *= arg.value
    return tokens.Number(result)


@tokens.PythonMacro
def DEFINE(env, argument_cons):
    if argument_cons == tokens.EmptyList() or argument_cons.cdr == tokens.EmptyList():
        raise NotEnoughArgumentsError("define: Not enough arguments")
    if argument_cons.cdr.cdr != tokens.EmptyList():
        raise TooManyArgumentsError("define: Too many arguments")
    if not isinstance(argument_cons.car, tokens.Identifier):
        raise BadArgumentError("define: First argument must be an identifier")
    env._sym_tbl[argument_cons.car.value] = env.evalOne(argument_cons.cdr.car)

@tokens.PythonMacro
def IF(env, argument_cons):
    args = argument_cons.toPythonList()
    if len(args) < 2:
        raise NotEnoughArgumentsError("if requires at least two arguments")
    if len(args) > 3:
        raise TooManyArgumentsError("if can take at most three arguments")
    if env.evalOne(args[0]) != tokens.Bool(False):
        return env.evalOne(args[1])
    else:
        try:
            return env.evalOne(args[2])
        except IndexError:
            # If statement with no false branch
            return None

@tokens.PythonMacro
def LAMBDA(env, argument_cons):
    args = argument_cons.toPythonList()
    if len(args) < 2:
        raise NotEnoughArgumentsError("lambda: Not enough arguments")
    return _Lambda(argument_cons.car, argument_cons.cdr.car)

@tokens.PythonMacro
def QUOTE(env, argument_cons):
    if argument_cons == tokens.EmptyList():
        raise NotEnoughArgumentsError("quote: Not enough arguments")
    if argument_cons.cdr != tokens.EmptyList():
        raise TooManyArgumentsError("quote: Too many arguments")
    return argument_cons.car


class Interpreter(object):
    def __init__(self):
        self._sym_tbl = {
            '+': ADD,
            '-': SUB,
            '*': MUL,
            'define': DEFINE,
            'if': IF,
            'lambda': LAMBDA,
            'quote': QUOTE
        }

    def run(self, parse_tree):
        return [self.evalOne(expression) for expression in parse_tree]

    def evalOne(self, expression):
        if isinstance(expression, tokens.Cons):
            if expression.isImproperList():
                raise ImproperListCallError
            operation = self.evalOne(expression.car)
            if isinstance(operation, tokens.PythonProcedure):
                # A procedure evaluates its arguments first...
                args = expression.cdr.toPythonList()
                return operation.call(self.run(args))
            elif isinstance(operation, tokens.PythonMacro):
                # ...but a macro does not.
                return operation.call(self, expression.cdr)
            elif isinstance(operation, _Lambda):
                # A lambda does, though (@TODO@ - duplication?)
                args = expression.cdr.toPythonList()
                return operation.call(self, self.run(args))
            else:
                raise NotCallableError("Not a macro or procedure")
        elif isinstance(expression, tokens.EmptyList):
            raise NotCallableError("Empty list is not callable")
        elif isinstance(expression, tokens.Identifier):
            try:
                return self._sym_tbl[expression.value]
            except KeyError:
                raise UnknownIdentifier("Unknown identifier: {0}".format(expression.value))
        else:
            return expression


class _Lambda(object):
    def __init__(self, args, expr):
        self.args = args
        self.expr = expr

    def call(self, env, args):
        for identifier, arg_value in zip(self.args.toPythonList(), args):
            env._sym_tbl[identifier.value] = arg_value
        return env.evalOne(self.expr)
