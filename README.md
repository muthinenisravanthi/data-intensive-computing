Data Intensive Computing Exercise 1

## To make changes

1. Clone the repository with

git clone "insert ssh or https address"

2. Make changes, then add and commit with

git add <insert filepath>

git commit -m "your commit message"

git push

## To run the program 

To run the program you need to point to the paths where you downloaded the reviews_devset json and the stopwords.txt. 

python3 preprocessing.py <path/to/review/file> <paht/to/stopwords>

Example

python3 preprocessing.py Assignment_1_Assets/reviews_devset.json Assignment_1_Assets/stopwords.txt

