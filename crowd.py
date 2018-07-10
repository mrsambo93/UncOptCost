from __future__ import division
from user import User
from spammer import Spammer
from numpy import random
from functools import reduce
import json
import os


class Crowd:

    _users_path = "users.json"

    def __init__(self, num_users, error_rate_max_yes, error_rate_max_no, test):
        self.num_users = num_users
        self.users = self.create_users(num_users, error_rate_max_yes, error_rate_max_no)
        self.avg_er_yes = 0.0
        self.avg_er_no = 0.0
        self.reliable_users = self.evaluate_users(test, self.users)

    def create_users(self, num_users, error_rate_max_yes, error_rate_max_no):
        users = list()
        spammer1 = Spammer("spammer1")
        spammer2 = Spammer("spammer2")
        hammer1 = User(0.0, 0.0, "hammer1")
        hammer2 = User(0.0, 0.0, "hammer2")
        users.append(spammer1)
        users.append(spammer2)
        users.append(hammer1)
        users.append(hammer2)
        if os.path.isfile(self._users_path):
            with open(self._users_path, "r") as users_file:
                users_dict = json.load(users_file)
                for user in users_dict:
                    error_rate_yes = users_dict[user]["error_rate_yes"]
                    print("error_rate_yes: %s" % error_rate_yes)
                    error_rate_no = users_dict[user]["error_rate_no"]
                    print("error_rate_no: %s" % error_rate_no)
                    us = User(error_rate_yes, error_rate_no, "user" + user)
                    users.append(us)
        else:
            i = 0
            users_dict = dict()
            for _ in range(num_users - len(users)):
                error_rate_yes = random.uniform(0.0, error_rate_max_yes)
                print("error_rate_yes: %s" % error_rate_yes)
                error_rate_no = random.uniform(0.0, error_rate_max_no)
                print("error_rate_no: %s" % error_rate_no)
                users_dict[i] = {
                    "error_rate_yes": error_rate_yes,
                    "error_rate_no": error_rate_no
                }
                user = User(error_rate_yes, error_rate_no, "user" + str(i))
                users.append(user)
                i += 1
            with open(self._users_path, "w") as users_file:
                json.dump(users_dict, users_file, indent=4, separators=(',', ': '))
        random.shuffle(users)
        return users

    def evaluate_users(self, test, users):
        answers = dict()
        for user in users:
            answers[user.name] = list()
            for i in test:
                for item in test[i]:
                    if user.answer(item):
                        answers[user.name].append((item, 1))
                    else:
                        answers[user.name].append((item, 0))
        errors_dict = dict()
        for user in answers:
            total_yes = 0
            total_no = 0
            total_yes_er = 0
            total_no_er = 0
            for (item, answer) in answers[user]:
                if item == 1:
                    total_yes += 1
                    if answer != item:
                        total_yes_er += 1
                if item == 0:
                    total_no += 1
                    if answer != item:
                        total_no_er += 1
            er_yes = total_yes_er/total_yes
            er_no = total_no_er/total_no
            errors_dict[user] = {
                "er_yes": er_yes,
                "er_no": er_no
            }
        total_er_yes = 0.0
        total_er_no = 0.0
        for user in errors_dict:
            total_er_yes += errors_dict[user]["er_yes"]
            total_er_no += errors_dict[user]["er_no"]
        self.avg_er_yes = total_er_yes/self.num_users
        self.avg_er_no = total_er_no/self.num_users
        print("avg_yes: %s" % self.avg_er_yes)
        print("avg_no: %s" % self.avg_er_no)

        reliable_users = list()
        for user in answers:
            cont = reduce(lambda x, y: (0, x[1] + y[1]), answers[user])
            if cont[1] != 0:
                print("user: %s" % user)
                if errors_dict[user]["er_yes"] <= self.avg_er_yes and errors_dict[user]["er_no"] <= self.avg_er_no:
                    us = next((x for x in users if x.name == user), None)
                    reliable_users.append(us)
        print("len(realiable): %d" % len(reliable_users))
        reliables = list()
        for user in reliable_users:
            reliables.append(user.name)
        print("reliables: %s" % reliables)
        return reliable_users

    def ask(self, cq, r, u):
        for item in cq:
            n1 = 0
            n2 = 0
            for _ in range(cq[item]):
                current_user = self.reliable_users.pop(0)
                if current_user.answer(u[item]):
                    n1 += 1
                    print(current_user.name + "\t1")
                else:
                    n2 += 1
                    print(current_user.name + "\t0")
                self.reliable_users.append(current_user)
            r[item]["n1"] += n1
            r[item]["n2"] += n2
