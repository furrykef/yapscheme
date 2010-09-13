#!/usr/bin/env python
from __future__ import division
import unittest

from yapscheme import Parser
from yapscheme.tokens import Cons, Identifier, NullCons, Number, String


def parseOne(arg):
    return Parser.parse(arg)[0]


# @TODO@ - more tests here!
class TestDataTypes(unittest.TestCase):
    def testNullCons(self):
        self.assertEqual(NullCons(), Cons(None, None))


class TestParser(unittest.TestCase):
    def testPositiveInteger(self):
        result = parseOne("7")
        self.assertEqual(result, Number(7))

    def testReallyPositiveInteger(self):
        result = parseOne("+7")
        self.assertEqual(result, Number(7))

    def testNegativeInteger(self):
        result = parseOne("-42")
        self.assertEqual(result, Number(-42))

    def testRejectIntegerContainingAlphas(self):
        with self.assertRaises(Parser.BadTokenError):
            parseOne("123abc")

    def testRejectIntegerWithInterposedPlusSign(self):
        with self.assertRaises(Parser.BadTokenError):
            parseOne("123+456")

    def testString(self):
        result = parseOne('"Hello mom"')
        self.assertEqual(result, String("Hello mom"))

    def testIgnoreWhitespace(self):
        result = parseOne(' \t\r\n\f\v"Hello mom" \t\r\n\f\v')
        self.assertEqual(result, String("Hello mom"))

    def testEscapeBackslash(self):
        result = parseOne(r'"Hello\\\\mom"')
        self.assertEqual(result, String(r"Hello\\mom"))

    def testEscapeDoublequote(self):
        result = parseOne(r'"Hello\"mom"')
        self.assertEqual(result, String('Hello"mom'))

    def testBadEscape(self):
        with self.assertRaises(Parser.EscapeError):
            parseOne(r'"Hello\mom"')

    def testUnterminatedString(self):
        with self.assertRaises(Parser.UnterminatedError):
            parseOne(r'"Hello mom')

    def testUnterminatedStringAfterBackslash(self):
        # I can't decide whether this should raise UnterminatedError or
        # EscapeError. What matters here is that an error is raised, so
        # I'll accept SyntaxError (the superclass of both).
        with self.assertRaises(Parser.SyntaxError):
            parseOne('"Hello mom\\')

    def testIgnoreComments(self):
        result = parseOne(";Comment\n7")
        self.assertEqual(result, Number(7))

    def testJustACommentProducesEmptyExpressionList(self):
        self.assertEqual(Parser.parse(";Comment"), [])

    def testSimpleDotPair(self):
        result = parseOne("(7 . 2)")
        self.assertEqual(result, Cons(Number(7), Number(2)))

    def testUnterminatedDotPair(self):
        with self.assertRaises(Parser.UnterminatedError):
            parseOne("(7 . 2")

    def testRejectStrayParen(self):
        # @TODO@ - more specific exception type?
        with self.assertRaises(Parser.BadTokenError):
            parseOne(")")

    def testRejectStrayDotOperator(self):
        # @TODO@ - more specific exception type?
        with self.assertRaises(Parser.BadTokenError):
            parseOne(".")

    def testImproperList(self):
        result = parseOne("(1 2 . 3)")
        self.assertEqual(result, Cons(Number(1), Cons(Number(2), Number(3))))

    def testRejectMoreThanOneExpressionAfterDotOperator(self):
        with self.assertRaises(Parser.BadDotPairError):
            parseOne("(1 2 . 3 4)")

    def testRejectDotPairWithNoCar(self):
        with self.assertRaises(Parser.BadDotPairError):
            parseOne("(. 7)")

    def testSimpleList(self):
        result = parseOne("(1 2 3)")
        self.assertEqual(result, Cons(Number(1), Cons(Number(2), Cons(Number(3), NullCons()))))

    def testIdentifier(self):
        result = parseOne("identifier")
        self.assertEqual(result, Identifier("identifier"))

    def testRejectIdentifierStartingWithPlus(self):
        with self.assertRaises(Parser.BadTokenError):
            result = parseOne("+id")

    def testRejectIdentifierStartingWithMinus(self):
        with self.assertRaises(Parser.BadTokenError):
            result = parseOne("-id")

    def testRejectIdentifierStartingWithDot(self):
        with self.assertRaises(Parser.BadTokenError):
            result = parseOne(".id")

    def testBarePlusIsAnIdentifier(self):
        result = parseOne("+")
        self.assertEqual(result, Identifier("+"))

    def testBareMinusIsAnIdentifier(self):
        result = parseOne("-")
        self.assertEqual(result, Identifier("-"))


if __name__ == '__main__':
    unittest.main()
