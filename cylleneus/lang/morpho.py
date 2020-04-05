class Morph:
    def __init__(self, desc: str):
        (
            self.pos,
            self.person,
            self.number,
            self.tense,
            self.mood,
            self.voice,
            self.gender,
            self.case,
            self.group,
            self.stem,
        ) = desc
        if self.pos in ["a", "r"]:
            self.degree, self.person = self.person, "-"

    def __str__(self):
        return f"{self.pos}{self.person}{self.number}{self.tense}{self.mood}{self.voice}{self.gender}{self.case}{self.group}{self.stem}"

    def __eq__(self, other):
        results = []
        comp = str(other)
        for i, tag in enumerate(str(self)):
            if comp[i] == "-":
                results.append(True)
            else:
                results.append(comp[i] == tag)
        return all(results)

    def __add__(self, other):
        pos = self.pos if (self.pos != "-" and other.pos == "-") else other.pos
        person = (
            self.person
            if (self.person != "-" and other.person == "-")
            else other.person
        )
        number = (
            self.number
            if (self.number != "-" and other.number == "-")
            else other.number
        )
        tense = (
            self.tense if (self.tense != "-" and other.tense == "-") else other.tense
        )
        mood = self.mood if (self.mood != "-" and other.mood == "-") else other.mood
        voice = (
            self.voice if (self.voice != "-" and other.voice == "-") else other.voice
        )
        gender = (
            self.gender
            if (self.gender != "-" and other.gender == "-")
            else other.gender
        )
        case = self.case if (self.case != "-" and other.case == "-") else other.case
        group = (
            self.group if (self.group != "-" and other.group == "-") else other.group
        )
        stem = self.stem if (self.stem != "-" and other.stem == "-") else other.stem

        desc = f"{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{group}{stem}"
        return Morph(desc)

    def __sub__(self, other):
        pos = other.pos if (other.pos != self.pos) else "-"
        person = other.person if (other.person != self.person) else "-"
        number = other.number if (other.number != self.number) else self.number
        tense = other.tense if (other.tense != self.tense) else "-"
        mood = other.mood if (other.mood != self.mood) else "-"
        voice = other.voice if (other.voice != self.voice) else "-"
        gender = other.gender if (other.gender != self.gender) else "-"
        case = other.case if (other.case != self.case) else "-"
        group = other.group if (other.group != self.group) else "-"
        stem = other.stem if (other.stem != self.stem) else "-"

        desc = f"{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{group}{stem}"
        return Morph(desc)


def leipzig2wn(gloss: str):
    if gloss:
        pos = (
            person
        ) = number = tense = mood = voice = gender = case = group = stem = "-"

        tags = [tag.strip() for tag in gloss.upper().split(".") if tag.strip()]
        for tag in tags:
            if tag[0].isdigit():
                if len(tag) == 3 and tag[1:] in ["SG", "PL", "DU", "XX"]:
                    person = _from_leipzig[tag[0]]
                    number = _from_leipzig[tag[1:]]
                elif len(tag) == 1 and tag in ["1", "2", "3", "4", "5"]:
                    group = _from_leipzig[tag]
            if tag in ["NN", "VB", "ADJ", "ADV"]:
                pos = _from_leipzig[tag]
            elif tag in ["SG", "PL", "DU", "XX"]:
                number = _from_leipzig[tag]
            elif tag in ["PRS", "IMPRF", "FUT", "PRF", "PLPRF", "FUTPRF", "AOR"]:
                tense = _from_leipzig[tag]
                pos = "v"
            elif tag in ["IND", "SBJV", "IMP", "PTCP", "INF", "GER", "GERV", "SUP", "OPT", "INJ", "PREC", "COND",
                         "PART"]:
                mood = _from_leipzig[tag]
                pos = "v"
            elif tag in ["ACT", "PASS", "DEP", "MID"]:
                voice = _from_leipzig[tag]
                pos = "v"
            elif tag in ["M", "F", "N"]:
                gender = _from_leipzig[tag]
            elif tag in ["POS", "COMP", "SUPL"]:
                person = _from_leipzig[tag]
                if pos == "-" and (
                    gender != "-" or case != "-" or number != "-" or group != "-"
                ):
                    pos = "a"
                else:
                    pos = "r"
            elif tag in ["NOM", "GEN", "DAT", "ACC", "ABL", "LOC", "VOC", "INS", "CPD"]:
                case = _from_leipzig[tag]
                # if mood in 'pgds':
                #     pos = 'v'
                # elif person != '-':  # adjectives have degree
                #     pos = 'a'
                # else:
                #     pos = 'n'
        desc = f"{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{group}{stem}"
        return desc


def apn2wn(gloss: str) -> str:
    if gloss:
        gender = stem = "-"
        pos, group, case, number, degree, mood, tense, voice, person, _ = [
            _from_apn[index][tag] if tag.strip() else "-"
            for index, tag in enumerate(gloss)
        ]

        if pos == "a" and group == "2":
            group = "1"
        if pos in ["a", "r"]:
            person = degree
        if mood == "s":
            if gloss[5] == "8":
                case = "n"
            elif gloss[5] == "9":
                case = "a"

        desc = f"{pos}{person}{number}{tense}{mood}{voice}{gender}{case}{group}{stem}"
        return desc


_from_apn = [
    {
        # POS
        "A": "n",
        "B": "v",
        "C": "a",
        "D": "a",
        "E": "n",  # PRONOUN
        "F": "-",
        "G": "-",
        "H": "-",
        "I": "-",
        "J": "-",
        "K": "-",
        "L": "-",
        "M": "r",
        "N": "r",
        "O": "r",
        "P": "r",
        "Q": "r",
        "R": "-",  # PREPOSITION
        "S": "-",  # CONJUNCTION
        "T": "-",  # CONJUNCTION
        "U": "-",  # INTERJECTION
        "#": "v",
    },
    {
        # GROUP
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
    },
    {
        # CASE
        "1": "n",
        "2": "v",
        "3": "a",
        "4": "g",
        "5": "d",
        "6": "b",
        "7": "l",
        "8": "-",  # indeclinable
    },
    {
        # NUMBER
        "1": "s",
        "2": "p",
    },
    {
        # DEGREE
        "1": "p",
        "2": "c",
        "3": "s",
    },
    {
        # MOOD
        "1": "i",
        "2": "s",
        "3": "m",
        "4": "p",
        "5": "n",
        "6": "d",
        "7": "g",
        "8": "u",
        "9": "u",
    },
    {
        # TENSE
        "1": "p",
        "2": "i",
        "3": "f",
        "4": "r",
        "5": "l",
        "6": "t",
        "7": "r",
        "8": "l",
        "9": "f",
    },
    {
        # VOICE
        "1": "a",
        "2": "p",
        "3": "d",
        "4": "d",
    },
    {
        # PERSON
        "1": "1",
        "2": "2",
        "3": "3",
    },
]

_from_leipzig = {
    # POS
    "NN":     "n",
    "VB":     "v",
    "ADJ":    "a",
    "ADV":    "r",
    # CASE
    "NOM":    "n",
    "VOC":    "v",
    "ACC":    "a",
    "GEN":    "g",
    "DAT":    "d",
    "ABL":    "b",
    "LOC":    "l",
    "INS":    "i",
    "CPD":    "c",
    # NUMBER
    "SG":     "s",
    "PL":     "p",
    "DU":     "d",
    "XX":     "-",
    # DEGREE
    "POS":    "p",
    "COMP":   "c",
    "SUPL":   "s",
    # MOOD
    "IND":    "i",
    "SBJV":   "s",
    "IMP":    "m",
    "PTCP":   "p",
    "INF":    "n",
    "GER":    "d",
    "GERV":   "g",
    "SUP":    "u",
    "OPT":    "o",
    "COND":   "c",
    "PREC":   "r",
    "INJ":    "j",
    # TENSE
    "PRS":    "p",
    "IMPRF":  "i",
    "FUT":    "f",
    "PRF":    "r",
    "PLPRF":  "l",
    "FUTPRF": "t",
    "AOR":    "a",
    # VOICE
    "ACT":    "a",
    "PASS":   "p",
    "DEP":    "d",
    "MID":    "m",
    # PERSON
    "1":      "1",
    "2":      "2",
    "3":      "3",
    # GROUP
    "4":      "4",
    "5":      "5",
    # GENDER
    "M":      "m",
    "F":      "f",
    "N":      "n",
}
