import os
from pyspark import SparkConf, SparkContext

BASE_DIR = os.path.join(os.getcwd().split('python')[0], 'data')
DATA_FILE = os.path.join(BASE_DIR, 'fakefriends.csv')
import collections

conf = SparkConf().setMaster("local").setAppName("RatingsHistogram")
sc = SparkContext(conf = conf)

lines = sc.textFile("= sc.textFile(DATA_FILE)ml-100k/u.data")
ratings = lines.map(lambda x: x.split()[2])
result = ratings.countByValue()

sortedResults = collections.OrderedDict(sorted(result.items()))
for key, value in sortedResults.items():
    print("%s %i" % (key, value))
