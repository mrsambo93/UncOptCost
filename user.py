from numpy import random


class User:

    def __init__(self, error_rate_yes, error_rate_no, name):
        self.error_rate_yes = error_rate_yes
        self.error_rate_no = error_rate_no
        self.name = name

    def answer(self, item):
        answer = random.random_sample()
        if item == 1:
            return answer <= (1 - self.error_rate_yes)
        if item == 0:
            return answer <= self.error_rate_no
