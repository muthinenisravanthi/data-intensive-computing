import utils as u

from timeit import default_timer
import json

from mrjob.job import MRJob

class MRChiSqr(MRJob):
    def configure_args(self):
        super(MRChiSqr, self).configure_args()
        
        self.add_file_arg("--stopwords", help="Path to stopwords.txt")
    
    def mapper_init(self):
        with open(self.options.stopwords, "r") as file:
            self.stopwords = set(line.strip() for line in file)
        
    def mapper(self, _, line):
        review_dictionary = json.loads(line)
        review = review_dictionary["reviewText"]
        category = review_dictionary["category"]
        
        tokens = u.tokenize(review, self.stopwords)
        for token in tokens:
            yield (token, category), 1
        
    def reducer(self, key, values):
        yield key, sum(values)
        
        
if __name__ == "__main__":
    timer_start = default_timer()
    MRChiSqr.run()
    timer_end = default_timer()
    
    print(f"Total runtime: {timer_end - timer_start:.2f} seconds")