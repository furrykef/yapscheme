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


def ADD(env, argument_list):
    result = 0
    cur_cons = argument_list
    while cur_cons != tokens.EmptyList():
        result += env.runOne(cur_cons.car).value
        cur_cons = cur_cons.cdr
    return tokens.Number(result)

def SUB(env, argument_list):
    if argument_list == tokens.EmptyList():
        raise NotEnoughArgumentsError("Subtraction requires at least one argument")

    result = argument_list.car.value
    cur_cons = argument_list.cdr
    more_than_one_arg = False
    while cur_cons != tokens.EmptyList():
        more_than_one_arg = True
        result -= env.runOne(cur_cons.car).value
        cur_cons = cur_cons.cdr

    if not more_than_one_arg:
        # One argument means negation
        return tokens.Number(-result)
    else:
        return tokens.Number(result)

def MUL(env, argument_list):
    result = 1
    cur_cons = argument_list
    while cur_cons != tokens.EmptyList():
        result *= env.runOne(cur_cons.car).value
        cur_cons = cur_cons.cdr
    return tokens.Number(result)

def DEFINE(env, argument_list):
    if argument_list == tokens.EmptyList() or argument_list.cdr == tokens.EmptyList():
        raise NotEnoughArgumentsError("define: Not enough arguments")
    if argument_list.cdr.cdr != tokens.EmptyList():
        raise TooManyArgumentsError("define: Too many arguments")
    if not isinstance(argument_list.car, tokens.Identifier):
        raise BadArgumentError("define: First argument must be an identifier")
    env._sym_tbl[argument_list.car.value] = env.runOne(argument_list.cdr.car)

def QUOTE(env, argument_list):
    if argument_list == tokens.EmptyList():
        raise NotEnoughArgumentsError("quote: Not enough arguments")
    if argument_list.cdr != tokens.EmptyList():
        raise TooManyArgumentsError("quote: Too many arguments")
    return argument_list.car


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
        results = []
        for expression in parse_tree:
            results.append(self.runOne(expression))
        return results

    def runOne(self, expression):
        if isinstance(expression, tokens.Cons):
            if expression.isImproperList():
                raise ImproperListCallError

            operation = self.runOne(expression.car)
            if not callable(operation):
                raise NotCallableError("Not a macro or procedure")
            # @TODO@ - pre-evaluate arguments
            return operation(self, expression.cdr)
        elif isinstance(expression, tokens.EmptyList):
            raise NotCallableError("Empty list is not callable")
        elif isinstance(expression, tokens.Identifier):
            try:
                return self._sym_tbl[expression.value]
            except KeyError:
                raise UnknownIdentifier("Unknown identifier: {0}".format(expression.value))
        else:
            return expression
