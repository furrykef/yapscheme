#!/usr/bin/env python
from __future__ import division
import unittest

from yapscheme import Parser
from yapscheme import Environment
from yapscheme.tokens import Cons, EmptyList, Identifier, Number, String


def parseOne(arg):
    # 2to3.py will convert the below 'unicode' to a superfluous 'str'
    return Parser.parse(unicode(arg))[0]

def run(arg):
    # 2to3.py will convert the below 'unicode' to a superfluous 'str'
    return Environment.Environment().run(Parser.parse(unicode(arg)))

def runOne(arg):
    return Environment.Environment().runOne(parseOne(arg))


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
        self.assertEqual(Parser.parse(u";Comment"), [])

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
        self.assertEqual(result, Cons(Number(1), Cons(Number(2), Cons(Number(3), EmptyList()))))

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

    def testEmptyList(self):
        self.assertEqual(parseOne("()"), EmptyList())


class TestBareEnvironment(unittest.TestCase):
    def testInteger(self):
        self.assertEqual(runOne("-1337"), Number(-1337))

    def testQuoteInteger(self):
        self.assertEqual(runOne("(quote 7)"), Number(7))

    def testRejectQuoteWithMultipleArguments(self):
        with self.assertRaises(Environment.TooManyArgumentsError):
            runOne("(quote 7 2)")

    def testRejectQuoteWithNoArguments(self):
        with self.assertRaises(Environment.NotEnoughArgumentsError):
            runOne("(quote)")

    def testQuoteList(self):
        self.assertEqual(runOne("(quote (1 2 3))"), Cons(Number(1), Cons(Number(2), Cons(Number(3), EmptyList()))))

    def testAdditionOfTwoOperands(self):
        self.assertEqual(runOne("(+ 123 456)"), Number(579))

    def testAdditionOfThreeOperands(self):
        self.assertEqual(runOne("(+ 1 2 3)"), Number(6))

    def testAdditionOfNoOperands(self):
        self.assertEqual(runOne("(+)"), Number(0))

    def testNestedAddition(self):
        self.assertEqual(runOne("(+ (+ 1 2) (+ 3 4))"), Number(10))

    def testRejectNullProcedure(self):
        with self.assertRaises(Environment.NotCallableError):
            runOne("()")

    def testRejectNumberAsProcedure(self):
        with self.assertRaises(Environment.NotCallableError):
            runOne("(27)")

    def testRejectProcedureCallWithDot(self):
        with self.assertRaises(Environment.ImproperListCallError):
            runOne("(+ 1 . 2)")

    def testRejectUnknownIdentifier(self):
        with self.assertRaises(Environment.UnknownIdentifier):
            runOne("this-does-not-exist")

    def testRejectCallingUnknownIdentifier(self):
        with self.assertRaises(Environment.UnknownIdentifier):
            runOne("(this-does-not-exist)")

    def testDefine(self):
        result = run("(define the-answer 42) the-answer")
        self.assertEqual(result, [None, Number(42)])

    def testRejectDefineWithTooManyArguments(self):
        with self.assertRaises(Environment.TooManyArgumentsError):
            runOne("(define hello 2 3)")

    def testRejectDefineWithNoArguments(self):
        with self.assertRaises(Environment.NotEnoughArgumentsError):
            runOne("(define)")

    def testRejectDefineWithOneArgument(self):
        with self.assertRaises(Environment.NotEnoughArgumentsError):
            runOne("(define foo)")

    def testDefineRequiresAnIdentifierAsFirstArgument(self):
        with self.assertRaises(Environment.BadArgumentError):
            runOne("(define 7 2)")

    def testSubtraction(self):
        self.assertEqual(runOne("(- 2 7)"), Number(-5))

    def testRejectSubtrationWithNoOperands(self):
        with self.assertRaises(Environment.NotEnoughArgumentsError):
            runOne("(-)")

    def testSubtractionWithOneOperandIsNegation(self):
        self.assertEqual(runOne("(- 8)"), Number(-8))

    def testMultiplication(self):
        self.assertEqual(runOne("(* 7 2)"), Number(14))

    def testMultiplicationWithNoOperands(self):
        self.assertEqual(runOne("(*)"), Number(1))

    def testAdditionWithDefine(self):
        result = run("(define one 1) (+ one one)")
        self.assertEqual(result, [None, Number(2)])

    def testDefiningAliasForProcedure(self):
        result = run("(define plus +) (plus 7 2)")
        self.assertEqual(result, [None, Number(9)])

    def testCaseInsensitivityOfBoundVariables(self):
        result = run("(define FOO 42) FoO")
        self.assertEqual(result, [None, Number(42)])


if __name__ == '__main__':
    unittest.main()
