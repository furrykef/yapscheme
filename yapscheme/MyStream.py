# A wrapper around Python streams
#
# Rationale:
#  * Cannot always seek backwards on a stream, which the parser needs
#  * I got tired of checking for EOF after every single read instead of
#    letting an exception handler take care of it. The idea here is,
#    if I forget to check for EOF, I want an exception to be thrown
#    immediately rather than introducing a subtle error in processing
#    or output.

# Note: NOT a MyStreamError since it's not intended to be an error
class EOF(EOFError):
    pass


class MyStreamError(Exception):
    pass

class PutBackError(MyStreamError):
    pass


class MyStream(object):
    def __init__(self, stream):
        self.stream = stream
        self.__put_back = None
        self.__last_char = None

    def read_ch(self):
        if self.__put_back is not None:
            ch = self.__put_back
            self.__put_back = None
            return ch
        else:
            ch = self.stream.read(1)
            self.__last_char = ch
            if ch == '':
                raise EOF("Reading after end of stream")
            return ch

    def put_back(self):
        if self.__last_char is None:
            raise PutBackError("No character to put back")
        self.__put_back = self.__last_char
        self.__last_char = None

    def close(self):
        self.stream.close()
