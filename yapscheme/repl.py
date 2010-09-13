from __future__ import division
import os
import sys
from yapscheme import Parser, Environment


def main():
    env = Environment.Environment()
    while True:
        try:
            input = raw_input("yap> ").strip()
        except EOFError:
            return

        try:
            for result in env.run(Parser.parse(input)):
                if result is not None:
                    print result
        except Parser.ParseError as e:
            print >> sys.stderr, "PARSE ERROR:", e
        except Environment.EnvironmentError as e:
            suppress_error = False
            if isinstance(e, Environment.UnknownIdentifier):
                if handleUnknownIdentifier(input):
                    suppress_error = True

            if not suppress_error:
                print >> sys.stderr, "RUNTIME ERROR:", e

        print


def handleUnknownIdentifier(input):
    input = input.lower()

    # Easter eggs and such go here
    if input in ('help', 'exit', 'quit'):
        # This ugly hack taken from Python's site.py
        if os.sep == ':':
            eof = 'Cmd-Q'
        elif os.sep == '\\':
            eof = 'Ctrl-Z plus Return'
        else:
            eof = 'Ctrl-D (i.e. EOF)'
        print "Press", eof, "to exit."
        return True
    elif input == 'xyzzy':
        print "Nothing happens."
        return True
    elif input == 'get ye flask':
        print "You can't get ye flask."
        return True

    return False


if __name__ == '__main__':
    main()
