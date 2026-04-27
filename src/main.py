from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import RawValueProtocol
import json
import re
import heapq
import sys
from collections import defaultdict
from timeit import default_timer

TOKEN_RE = re.compile(r"[^a-zA-Z]+")
TOP_K = 75

class MRChiSqr(MRJob):
    OUTPUT_PROTOCOL = RawValueProtocol
    
    def configure_args(self):
        """ Leave the standard MRJOB parameter available and distribute the stopword file to each worker for filtering """
        super().configure_args()
        self.add_file_arg("--stopwords")

    def steps(self):
        """
        Defines the two-step MapReduce workflow for this job.
        Step 1:
            - mapper_init: load any needed data before mapping
            - mapper: process each input line and emit intermediate key/value pairs
            - mapper_final: finalize mapper output (e.g., flush buffers)
            - reducer_collect_counts: aggregate counts for each term/category
        Step 2:
            - reducer_compute_top_terms: take the aggregated counts from Step 1
              and compute the top-N terms (e.g., highest chi-square scores)
        """
        return [
            MRStep(
                mapper_init=self.mapper_init,
                mapper=self.mapper,
                mapper_final=self.mapper_final,
                reducer=self.reducer_collect_counts
            ),
            MRStep(
                reducer=self.reducer_compute_top_terms
            )
        ]
        
    def mapper_init(self):
        """
        MAPPER SETUP: runs once per worker at the start to open the stopwordlist and keep it in RAM for optimization 
            Initialize a dictionary to hold counts "In-Mapper Combining" logic
        """
        self.local_counts = defaultdict(int)
        with open(self.options.stopwords) as f:
            self.stopwords = set(w.strip() for w in f if w.strip())

    def mapper(self, _, line):
        """
        MAPPER WORK: 
            Preprocess: Strip lines, parse JSON with validation.
            Validation: Skip records missing a category or empty text.
            Tokenization: Apply case folding and split text into unique tokens (sets). 
        Output :
            - ((token, category), 1): For term-category frequency (Variable A). 
            - (("__DOCS__", category), 1): For total document counts per category.
        """
        line = line.strip()
        if not line:
            return

        try:
            doc = json.loads(line)
        except json.JSONDecodeError:
            return

        category = doc.get("category")
        text = doc.get("reviewText", "")

        if not category:
            return

        text = text.lower()
        
        # tokens are defined as sets so repeated tokens are counted as one
        tokens = {
            t for t in TOKEN_RE.split(text)
            if len(t) > 1 and t not in self.stopwords
        }

        # Term-document frequency per category using (token, category) as key
        # update the local dictionary
        for token in tokens:
            self.local_counts[(token, category)] += 1
        self.local_counts[("__DOCS__", category)] += 1
    
    def mapper_final(self):
        for (token, category), count in self.local_counts.items():
            yield (token, category), count

    """
    REDUCER WORK 1: Intermediate Aggregation
        Aggregates the '1s' from the Mapper into final counts for each key
        Transitions to a 'None' key to funnel all data into a single final reducer,
    output: tokens with tags and none as key
    """
    def reducer_collect_counts(self, key, values):
        token, category = key
        count = sum(values)

        if token == "__DOCS__":
            yield None, ["DOC", category, count]
        else:
            yield None, ["WORD", token, category, count]


    def reducer_compute_top_terms(self, _, records):
        """
        Final Reducer
        1. Reconstruct global state:
           - Rebuilds category document totals.
           - Rebuilds a nested dictionary word_counts[word][category] with term frequencies per category.
           - Computes the global document count N.
        2. Statistical analysis and feature selection:
           - Builds the contingency table (A, B, C, D) for each word/category pair.
           - Computes the Chi-square score measuring association with the category.
           - Uses a min-heap (heapq) to keep only the Top-K highest scoring terms for each category.
        3. Output:
           - One line per category:
             <category> word1:chi1 word2:chi2 ...
           - One final line:
             all unique selected words across categories, sorted alphabetically, no repetitions.
        """
        category_totals = {}
        word_counts = defaultdict(dict)
        
        for record in records:
            tag = record[0]

            if tag == "DOC":
                _, category, count = record
                category_totals[category] = count

            elif tag == "WORD":
                _, word, category, count = record
                word_counts[word][category] = count #nested dictionary
        
        N = sum(category_totals.values())

        top_k = defaultdict(list)

        # For every word/category pair, compute chi-square
        for word, cat_counts in word_counts.items():
            #number of doc containing token
            word_total = sum(cat_counts.values()) 
            #filtering criterion
            if word_total < 50: 
                continue
            #contingency table calculation
            for category, cat_total in category_totals.items():
                A = cat_counts.get(category, 0)
                B = word_total - A
                C = cat_total - A
                D = (N - cat_total) - B

                denominator = (A + C) * (B + D) * (A + B) * (C + D)
                chi = (N * (A * D - B * C) ** 2 / denominator) if denominator else 0.0
                
                item = (chi, word)
                # defaultdict(list) ensures it starts as an empty list.
                heap = top_k[category]

                if len(heap) < TOP_K:
                    heapq.heappush(heap, item)
                # heap[0] is the *smallest* chi-square in the current top-K 
                elif item > heap[0]:
                    heapq.heapreplace(heap, item)
        # set to output the final line
        merged_terms = set()
        # sorting and composition of category line output
        for category in sorted(top_k):
            # sorting in descending order 
            terms = sorted(top_k[category], key=lambda x: (-x[0], x[1])) 
            merged_terms.update(word for chi, word in terms)
            
            line = category + " " + " ".join(
                f"{word}:{chi}" for chi, word in terms
            )
            yield None, line
        #final output line
        yield None, " ".join(sorted(merged_terms))


if __name__ == "__main__":
    start = default_timer()
    MRChiSqr.run()
    end = default_timer()
    sys.stderr.write(f"Total runtime: {end - start:.2f} seconds\n")
