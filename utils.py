import re
import sys
    
def tokenize(text, stopwords):
    TOKEN_RE = re.compile(r"[^a-zA-Z<>^|]+")
    text = text.lower()
    parts = TOKEN_RE.split(text)
    
    tokens = [token for token in parts if token and len(token) > 1 and token not in stopwords]
    return tokens

if __name__ == "__main__":
    # First arguement is always the .json file
    sentence = sys.argv[1]
    with open(sentence, "r") as file:
        text = file.read()
    
    # Second arguement is always the stopwords.txt
    # We store stopwords in a Python set because sets use hash‑based lookup
    # which is extremely fast, and because they guarantee exact word matching.    
    stopwords = sys.argv[2]
    with open(stopwords, "r") as file:
        stoptext = set(w.strip().lower() for w in file)
    
    tokens = tokenize(text, stoptext)
    print(tokens[:5])
    