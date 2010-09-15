#!/usr/bin/env python
import io
import unittest

from .. import MyStream

class TestMyStream(unittest.TestCase):
    def setUp(self):
        self.test_string = "abcdef"
        self.stream = MyStream.MyStream(io.StringIO(self.test_string))

    def testReadOneChar(self):
        ch = self.stream.read_ch()
        self.assertEqual(ch, 'a')

    def testReadTwoChars(self):
        s = self.stream.read_ch()
        s += self.stream.read_ch()
        self.assertEqual(s, 'ab')

    def testThrowEof(self):
        for x in range(len(self.test_string)):
              self.stream.read_ch()
        with self.assertRaises(MyStream.EOF):
            self.stream.read_ch()

    def testReadEntireStream(self):
        s = ''
        try:
            # The range is to ensure we can't loop indefinitely
            for x in range(42):
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
