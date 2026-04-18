import re

def tokenize(text, stopwords):
    TOKEN_RE = re.compile(r"[^a-zA-Z<>^|]+")
    text = text.lower()
    parts = TOKEN_RE.split(text)
    
    tokens = [token for token in parts if token and len(token) > 1 and token not in stopwords]
    return tokens
