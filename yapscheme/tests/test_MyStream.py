#!/usr/bin/env python
from __future__ import division
import io
import unittest

from yapscheme.MyStream import MyStream, MyStreamEOF, MyStreamPutBackError

class TestMyStream(unittest.TestCase):
    def testReadOneChar(self):
        stream = MyStream(io.StringIO(u"Hello mom"))
        ch = stream.read_ch()
        self.assertEqual(ch, 'H')

    def testReadTwoChars(self):
        stream = MyStream(io.StringIO(u"Hello mom"))
        s = stream.read_ch()
        s += stream.read_ch()
        self.assertEqual(s, 'He')

    def testThrowEof(self):
        test_string = u"Hello mom"
        stream = MyStream(io.StringIO(test_string))
        with self.assertRaises(MyStreamEOF):
            for x in xrange(len(test_string)+1):
                stream.read_ch()

    def testReadEntireStream(self):
        test_string = u"Hello mom"
        stream = MyStream(io.StringIO(test_string))
        s = ''
        try:
            # The xrange is to ensure we can't loop infinitely
            for x in xrange(42):
                s += stream.read_ch()
        except MyStreamEOF:
            pass
        self.assertEqual(s, test_string)

    def testPutBack(self):
        stream = MyStream(io.StringIO(u"abcdef"))
        stream.read_ch()
        stream.put_back()
        ch = stream.read_ch()
        self.assertEqual(ch, "a")

    def testCannotPutBackIfNothingWasRead(self):
        stream = MyStream(io.StringIO(u"abcdef"))
        with self.assertRaises(MyStreamPutBackError):
            stream.put_back()

    def testCannotPutBackTwice(self):
        stream = MyStream(io.StringIO(u"abcdef"))
        stream.read_ch()
        stream.read_ch()
        stream.put_back()
        with self.assertRaises(MyStreamPutBackError):
            stream.put_back()

    def testClose(self):
        stream = MyStream(io.StringIO(u"abcdef"))
        stream.close()
        self.assert_(stream.stream.closed)


if __name__ == '__main__':
    unittest.main()
