import json
import re
import unicodedata

FULL_STOPS = {"󱛕", "󱛖", "󱛗"}

CONSONANTS = {
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

VOWELS = {
    "󱚲": "u",
    "󱚴": "e",
    "󱚹": "ı",
    "󱚺": "a",
    "󱛃": "o",
}

DERANI_T2 = "\U000f16ca"
DERANI_T3 = "\U000f16cb"
DERANI_T4 = "\U000f16cc"
STRIP_TONES = str.maketrans("", "", DERANI_T2 + DERANI_T3 + DERANI_T4)
BETWEEN_VOWELS = {"\U000f16cd", "\U000f16ce"}
UNDERDOT = "\N{combining dot below}"
TRANSLATE_PUNCTUATION = str.maketrans("󱛕󱛖󱛗󱛛", ".!? ", "󱛓󱛘󱛙")


class DeraniToLatin:
    def __init__(self, prefix_separator=None, ꝡ_replacement=None):
        self.prefix_separator = prefix_separator
        self.ꝡ_replacement = ꝡ_replacement

    def convert_word(self, word):
        latin = ""
        tone = (
            "\N{combining acute accent}"
            if DERANI_T2 in word
            else "\N{combining diaeresis}"
            if DERANI_T3 in word
            else "\N{combining circumflex accent}"
            if DERANI_T4 in word
            else ""
        )
        word = word.translate(STRIP_TONES)
        vowel = len(word) > 1 and word[1] not in VOWELS
        placed_tone = False
        for c in word:
            if c == "󱚱":
                latin += "m"
                vowel = False
            elif c == "󱛂":
                latin += "q"
                vowel = False
            elif c == "󱛒":
                if self.prefix_separator:
                    latin += self.prefix_separator
                else:
                    # Place a dot under the first vowel of the last raku:
                    latin = re.sub(
                        "[aeıou\u0301\u0302\u0308]+[mq]?$",
                        lambda m: m[0][0] + UNDERDOT + m[0][1:],
                        latin,
                        1,
                    )
            elif c in BETWEEN_VOWELS:
                vowel = True
                continue
            elif vowel and c in VOWELS:
                if placed_tone:
                    latin += VOWELS[c]
                else:
                    vowel = VOWELS[c]
                    if tone != "" and vowel == "ı":
                        vowel = "i"
                    latin += vowel + tone
                    placed_tone = True
                vowel = False
            else:
                consonant = CONSONANTS[c]
                if consonant == "ꝡ" and self.ꝡ_replacement:
                    consonant = self.ꝡ_replacement
                latin += consonant
                vowel = True
        return unicodedata.normalize("NFKC", latin.lstrip("'"))

    def convert_sentence(self, sentence):
        if not re.match(".*[\U000f16b0-\U000f16df]", sentence):
            return sentence
        sentence = sentence.translate(TRANSLATE_PUNCTUATION)
        sentence = re.sub(r"\s󱛚", "", sentence)
        sentence = re.sub(r"\s󱛔", ",", sentence)
        sentence = re.sub(r"[󱚰-󱛒]+", lambda m: self.convert_word(m[0]), sentence)
        sentence = re.sub(r"\w", lambda m: m[0].upper(), sentence, 1)
        sentence = re.sub(r"\s([.?!])", lambda m: m[1], sentence)
        sentence = sentence.replace("\u00a0", " ")
        return sentence

    def convert(self, text):
        sentences = re.findall(r".+?(?:[󱛕󱛖󱛗]|$)", text)
        return "".join(self.convert_sentence(s) for s in sentences)


if __name__ == "__main__":
    with open("src/assets/minecraft/lang/qtq_tqg.json") as f:
        lang = json.load(f)

    with open("src/assets/minecraft/lang/qtq_latn_tqg.json", "w") as f:
        d2l = DeraniToLatin(prefix_separator="·")
        lang = {k: d2l.convert(v) for k, v in lang.items()}
        lang["language.code"] = "qtq_latn_tqg"
        json.dump(lang, f, ensure_ascii=False, indent=4)
