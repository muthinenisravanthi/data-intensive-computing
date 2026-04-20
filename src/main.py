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
        super().configure_args()
        self.add_file_arg("--stopwords")

    def steps(self):
        return [
            MRStep(
                mapper_init=self.mapper_init,
                mapper=self.mapper,
                reducer=self.reducer_collect_counts
            ),
            MRStep(
                reducer=self.reducer_compute_top_terms
            )
        ]
        
    def mapper_init(self):
        with open(self.options.stopwords) as f:
            self.stopwords = set(w.strip() for w in f if w.strip())

    def mapper(self, _, line):
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

        tokens = {
            t for t in TOKEN_RE.split(text)
            if len(t) > 1 and t not in self.stopwords
        }

        # term-document frequency per category
        for token in tokens:
            yield (token, category), 1

        # total document count per category
        yield ("__DOCS__", category), 1


    def reducer_collect_counts(self, key, values):
        token, category = key
        count = sum(values)

        if token == "__DOCS__":
            yield None, ["DOC", category, count]
        else:
            yield None, ["WORD", token, category, count]


    def reducer_compute_top_terms(self, _, records):
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