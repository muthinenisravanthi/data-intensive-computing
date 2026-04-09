import re
import sys

def read_stopwords(path):
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}
    
def tokenize(text, stopwords):
    TOKEN_RE = re.compile(r"""[\s\d\(\)\[\]\{\}\.\!\?,;:\+=_"'`~#@&\*%€$§\\/]+""")
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
    stopwords = sys.argv[2]
    with open(stopwords, "r") as file:
        stoptext = file.read()
    
    tokens = tokenize(text, stoptext)
    print(tokens[:5])
    