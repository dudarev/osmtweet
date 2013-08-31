# -*- coding: utf-8 -*-
import unittest

MAX_URL_LENGTH = 50
MAX_TWEET_LENGTH = 140

def remove_word(s):
    words = s.strip().split(' ')
    i_max = len(words)-1
    i = i_max
    has_dots = False
    while i>=0:
        if not words[i] == '...':
            if (not 'http:' in words[i]) or (len(words[i]) > MAX_URL_LENGTH) or (i<i_max):
                if has_dots:
                    del words[i]
                else:
                    words[i] = '...'
                break
        else:
            has_dots = True
        i -= 1
    return ' '.join(words)

def trim_to_tweet(s):
    if len(s) <= MAX_TWEET_LENGTH:
        return s
    while len(s) > MAX_TWEET_LENGTH:
        s = remove_word(s)
    return s

class TestSequenceFunctions(unittest.TestCase):

    def testRemoveWord(self):
        old = 'one two three'
        new = 'one two ...'
        self.assertEqual(remove_word(old),new)
        old = 'one two three ...'
        new = 'one two ...'
        self.assertEqual(remove_word(old),new)
        old = 'one two three ... http://example.com/?text=test'
        new = 'one two ... http://example.com/?text=test'
        self.assertEqual(remove_word(old),new)

    def testTrimToTweet(self):
        old = 'less then MAX_TWEET_LENGTH'
        new = old
        self.assertEqual(trim_to_tweet(old), new)
        old = 'Tiger Woods Voicemail Slow Jam Remix Tiger Woods Voicemail Slow Jam Remix Tiger Woods Voicemail Slow Jam Remix Tiger Woods Voicemail Slow Jam Remix http://toptuby.appspot.com/?v=OEkomaBTppY'
        new = 'Tiger Woods Voicemail Slow Jam Remix Tiger Woods Voicemail Slow Jam Remix Tiger Woods ... http://toptuby.appspot.com/?v=OEkomaBTppY'
        self.assertEqual(trim_to_tweet(old), new)

    def testTrimUnicode(self):
        old = u"""Исправил границы военкомата и landuse=residental чтобы они не пересекались. 
        TODO: надо организовать их через отношения, чтобы была граничная линия, и чтобы не будлировалась информация. 
        http://www.openstreetmap.org/browse/changeset/15210559
        """
        new = trim_to_tweet(old)
        self.assertTrue(len(new) <= MAX_TWEET_LENGTH)

    def testTrimVeryLongURL(self):
        old = "http://example.com/A_VERY_LONG_URL" + 200*'a'
        new = trim_to_tweet(old)
        self.assertTrue(len(new) <= MAX_TWEET_LENGTH)

    def testSeveralShortURLs(self):
        old = 20 * "http://example.com/A_SHORT_URL "
        new = trim_to_tweet(old)
        print new
        self.assertTrue(len(new) <= MAX_TWEET_LENGTH)


if __name__ == '__main__':
    unittest.main()
