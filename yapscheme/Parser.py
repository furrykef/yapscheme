from __future__ import division
from cStringIO import StringIO
import re
import os

from yapscheme import tokens


class ParseError(Exception):
    pass

class NothingToParse(ParseError):
    pass

class SyntaxError(ParseError):
    pass

class BadTokenError(SyntaxError):
    def __init__(self, token):
        # @TODO@ - make sure the exception text is never too long
        super(BadTokenError, self).__init__("Bad token: {0}".format(token))

class UnterminatedError(SyntaxError):
    pass

class EscapeError(SyntaxError):
    pass

class BadDotPairError(SyntaxError):
    pass


# @TODO@ - verify that the regexps are correct
# @TODO@ - test cases for regexps (especially atoms/identifiers)
_MATCH_ATOM_CHAR = re.compile("^[-A-Za-z0-9!$%&*+./:<=>?@^_~]$")
_MATCH_INTEGER_LITERAL = re.compile(r"^(\+|-)?\d+$")
_MATCH_IDENTIFIER = re.compile("^[A-Za-z!$%&*/:<=>?@^_~]([-+.0-9A-Za-z!$%&*/:<=>?@^_~]+)$")

class Parser(object):
    def loadFromString(self, code):
        self.__file = StringIO(code)

    def parse(self):
        # @XXX@ - what if self.__file is None or not defined?
        expressions = []
        try:
            while True:
                expressions.append(self.parseNextExpression())
        except NothingToParse:
            # This just means we hit the end
            pass
        finally:
            self.__file.close()

        return expressions


    def parseNextExpression(self, allow_dot_operator=False, allow_close_paren=False):
        # Eat any whitespace and comments
        while True:
            ch = self.__file.read(1)
            if ch == '':
                # We hit the end of the file
                raise NothingToParse
            elif ch == ';':
                # Comment; skip to end of line
                while ch not in ('', '\n'):
                    ch = self.__file.read(1)
            elif not ch.isspace():
                # Not whitespace
                break

        if ch == '"':
            return tokens.String(self.__read_string())
        elif ch == '(':
            return self.__read_sexpr()
        elif ch == ')':
            if allow_close_paren:
                # @TODO@ - parsing CloseParen as a token seems hacky
                return tokens.CloseParen
            else:
                # Not expecting a ')' in this context
                raise BadTokenError(ch)
        elif _MATCH_ATOM_CHAR.match(ch):
            # Assume an atom
            atom = self.__read_rest_of_atom(ch)
            if atom == '.':
                if allow_dot_operator:
                    # @TODO@ - parsing DotOperator as a token seems hacky
                    return tokens.DotOperator
                else:
                    # Dot operator not allowed in this context
                    raise BadTokenError(atom)
            elif _MATCH_INTEGER_LITERAL.match(atom):
                return tokens.Number(int(atom))
            elif _MATCH_IDENTIFIER.match(atom):
                return tokens.Identifier(atom)
            elif atom in ('+', '-'):
                # Special-cased since _MATCH_IDENTIFIER won't match these
                return tokens.Identifier(atom)
            else:
                raise BadTokenError(atom)
        else:
            raise BadTokenError(ch)

        # Can't get here
        # @TODO@ - use something other than assert?
        assert False


    def __read_string(self):
        # We're starting from the character after the opening quote-mark
        the_string = StringIO()
        while True:
            ch = self.__file.read(1)
            if ch == '':
                # We hit EOF before the string was terminated!
                raise UnterminatedError("Unterminated string literal")
            if ch == '\\':
                # This is an escape sequence
                ch = self.__file.read(1)
                if ch == '':
                    # @TODO@ - all these EOF checks are bothersome!
                    raise UnterminatedError("Unterminated string literal")
                elif ch in ('\\', '"'):
                    the_string.write(ch)
                else:
                    raise EscapeError("String has unknown escape sequence: \\%c" % ch)
            elif ch == '"':
                # String terminated
                return the_string.getvalue()
            else:
                # Just an ordinary char in the string
                the_string.write(ch)


    def __read_sexpr(self):
        # We're starting from the character after the opening paren
        root_cons = tokens.Cons(None, None)     # Root is a dummy that we'll throw away
        last_cons = root_cons
        first = True
        try:
            while True:
                expr = self.parseNextExpression(allow_dot_operator=True, allow_close_paren=True)
                if expr is tokens.CloseParen:
                    return root_cons.cdr
                elif expr is tokens.DotOperator:
                    if first:
                        # Dot operator not allowed at start of S-expression!
                        raise BadDotPairError()
                    last_cons.cdr = self.parseNextExpression()
                    if self.parseNextExpression(allow_close_paren=True) is not tokens.CloseParen:
                        raise BadDotPairError()
                    return root_cons.cdr
                else:
                    new_cons = tokens.Cons(expr, tokens.NullCons())
                    last_cons.cdr = new_cons
                    last_cons = new_cons
                first = False
        except NothingToParse:
            raise UnterminatedError("Unterminated S-expression")


    def __read_rest_of_atom(self, first_chr):
        # @TODO@ - StringIO, or is that overkill here? Try profiling...
        atom = first_chr
        while True:
            ch = self.__file.read(1)
            if _MATCH_ATOM_CHAR.match(ch):
                atom += ch
            else:
                # End of atom
                if ch != '':
                    # Put back the char we read since it may belong to next token
                    # @TODO@ - how to avoid seeking here?
                    self.__file.seek(-1, os.SEEK_CUR)
                return atom


def parse(what):
    parser = Parser()
    parser.loadFromString(what)
    return parser.parse()
