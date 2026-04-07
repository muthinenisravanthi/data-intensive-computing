#tokenization
import re
import sys 

def tokenization(Reviews):
    tokens = re.split(r'[ \s\t\d\(\)\[\]\{\}\.\!\?\,\;\+\=\-\_\"\'\~\#\@\&\*\%\€\$\ß\\\/ ]', Reviews)
    return [t for t in tokens if t]


def main():
    sentence = sys.argv[1]
    with open(sentence, "r") as file:
        text = file.read()

    
    result = tokenization(text)
    print(result)
    print("Test World")


main()