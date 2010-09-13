from __future__ import division

from yapscheme import tokens


class EnvironmentError(Exception):
    pass

class NotEnoughArgumentsError(EnvironmentError):
    pass

class TooManyArgumentsError(EnvironmentError):
    pass


class Environment(object):
    def __init__(self, parse_tree):
        self.__parse_tree = parse_tree

    def run(self, parse_tree=None):
        if parse_tree is None:
            # @TODO@ - if self.__parse_tree hasn't been set?
            parse_tree = self.__parse_tree

        for expression in parse_tree:
            if isinstance(expression, tokens.Cons):
                operation = expression.car
                if operation == tokens.Identifier('+'):
                    result = 0
                    cell = expression.cdr
                    while cell != tokens.NullCons():
                        if isinstance(cell.car, tokens.Cons):
                            # Procedure call
                            # @TODO@ - having to stick it in a list feels silly
                            value = self.run([cell.car]).value
                        else:
                            # Just an expression
                            value = cell.car.value
                        result += value
                        cell = cell.cdr
                    return tokens.Number(result)
                elif operation == tokens.Identifier('quote'):
                    if expression.cdr == tokens.NullCons():
                        raise NotEnoughArgumentsError()
                    if expression.cdr.cdr != tokens.NullCons():
                        raise TooManyArgumentsError()
                    return expression.cdr.car
            else:
                return expression
