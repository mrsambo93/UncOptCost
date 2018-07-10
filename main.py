from unc_opt_cost import UncOptCost
from crowd import Crowd
from strategy import Strategy
import numpy
import json
import os

DATASET_JSON = "dataset.json"
TEST_PHASES = 5
TEST_PHASE_SIZE = 10
SELECTIVITY = 0.01
DATASET_SIZE = 100000
ERROR_RATE_YES = 0.4
ERROR_RATE_NO = 0.2
NUM_USERS = 14
K = 100
M = 3

if os.path.isfile(DATASET_JSON):
    with open(DATASET_JSON) as dataset_json:
        items = json.load(dataset_json)["0"]
else:
    items = numpy.zeros(DATASET_SIZE, dtype=int)
    items[:int(len(items) * SELECTIVITY)] = 1
    numpy.random.shuffle(items)
    numpy.random.shuffle(items)
    dataset = dict()
    dataset[0] = list(items)
    with open(DATASET_JSON, "w") as dataset_json:
        json.dump(dataset, dataset_json)
enumerated = dict()
for (index, item) in enumerate(items):
    enumerated[index] = item
test = dict()
for i in range(TEST_PHASES):
    its = numpy.zeros(TEST_PHASE_SIZE, dtype=int)
    its[:TEST_PHASE_SIZE/2] = 1
    numpy.random.shuffle(its)
    test[i] = its
crowd = Crowd(NUM_USERS, ERROR_RATE_YES, ERROR_RATE_NO, test)
avg_er_yes = crowd.avg_er_yes
avg_er_no = crowd.avg_er_no
strategy = Strategy(M, M)
unc_opt_cost = UncOptCost()

unc_opt_cost.unc_opt_cost(enumerated, K, SELECTIVITY, avg_er_yes, strategy, crowd)
