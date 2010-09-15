#!/usr/bin/env python
import os
import sys
from . import Parser, Environment


def main():
    env = Environment.Environment()
    while True:
        try:
            input_str = input("yap> ").strip()
        except EOFError:
            return

        try:
            for result in env.run(Parser.parse(input_str)):
                if result is not None:
                    print(result)
        except Parser.ParseError as e:
            print("PARSE ERROR:", e, file=sys.stderr)
        except Environment.EnvironmentError as e:
            suppress_error = False
            if isinstance(e, Environment.UnknownIdentifier):
                if handleUnknownIdentifier(input_str):
                    suppress_error = True

            if not suppress_error:
                print("RUNTIME ERROR:", e, file=sys.stderr)

        print()


def handleUnknownIdentifier(input_str):
    input_str = input_str.lower()

    # Easter eggs and such go here
    if input_str in ('help', 'exit', 'quit'):
        # This ugly hack taken from Python's site.py
        if os.sep == ':':
            eof = 'Cmd-Q'
        elif os.sep == '\\':
            eof = 'Ctrl-Z plus Return'
        else:
            eof = 'Ctrl-D (i.e. EOF)'
        print("Press", eof, "to exit.")
        return True
    elif input_str == 'xyzzy':
        print("Nothing happens.")
        return True
    elif input_str == 'get ye flask':
        print("You can't get ye flask.")
        return True

    return False


if __name__ == '__main__':
    main()
