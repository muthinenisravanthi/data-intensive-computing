# Data-Intensive Computing Project

This project was developed as part of a university team assignment.

**Contributors:**  
Sravanthi Muthineni
dylan
bakogiannis
Roberto
-
- ## Requirements

- **Python** 3.12
- Dependencies listed in `requirements.txt`

Install dependencies with:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
## Run the code
- Make sure a folder that contains the development datasets exists, called data
- Example test run:
```bash
python src/main.py data/reviews_devset.json --stopwords data/stopwords.txt
```


## Unit Testing

Make sure your code works before pushing

Example of individual tests
```bash
python -m unittest unittests.test_tokenize
```
