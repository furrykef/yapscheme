from __future__ import division

# @TODO@ - disallow comparing, e.g., a Number and a String?
# What about disallowing comparing strings except with == and !=?

# @TODO@ - unit test these methods??
class _Comparable(object):
    def __init__(self, value):
        self.value = value

    # Since Python 3.x doesn't have __cmp__ anymore
    def __lt__(self, other):
        return self.value < other.value
    def __gt__(self, other):
        return self.value > other.value
    def __eq__(self, other):
        return self.value == other.value
    def __le__(self, other):
        return self.value <= other.value
    def __ge__(self, other):
        return self.value >= other.value
    def __ne__(self, other):
        return self.value != other.value

    def __str__(self):
        return str(self.value)

class Number(_Comparable):
    pass

class String(_Comparable):
    pass


# @TODO@ -- disallow comparison of atoms beyond == and !=
# Also disallow comparison of atoms and strings
class Identifier(_Comparable):
    pass


class Cons(object):
    __slots__ = ['car', 'cdr']
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __eq__(self, other):
        # @XXX@ - the exception handling is a hack of the highest order!!
        try:
            return self.car == other.car and self.cdr == other.cdr
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        if self.car is None and self.cdr is None:
            return '()'
        return '(' + str(self.car) + ' . ' + str(self.cdr) + ')'


def NullCons():
    return Cons(None, None)


# Used internally by parser
class DotOperator(object):
    pass

# Ditto
class CloseParen(object):
    pass
