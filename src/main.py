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
        MAPPER SETUP: runs once per worker at the start open stopword and keeps in RAM for optimization 
            Initialize an associative array to hold counts "In-Mapper Combining" logic
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
        
        # tokens are defined as sets so double are counted as one
        tokens = {
            t for t in TOKEN_RE.split(text)
            if len(t) > 1 and t not in self.stopwords
        }

        # Term-document frequency per category using (token, category) as key
        # Using a set (tokens) ensures we measure Document Frequency, not Term Frequency.
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
    output: Word and Doc tokens with none as key, end of parrapelism
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
        Final Reducer: Global State Reconstruction
            iterate to reconstruct the global state in memory using 2 dictionaries category-level metadata and term-category frequencies
            Builds a nested dictionary structure word_counts[word][category]
            Computes the total population size N by summing the document counts across all categories.
        Statistical Analysis & Feature Selection
            Contingency Table Construction :computes the four quadrants of a contingency table A,B,C,D
            Chi-Square Metric: calculation of indipendence using the Chi-square statistic
            Top-K Selection: Utilizing the heapq library, the reducer maintains a Min-Heap of size 75 for each category
        output: one single, long line
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
                word_counts[word][category] = count

        N = sum(category_totals.values())

        top_k = defaultdict(list)

        # For every word/category pair, compute chi-square
        for word, cat_counts in word_counts.items():
            word_total = sum(cat_counts.values())

            for category, cat_total in category_totals.items():
                A = cat_counts.get(category, 0)
                B = word_total - A
                C = cat_total - A
                D = (N - cat_total) - B

                denominator = (A + C) * (B + D) * (A + B) * (C + D)
                chi = (N * (A * D - B * C) ** 2 / denominator) if denominator else 0.0

                item = (chi, word)
                heap = top_k[category]

                if len(heap) < TOP_K:
                    heapq.heappush(heap, item)
                elif item > heap[0]:
                    heapq.heapreplace(heap, item)

        merged_terms = set()

        for category in sorted(top_k):
            terms = sorted(top_k[category], key=lambda x: (-x[0], x[1]))
            merged_terms.update(word for chi, word in terms)

            line = category + " " + " ".join(
                f"{word}:{chi}" for chi, word in terms
            )
            yield None, line

        yield None, " ".join(sorted(merged_terms))


if __name__ == "__main__":
    start = default_timer()
    MRChiSqr.run()
    end = default_timer()
    sys.stderr.write(f"Total runtime: {end - start:.2f} seconds\n")
