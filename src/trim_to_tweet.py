# -*- coding: utf-8 -*-
import unittest

def remove_word(s):
    words = s.split(' ')
    i = len(words)-1
    has_dots = False
    while i>0:
        if not words[i] == '...':
            if not 'http:' in words[i]:
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
    if len(s) <= 140:
        return s
    while len(s) > 140:
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
        old = 'less then 140'
        new = old
        self.assertEqual(trim_to_tweet(old), new)
        old = 'Tiger Woods Voicemail Slow Jam Remix Tiger Woods Voicemail Slow Jam Remix Tiger Woods Voicemail Slow Jam Remix Tiger Woods Voicemail Slow Jam Remix http://toptuby.appspot.com/?v=OEkomaBTppY'
        new = 'Tiger Woods Voicemail Slow Jam Remix Tiger Woods Voicemail Slow Jam Remix Tiger Woods ... http://toptuby.appspot.com/?v=OEkomaBTppY'
        self.assertEqual(trim_to_tweet(old), new)

if __name__ == '__main__':
    unittest.main()
