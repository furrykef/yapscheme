from __future__ import division

# @TODO@ - disallow comparing, e.g., a Number and a String?
# What about disallowing comparing strings except with == and !=?

# @TODO@ - unit test these methods??
class _Comparable(object):
    def __init__(self, value):
        self.value = value

    # Since Python 3.x doesn't have __cmp__ anymore
    # @TODO@ -- __class__ comparison is a *severe* hack
    def __lt__(self, other):
        if not self.__class__ == other.__class__:
            return False
        return self.value < other.value
    def __gt__(self, other):
        if not self.__class__ == other.__class__:
            return False
        return self.value > other.value
    def __eq__(self, other):
        if not self.__class__ == other.__class__:
            return False
        return self.value == other.value
    def __le__(self, other):
        if not self.__class__ == other.__class__:
            return False
        return self.value <= other.value
    def __ge__(self, other):
        if not self.__class__ == other.__class__:
            return False
        return self.value >= other.value
    def __ne__(self, other):
        if not self.__class__ == other.__class__:
            return False
        return self.value != other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        # @TODO@ - hack?
        return "{0}({1})".format(self.__class__.__name__, self.value)


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

    # @TODO@ - unit testing on each execution path?
    def isImproperList(self):
        if self.cdr == EmptyList():
            return False
        if not isinstance(self.cdr, Cons):
            return True
        return self.cdr.isImproperList()

    # Assumes self.isImproperList() is false
    def toPythonList(self):
        return [x for x in self.traverse()]

    # Assumes self.isImproperList() is false
    def traverse(self):
        cons = self
        while True:
            if cons == EmptyList():
                return
            yield cons.car
            cons = cons.cdr

    def __eq__(self, other):
        if not isinstance(other, Cons):
            return False
        return self.car == other.car and self.cdr == other.cdr

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return '(' + str(self.car) + ' . ' + str(self.cdr) + ')'


class EmptyList(object):
    def __eq__(self, other):
        return isinstance(other, EmptyList)

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return "()"


class Callable(object):
    pass

class PythonCallable(Callable):
    def __init__(self, call):
        self.call = call

class PythonProcedure(PythonCallable):
    pass

class PythonMacro(PythonCallable):
    pass


# Used internally by parser
class DotOperator(object):
    pass

# Ditto
class CloseParen(object):
    pass
