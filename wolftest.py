import re
LOGFILE = "/home/fwilson/.weechat/logs/irc.freenode.##werewolf.weechatlog"

def is_lykos(s):
    return s.split("\t")[1] == "@lykos"

global logs, startlines, endlines
logs = list(map(str.strip, open(LOGFILE).readlines()))
startlines = [index for index, value in enumerate(logs) if "Welcome to Werewolf, the popular detective" in value and is_lykos(value)]
endlines = [index for index, value in enumerate(logs) if "Game lasted" in value and is_lykos(value)]

wolf_roles = ["wolf", "werecrow", "wolf cub", "alpha wolf", "cultist", "minion", "traitor", "hag", "sorcerer"]
neutral_roles = ["lycan", "clone", "crazed shaman", "fool", "jester", "monster"]
village_roles = ["villager", "seer", "oracle", "village drunk", "harlot", "guardian angel", "bodyguard", "detective", "augur", "village elder", "time lord", "matchmaker", "mad scientist", "hunter", "shaman"]

def update():
    global logs, startlines, endlines
    logs = list(map(str.strip, open(LOGFILE).readlines()))
    startlines = [index for index, value in enumerate(logs) if "Welcome to Werewolf, the popular detective" in value and is_lykos(value)]
    endlines = [index for index, value in enumerate(logs) if "Game lasted" in value and is_lykos(value)]

def text_from_user(user, game):
    return [i.split("\t")[2] for i in logs[startlines[game]:endlines[game]] if i.count("\t") == 2 and i.split("\t")[1] == "+%s" % user]

def find_endgame_strings(line):
    lines = []
    while is_lykos(logs[line]):
        lines.append(logs[line].split("\t")[2])
        line += 1
    return " ".join(lines).split(". ")

def depluralize(s):
    roles = {
            # Wolf roles
            "wolves": "wolf",
            "werecrows": "werecrow",
            "wolf cubs": "wolf cub",
            "alpha wolves": "alpha wolf",
            "cultists": "cultist",
            "minions": "minion",
            "traitors": "traitor",
            "hags": "hag",
            "sorcerers": "sorcerer",
            # Neutral roles
            "lycans": "lycan",
            "clones": "clone",
            "crazed shamen": "crazed shaman",
            "fools": "fool",
            "jesters": "jester",
            "monsters": "monster",
            # Village roles
            "villagers": "villager",
            "seers": "seer",
            "oracles": "oracle",
            "village drunks": "village drunk",
            "harlots": "harlot",
            "guardian angels": "guradian angel",
            "bodyguards": "bodyguard",
            "detectives": "detective",
            "augurs": "augur",
            "village elders": "village elder",
            "time lords": "time lord",
            "matchmakers": "matchmaker",
            "mad scientists": "mad scientist",
            "hunters": "hunter",
            "shamen": "shaman"
    }
    if s not in roles:
        if s in roles.values():
            return s
        return None
    return roles[s]

def parse_endgame_strings(pieces):
    pieces = pieces[3:] # Game lasted... was day ... was night
    if not pieces:
        return []
    if "The winner" in pieces[-1]:
        pieces = pieces[:-1]
    pieces = [i[4:] for i in pieces] # "The ..."
    pieces = [i[:i.index('(') - 1] if ' (' in i else i for i in pieces]
    pieces = [i.split(" was ") if "was" in i else i.split(" were ") for i in pieces]
    pieces = [(depluralize(i[0]), [k for k in re.split(' ?and |, ', i[1]) if k]) for i in pieces if depluralize(i[0])]
    return pieces

def parsed_to_playerdict(parsed):
    d = {}
    parsed = dict(parsed)
    for role in parsed:
        for player in parsed[role]:
            d[player] = role
    return d

def worddata_to_probdict(word_data):
    total = len(word_data)
    probdict = {}
    for i in set(word_data):
        probdict[i] = word_data.count(i) / total
    return probdict

def training():
    training_data = {}
    for i in range(len(startlines)):
        print("-- GAME %d --" % i)
        playerdict = parsed_to_playerdict(parse_endgame_strings(find_endgame_strings(endlines[i])))
        for player, role in playerdict.items():
            word_data = [re.sub('[,.\\?!:;\'"\\[\\]]', '', i) for i in list(map(str.lower, " ".join(text_from_user(player, i)).split()))]
            probdict = worddata_to_probdict(word_data)
            if player not in training_data:
                training_data[player] = {}
            training_data[player][role] = probdict
    return training_data

def retrain():
    import json
    with open("training_data.json", "w") as f:
        f.write(json.dumps(training()))

if __name__ == '__main__':
    retrain()
