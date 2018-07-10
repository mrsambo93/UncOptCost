
class Strategy:

    data = {}

    def __init__(self, n1, n2):
        self.data = {
            "n1": n1,
            "n2": n2
        }

    def check(self, n1, n2):
        if n1 >= self.data["n1"] and n2 < self.data["n2"]:
            return 1
        if n2 >= self.data["n2"] and n1 < self.data["n1"]:
            return 0
        return -1
