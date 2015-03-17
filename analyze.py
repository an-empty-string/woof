import copy
import wolftest
import re
import json

def text_from_game(game, user):
    return [i.split("\t")[2] for i in game if i.count("\t") == 2 and i.split("\t")[1] == "+%s" % user]

def convert(text):
    return re.sub('[,.\\?!:;\'"\\[\\]]', '', " ".join(text)).split()

def chisquare(a, b):
    a = copy.copy(a)
    b = copy.copy(b)
    for i in b.keys():
        if i not in a:
            a[i] = 0
    for i in a.keys():
        if i not in b:
            b[i] = 0

    total = 0
    for i in a.keys():
        total += (b[i] - a[i])**2

    return total

def currentusers():
    users = list(map(str.strip, wolftest.logs[max(wolftest.startlines)].split("\t")[2].split(":")[0].split(",")))
    logs = [i.split("\t")[2] for i in wolftest.logs[max(wolftest.startlines):] if i.split("\t")[1] == "--" and "Mode" in i.split("\t")[2]]
    return list(set(users) - set(sum([i.split("[")[1].split("]")[0].split()[1:] for i in logs], [])))

def dead():
    logs = [i.split("\t")[2] for i in wolftest.logs[max(wolftest.startlines):] if i.split("\t")[1] == "--" and "Mode" in i.split("\t")[2]]
    return list(set(sum([i.split("[")[1].split("]")[0].split()[1:] for i in logs], [])))

def analyze():
    data = json.loads(open("training_data.json").read())
    wolftest.update()
    game = wolftest.logs[max(wolftest.startlines):]
    allusers = currentusers()
    wolfiness = {}

    for user in allusers:
        otherdata = convert(text_from_game(game, user))
        probdict = wolftest.worddata_to_probdict(otherdata)

        confidences = {}
        if user not in data:
            data[user] = {}
        for role in data[user]:
            confidences[role] = chisquare(data[user][role], probdict) * len(otherdata)

        wolfiness[user] = sum([confidences[role] for role in wolftest.wolf_roles if role in confidences]) - (sum(confidences[role] for role in wolftest.village_roles if role in confidences))

    min_wolfiness = min(wolfiness.values())
    slope = 1 / (max(wolfiness.values()) - min_wolfiness)

    return sorted([(k[0], slope * (k[1] - min_wolfiness)) for k in wolfiness.items()], key=lambda k: -k[1])

if __name__ == '__main__':
    import pprint
    pprint.pprint(analyze())
