#!/usr/bin/env bash

# Set to 1 for the full set / 0 for the dev set
use_full_set=1

if [ "$use_full_set" -eq 1 ]; then
    python main.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.6.jar -r hadoop hdfs:///dic_shared/amazon-reviews/full/reviewscombined.json --stopwords stopwords.txt > output_cluster.txt
else
    python main.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.6.jar -r hadoop hdfs:///dic_shared/amazon-reviews/full/reviews_devset.json --stopwords stopwords.txt > output_dev.txt
fi