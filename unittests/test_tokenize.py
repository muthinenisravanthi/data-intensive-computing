import unittest
# from utils import tokenize

class TestTokenization(unittest.TestCase):
    
    def test_lowercase_split(self):
        stopwords = set()
        text = "HELLO WoRlD \tTab"
        self.assertEqual(tokenize(text, stopwords), ["hello", "world", "tab"])
        
    def test_digits(self):
        stopwords = set()
        text = "abc123def21"
        self.assertEqual(tokenize(text, stopwords), ["abc", "def"])
        
    def test_delimiters(self):
        stopwords = set()
        text = "a(b)c[d]e{f}.g!h?i,j;k:l+m=n_o\"p'q`r~s#t@u&v*w%x€y$z§k/l\\m"
        self.assertEqual(tokenize(text, stopwords), [])

    def test_stopwords(self):
        stopwords = ["The", "quick", "lazy"]
        text = "The quick brown fox jumps over the lazy dog"
        self.assertEqual(tokenize(text,stopwords),
                        ["the", "brown", "fox", "jumps", "over", "the", "dog"])
        
    def test_single_chars(self):
        stopwords = set()
        text = "a b do c d e $ f ge"
        self.assertEqual(tokenize(text, stopwords), ["do", "ge"])
        
        
if __name__ == '__main__':
    unittest.main()