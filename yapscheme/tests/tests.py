#!/usr/bin/env python
import unittest

from .. import Parser
from .. import Interpreter
from ..tokens import Bool, Cons, EmptyList, Identifier, Number, String


def parseOne(arg):
    return Parser.parse(arg)[0]

def run(arg):
    return Interpreter.Interpreter().run(Parser.parse(arg))

def runOne(arg):
    return Interpreter.Interpreter().evalOne(parseOne(arg))


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

    def testParseTrue(self):
        self.assertEqual(parseOne("#t"), Bool(True))

    def testParseFalse(self):
        self.assertEqual(parseOne("#f"), Bool(False))

    def testUnexpectedCharAfterHash(self):
        with self.assertRaises(Parser.BadHashError):
            parseOne("#q")

    def testEOFAfterHash(self):
        with self.assertRaises(Parser.UnexpectedEOFError):
            parseOne("#")


class TestBareInterpeter(unittest.TestCase):
    def testInteger(self):
        self.assertEqual(runOne("-1337"), Number(-1337))

    def testQuoteInteger(self):
        self.assertEqual(runOne("(quote 7)"), Number(7))

    def testRejectQuoteWithMultipleArguments(self):
        with self.assertRaises(Interpreter.TooManyArgumentsError):
            runOne("(quote 7 2)")

    def testRejectQuoteWithNoArguments(self):
        with self.assertRaises(Interpreter.NotEnoughArgumentsError):
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
        with self.assertRaises(Interpreter.NotCallableError):
            runOne("()")

    def testRejectNumberAsProcedure(self):
        with self.assertRaises(Interpreter.NotCallableError):
            runOne("(27)")

    def testRejectProcedureCallWithDot(self):
        with self.assertRaises(Interpreter.ImproperListCallError):
            runOne("(+ 1 . 2)")

    def testRejectUnknownIdentifier(self):
        with self.assertRaises(Interpreter.UnknownIdentifier):
            runOne("this-does-not-exist")

    def testRejectCallingUnknownIdentifier(self):
        with self.assertRaises(Interpreter.UnknownIdentifier):
            runOne("(this-does-not-exist)")

    def testDefine(self):
        result = run("(define the-answer 42) the-answer")
        self.assertEqual(result, [None, Number(42)])

    def testRejectDefineWithTooManyArguments(self):
        with self.assertRaises(Interpreter.TooManyArgumentsError):
            runOne("(define hello 2 3)")

    def testRejectDefineWithNoArguments(self):
        with self.assertRaises(Interpreter.NotEnoughArgumentsError):
            runOne("(define)")

    def testRejectDefineWithOneArgument(self):
        with self.assertRaises(Interpreter.NotEnoughArgumentsError):
            runOne("(define foo)")

    def testDefineRequiresAnIdentifierAsFirstArgument(self):
        with self.assertRaises(Interpreter.BadArgumentError):
            runOne("(define 7 2)")

    def testSubtraction(self):
        self.assertEqual(runOne("(- 2 7)"), Number(-5))

    def testRejectSubtrationWithNoOperands(self):
        with self.assertRaises(Interpreter.NotEnoughArgumentsError):
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

    def testIfTrue(self):
        self.assertEqual(runOne("(if #t 1 2)"), Number(1))

    def testIfFalse(self):
        self.assertEqual(runOne("(if #f 1 2)"), Number(2))

    def testRejectIfWithTooFewArguments(self):
        with self.assertRaises(Interpreter.NotEnoughArgumentsError):
            runOne("(if #t)")

    def testRejectIfWithTooManyArguments(self):
        with self.assertRaises(Interpreter.TooManyArgumentsError):
            runOne("(if #t 1 2 3)")

    def testIfWithNoFalseBranchAndYetItsFalse(self):
        self.assertEqual(runOne("(if #f 42)"), None)

    def testIfEvaluatesCondition(self):
        self.assertEqual(runOne("(if (if #t #f) 1 2)"), Number(2))

    def testIfEvaluatesFirstBranch(self):
        self.assertEqual(runOne("(if #t (+ 0 1) 2)"), Number(1))

    def testIfEvaluatesSecondBranch(self):
        self.assertEqual(runOne("(if #f 1 (+ 0 2))"), Number(2))

    # The real difference between Lisp and Scheme! ;)
    def testEmptyListIsTrue(self):
        self.assertEqual(runOne("(if (quote ()) 1 2)"), Number(1))


if __name__ == '__main__':
    unittest.main()
