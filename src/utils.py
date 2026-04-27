import re

def tokenize(text, stopwords):                                                                      
    parts = text.lower()                                                                            #Case folding
    result = re.split(r'[ \s\t\d\(\)\[\]\{\}\.\!\?\,\;\+\=\-\_\"\'\~\#\@\&\*\%\€\$\ß\\\/ ]', parts) #Define the given list of tokens
    
    tokens = [token for token in result if token and len(token) > 1 and token not in stopwords]    #To filter out the stopwords and all the 1 character tokens
    return tokens                                                                                   #Returns the filtered, tokenized list


    
