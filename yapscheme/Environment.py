from __future__ import division

from yapscheme import tokens


class EnvironmentError(Exception):
    pass

class NotEnoughArgumentsError(EnvironmentError):
    pass

class TooManyArgumentsError(EnvironmentError):
    pass

class NotCallableError(EnvironmentError):
    pass

class ImproperListCallError(EnvironmentError):
    pass


class Environment(object):
    def run(self, parse_tree):
        results = []
        for expression in parse_tree:
            results.append(self.runOne(expression))
        return results

    def runOne(self, expression):
        if isinstance(expression, tokens.Cons):
            if expression.isImproperList():
                raise ImproperListCallError

            operation = expression.car
            if not isinstance(operation, tokens.Identifier):
                raise NotCallableError("Not a macro or procedure")
            if operation == tokens.Identifier('+'):
                result = 0
                cell = expression.cdr
                while cell != tokens.EmptyList():
                    if isinstance(cell.car, tokens.Cons):
                        # Procedure call
                        value = self.runOne(cell.car).value
                    else:
                        # Just an expression
                        value = cell.car.value
                    result += value
                    cell = cell.cdr
                return tokens.Number(result)
            elif operation == tokens.Identifier('quote'):
                if expression.cdr == tokens.EmptyList():
                    raise NotEnoughArgumentsError("quote: Not enough arguments")
                if expression.cdr.cdr != tokens.EmptyList():
                    raise TooManyArgumentsError("quote: Too many arguments")
                return expression.cdr.car
        elif isinstance(expression, tokens.EmptyList):
            raise NotCallableError("Empty list is not callable")
        else:
            return expression
