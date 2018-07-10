from __future__ import division


class UncOptCost:
    M = 10

    def __init__(self):
        pass

    def unc_opt_cost(self, items, k, selectivity, error_rate, strategy, crowd):
        l = dict()
        discarded = dict()
        u = dict(items)
        y = self.compute_y(selectivity, error_rate, strategy)
        phase = 0
        num_questions = 0
        print("y: %s" % y.items())
        r = {}
        for item in items:
            r[item] = {
                "n1": 0,
                "n2": 0
            }
        while len(l) < k and len(u) > 0:
            i1 = self.choose_elems_with_lowest_y(y, r, u, k - len(l))
            cq = {}
            for item in i1:
                n1 = self.get_number_positive_questions(item, strategy, r)
                n2 = self.get_number_negative_questions(item, strategy, r)
                cq[item] = min(n1, n2)
                num_questions += cq[item]
                # print("cq: " + str(item) + "\t" + str(cq[item]))

            crowd.ask(cq, r, u)
            phase += 1
            for i in cq:
                if strategy.check(r[i]["n1"], r[i]["n2"]) == 1:
                    l[i] = u.pop(i)
                    print("l: %s" % l)
                elif strategy.check(r[i]["n1"], r[i]["n2"]) == 0:
                    discarded[i] = u.pop(i)
                    # print("discarded: %s" % discarded)
        print("phases: %d" % phase)
        print("num_questions: %d" % num_questions)
        discarded_ones = self.count_discarded_ones(discarded)
        print("discarded_ones: %d" % discarded_ones)
        precision = self.eval_precision(l)
        print("precision: %f" % precision)

    def identify_items(self, items):
        item_dict = {}
        for (index, elem) in enumerate(items):
            item_dict[index] = elem
        return item_dict

    def compute_y(self, selectivity, error_rate, strategy):
        y = {}
        found = False
        a = 0
        while not found:
            self.recursive_search(selectivity, error_rate, strategy, a, 1, 0, y)
            self.recursive_search(selectivity, error_rate, strategy, a, 0, 1, y)
            y[(0, 0)] = int(round(self.p1(0, 0, selectivity, error_rate) * y[(1, 0)] +
                                  self.p0(0, 0, selectivity, error_rate) * y[(0, 1)] + 1))
            if a < int(round(y[(0, 0)])):
                a += 1
            elif a > int(round(y[(0, 0)])):
                a -= 1
            else:
                found = True
            print("a: %s" % a)
        return y

    def recursive_search(self, selectivity, error_rate, strategy, a, n1, n2, y):
        if strategy.check(n1, n2) == 1:
            y[(n1, n2)] = 0
            return 0
        if strategy.check(n1, n2) == 0:
            y[(n1, n2)] = a
            return a
        second = self.p1(n1, n2, selectivity, error_rate) * \
                 self.recursive_search(selectivity, error_rate, strategy, a, n1 + 1, n2, y) + \
                 self.p0(n1, n2, selectivity, error_rate) * \
                 self.recursive_search(selectivity, error_rate, strategy, a, n1, n2 + 1, y) + 1
        y[(n1, n2)] = int(round(min(a, second)))
        return y[(n1, n2)]

    def choose_elems_with_lowest_y(self, y, r, u, n):
        items = list(u.keys())
        items.sort(key=lambda x: y[(r[x]["n1"], r[x]["n2"])])
        res = items[:n]
        return res

    def get_number_positive_questions(self, item, strategy, r):
        actual_n1 = r[item]["n1"]
        new_n1 = strategy.data["n1"] - actual_n1
        return new_n1

    def get_number_negative_questions(self, item, strategy, r):
        actual_n2 = r[item]["n2"]
        new_n2 = strategy.data["n2"] - actual_n2
        return new_n2

    def p0(self, n1, n2, selectivity, error_rate):
        num_1 = self.reverse_probability_positive(n1, n2, error_rate) * selectivity
        num_2 = self.reverse_probability_negative(n1, n2, error_rate) * (1 - selectivity)
        den = num_1 + num_2
        return (num_1 / den) * error_rate + (num_2 / den) * (1 - error_rate)

    def p1(self, n1, n2, selectivity, error_rate):
        num_1 = self.reverse_probability_positive(n1, n2, error_rate) * selectivity
        num_2 = self.reverse_probability_negative(n1, n2, error_rate) * (1 - selectivity)
        den = num_1 + num_2
        return (num_1 / den) * (1 - error_rate) + (num_2 / den) * error_rate

    def reverse_probability_positive(self, n1, n2, error_rate):
        return (1 - error_rate)**n1 * error_rate**n2

    def reverse_probability_negative(self, n1, n2, error_rate):
        return error_rate**n1 * (1 - error_rate)**n2

    def eval_precision(self, l):
        ones = 0.0
        for el in l:
            if l[el] == 1:
                ones += 1
        return 0.0 if len(l) == 0 else ones/len(l)

    def count_discarded_ones(self, discarded):
        ones = 0
        for el in discarded:
            if discarded[el] == 1:
                ones += 1
        return ones
