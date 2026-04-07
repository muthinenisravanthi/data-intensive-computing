import re
import sys 

def tokenization(Reviews):
    tokens = re.split(r'[ \s\t\d\(\)\[\]\{\}\.\!\?\,\;\+\=\-\_\"\'\~\#\@\&\*\%\€\$\ß\\\/ ]', Reviews) #Define the given list of tokens
    return [t.lower() for t in tokens if len(t)>1] #added lower() for casefolding, added len(t)>1 to filter out tokens of 1 letter

def stopwords(Reviews, stopwordslist):
    return [t for t in Reviews if t not in stopwordslist]

def main():
    sentence = sys.argv[1]  #Take first argument in the command line
    with open(sentence, "r") as file:
        text = file.read()    

    result = tokenization(text)  #run the file content through the tokenization function

    stoplist = sys.argv[2]          #Take the second argument in the command line
    with open(stoplist, "r") as file:
        stoptext = file.read()
        #stoptext = stoptext.split()                     #Split in individual words
   
    filtered_results = stopwords(result, stoptext)
    print(filtered_results)

main()