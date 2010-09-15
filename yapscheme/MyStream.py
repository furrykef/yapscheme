# A wrapper around Python streams
#
# Rationale:
#  * Cannot always seek backwards on a stream, which the parser needs
#  * I got tired of checking for EOF after every single read instead of
#    letting an exception handler take care of it

# Note: NOT a MyStreamError since it's not intended to be an error
class MyStreamEOF(EOFError):
    pass


class MyStreamError(Exception):
    pass

class MyStreamPutBackError(MyStreamError):
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
                raise MyStreamEOF("Reading after end of stream")
            return ch

    def put_back(self):
        if self.__last_char is None:
            raise MyStreamPutBackError("No character to put back")
        self.__put_back = self.__last_char
        self.__last_char = None

    def close(self):
        self.stream.close()
