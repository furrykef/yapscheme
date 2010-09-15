import io
import re

from . import MyStream
from . import tokens


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
_MATCH_IDENTIFIER = re.compile("^[A-Za-z!$%&*/:<=>?@^_~]([-+.0-9A-Za-z!$%&*/:<=>?@^_~]*)$")

class Parser(object):
    def loadFromString(self, code):
        self.__file = MyStream.MyStream(io.StringIO(code))

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
            try:
                ch = self.__file.read_ch()
                if ch == ';':
                    # Comment; skip to end of line
                    while ch != '\n':
                        ch = self.__file.read_ch()
                elif not ch.isspace():
                    # Not whitespace
                    break
            except MyStream.EOF:
                # We hit the end of the file
                raise NothingToParse

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
            # Put back last char so __read_atom can see it
            self.__file.put_back()
            atom = self.__read_atom()
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
        try:
            # We're starting from the character after the opening quote-mark
            the_string = io.StringIO()
            while True:
                ch = self.__file.read_ch()
                if ch == '\\':
                    # This is an escape sequence
                    ch = self.__file.read_ch()
                    if ch in ('\\', '"'):
                        the_string.write(ch)
                    else:
                        raise EscapeError("String has unknown escape sequence: \\%c" % ch)
                elif ch == '"':
                    # String terminated
                    return the_string.getvalue()
                else:
                    # Just an ordinary char in the string
                    the_string.write(ch)
        except MyStream.EOF:
            raise UnterminatedError("Unterminated string literal")

    def __read_sexpr(self):
        # We're starting from the character after the opening paren
        root_cons = tokens.Cons(None, None)     # Root is a dummy that we'll throw away
        last_cons = root_cons
        first = True
        try:
            while True:
                expr = self.parseNextExpression(allow_dot_operator=True, allow_close_paren=True)
                if expr is tokens.CloseParen:
                    if first:
                        return tokens.EmptyList()
                    else:
                        return root_cons.cdr
                elif expr is tokens.DotOperator:
                    if first:
                        # Dot operator not allowed at start of S-expression!
                        raise BadDotPairError
                    last_cons.cdr = self.parseNextExpression()
                    if self.parseNextExpression(allow_close_paren=True) is not tokens.CloseParen:
                        raise BadDotPairError
                    return root_cons.cdr
                else:
                    new_cons = tokens.Cons(expr, tokens.EmptyList())
                    last_cons.cdr = new_cons
                    last_cons = new_cons
                first = False
        except NothingToParse:
            raise UnterminatedError("Unterminated S-expression")


    def __read_atom(self):
        # @TODO@ - StringIO, or is that overkill here? Try profiling...
        atom = ''
        try:
            while True:
                ch = self.__file.read_ch()
                if _MATCH_ATOM_CHAR.match(ch):
                    atom += ch
                else:
                    # End of atom
                    # Put last char back since it isn't part of atom
                    self.__file.put_back()
                    return atom
        except MyStream.EOF:
            return atom


def parse(what):
    parser = Parser()
    parser.loadFromString(what)
    return parser.parse()
