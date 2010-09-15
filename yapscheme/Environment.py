from __future__ import division

from yapscheme import tokens


class EnvironmentError(Exception):
    pass

class NotEnoughArgumentsError(EnvironmentError):
    pass

class TooManyArgumentsError(EnvironmentError):
    pass

class BadArgumentError(EnvironmentError):
    pass

class NotCallableError(EnvironmentError):
    pass

class ImproperListCallError(EnvironmentError):
    pass

class UnknownIdentifier(EnvironmentError):
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
    env._sym_tbl[argument_cons.car.value] = env.runOne(argument_cons.cdr.car)

@tokens.PythonMacro
def QUOTE(env, argument_cons):
    if argument_cons == tokens.EmptyList():
        raise NotEnoughArgumentsError("quote: Not enough arguments")
    if argument_cons.cdr != tokens.EmptyList():
        raise TooManyArgumentsError("quote: Too many arguments")
    return argument_cons.car


class Environment(object):
    def __init__(self):
        self._sym_tbl = {
            '+': ADD,
            '-': SUB,
            '*': MUL,
            'define': DEFINE,
            'quote': QUOTE
        }

    def run(self, parse_tree):
        return [self.runOne(expression) for expression in parse_tree]

    def runOne(self, expression):
        if isinstance(expression, tokens.Cons):
            if expression.isImproperList():
                raise ImproperListCallError
            operation = self.runOne(expression.car)
            if isinstance(operation, tokens.PythonProcedure):
                # A procedure evaluates its arguments first...
                # (@TODO@ - consider adding traverse() and toPythonList() to EmptyList
                #  in order to avoid this kind of special-casing)
                if expression.cdr == tokens.EmptyList():
                    args = []
                else:
                    args = expression.cdr.toPythonList()
                return operation.call(self.run(args))
            elif isinstance(operation, tokens.PythonMacro):
                # ...but a macro does not.
                return operation.call(self, expression.cdr)
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
