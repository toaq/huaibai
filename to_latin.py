import json
import re
import unicodedata

full_stops = {"󱛕", "󱛖", "󱛗"}

consonants = {
    "󱚰": "m",
    "󱚲": "b",
    "󱚳": "p",
    "󱚴": "f",
    "󱚵": "n",
    "󱚶": "d",
    "󱚷": "t",
    "󱚸": "z",
    "󱚹": "c",
    "󱚺": "s",
    "󱚻": "r",
    "󱚼": "l",
    "󱚽": "nh",
    "󱚾": "j",
    "󱚿": "ch",
    "󱛀": "sh",
    "󱛁": "ꝡ",
    "󱛂": "q",
    "󱛃": "g",
    "󱛄": "k",
    "󱛅": "'",
    "󱛆": "h",
}

vowels = {
    "󱚲": "u",
    "󱚴": "e",
    "󱚹": "ı",
    "󱚺": "a",
    "󱛃": "o",
}

t2 = "\U000f16ca"
t3 = "\U000f16cb"
t4 = "\U000f16cc"
strip_tones = str.maketrans("", "", t2 + t3 + t4)
between_vowels = {"\U000f16cd", "\U000f16ce"}
acute_accent = "\u0301"
diaeresis = "\u0308"
circumflex_accent = "\u0302"


def word_to_latin(word):
    latin = ""
    tone = (
        acute_accent
        if t2 in word
        else diaeresis
        if t3 in word
        else circumflex_accent
        if t4 in word
        else ""
    )
    word = word.translate(strip_tones)
    vowel = len(word) > 1 and word[1] not in vowels
    placed_tone = False
    for c in word:
        if c == "󱚱":
            latin += "m"
            vowel = False
        elif c == "󱛂":
            latin += "q"
            vowel = False
        elif c in between_vowels:
            vowel = True
            continue
        elif vowel and c in vowels:
            if placed_tone:
                latin += vowels[c]
            else:
                latin += vowels[c] + tone
                placed_tone = True
            vowel = False
        else:
            latin += consonants[c]
            vowel = True
    return unicodedata.normalize("NFKC", latin.lstrip("'"))


trans = str.maketrans("󱛒󱛕󱛖󱛗󱛛", "\u0323.!? ", "󱛓󱛘󱛙")


def sentence_to_latin(sentence):
    sentence = sentence.translate(trans)
    sentence = re.sub(r"\s󱛚", "", sentence)
    sentence = re.sub(r"\s󱛔", ",", sentence)
    sentence = re.sub(r"[󱚰-󱛎]+", lambda m: word_to_latin(m[0]), sentence)
    sentence = re.sub(r"[a-zA-Zıꝡ]", lambda m: m[0].upper(), sentence, 1)
    sentence = re.sub(r"\s([.?!])", lambda m: m[1], sentence)
    sentence = sentence.replace("\u00a0", " ")
    return sentence


def derani_to_latin(string):
    sentences = re.findall(r".+?(?:[󱛕󱛖󱛗]|$)", string)
    return "".join(map(sentence_to_latin, sentences))


if __name__ == "__main__":
    with open("src/assets/minecraft/lang/qtq_tqg.json") as f:
        lang = json.load(f)

    with open("src/assets/minecraft/lang/qtq_latin.json", "w") as f:
        lang = {k: derani_to_latin(v) for k, v in lang.items()}
        lang["language.code"] = "qtq_latin"
        json.dump(lang, f, ensure_ascii=False, indent=4)
