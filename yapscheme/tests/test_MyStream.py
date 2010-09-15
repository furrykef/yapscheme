#!/usr/bin/env python
from __future__ import division
import io
import unittest

from yapscheme import MyStream

class TestMyStream(unittest.TestCase):
    def setUp(self):
        self.test_string = u"abcdef"
        self.stream = MyStream.MyStream(io.StringIO(self.test_string))

    def testReadOneChar(self):
        ch = self.stream.read_ch()
        self.assertEqual(ch, 'a')

    def testReadTwoChars(self):
        s = self.stream.read_ch()
        s += self.stream.read_ch()
        self.assertEqual(s, 'ab')

    def testThrowEof(self):
        with self.assertRaises(MyStream.EOF):
            for x in xrange(len(self.test_string)+1):
                self.stream.read_ch()

    def testReadEntireStream(self):
        s = ''
        try:
            # The xrange is to ensure we can't loop infinitely
            for x in xrange(42):
                s += self.stream.read_ch()
        except MyStream.EOF:
            pass
        self.assertEqual(s, self.test_string)

    def testPutBack(self):
        self.stream.read_ch()
        self.stream.put_back()
        ch = self.stream.read_ch()
        self.assertEqual(ch, 'a')

    def testCannotPutBackIfNothingWasRead(self):
        with self.assertRaises(MyStream.PutBackError):
            self.stream.put_back()

    def testCannotPutBackTwice(self):
        self.stream.read_ch()
        self.stream.read_ch()
        self.stream.put_back()
        with self.assertRaises(MyStream.PutBackError):
            self.stream.put_back()

    def testClose(self):
        self.stream.close()
        self.assert_(self.stream.stream.closed)


if __name__ == '__main__':
    unittest.main()
