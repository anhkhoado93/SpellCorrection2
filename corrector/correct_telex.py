# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import unicodedata
import re
import json
from corrector.params import COMPLEX_TELEX_PATH, ENG_DICT_PATH
from corrector.lang_detect import LanguageDetection

class TelexErrorCorrector:
    '''
      Fix telex typing errors by regexs by function fix_telex_sentence
      
      Step 0: Convert accent to keystrokes and push it to the end of word: 'tròiw' -> 'troifw'
      Step 1: Use regex to fix characters such as aw => ă, aa => â
      Step 2: Use regex to fix accent such as af => à, ar => ả
      Step 3: Use regex to fix additional telex fault which can't be fixed in previous step: uả -> ủa
    '''
    fi = open(COMPLEX_TELEX_PATH, encoding='utf-8')
    complex_telex = json.load(fi)
    eng_file = open(ENG_DICT_PATH, 'r')
    eng_dic = json.load(eng_file)

    def __init__(self):
        self.build_character_regexs()
        self.build_accent_regexs()
        self.lang_detect = LanguageDetection()


    def fix_telex_sentence(self, sentence):
        sentence = unicodedata.normalize('NFC', sentence)
        words = re.findall('\w+&\w+|\w+\s?:|\w+|[^\s\w]+', sentence)
        words = [self.fix_telex_word(word) for word in words]
        return ' '.join(words)

    def fix_telex_word(self, word):
        try:
            if self.eng_dic[word.lower()] == 1: 
                return word
        except:
            ## covert accents to keystrokes
            word = word.lower()
            word = unicodedata.normalize('NFKD', word)
            for accent, keystroke in self.accent_to_telex.items():
                word = re.sub(accent, keystroke, word)

            ## push keystrokes to the end of word
            reorder_word = word
            i = 1
            n = len(word)
            while (i < n):
                a = reorder_word[i]
                if a in self.additional_keystrokes + ['w'] and (reorder_word[i - 1] + a != 'tr'):
                    reorder_word = reorder_word[:i] + reorder_word[i+1:] + a
                    n = n - 1
                else:
                    i = i + 1
            word = reorder_word

            word = unicodedata.normalize('NFC', word)

            for key, value in self.char_telex_errors.items():
                word = re.sub(key, value, word)

            ## 'trưong' -> 'trương'
            word = re.sub('ưo', 'ươ', word)

            for key, value in self.accent_telex_errors.items():
                word = re.sub(key, value, word)

            for key, value in self.complex_telex.items():
                word = re.sub(key, value, word) 
            return word

    def build_character_regexs(self):
        chars = ['ư', 'â', 'ă', 'ô', 'ơ', 'ê']
        additional_keystrokes = ['w', 'a', 'w', 'o', 'w', 'e']

        char_telex_errors = dict()

        for i, c in enumerate(chars):
            parts = unicodedata.normalize('NFKD', c)
            base_c = parts[0]
            keystroke = additional_keystrokes[i]
            pattern = f'{base_c}(.*){keystroke}'
            char_telex_errors[pattern] = c + '\\1'

        char_telex_errors['d(.*)d'] = 'đ\\1'

        self.char_telex_errors = char_telex_errors

    def build_accent_regexs(self):
        chars = ['ơ', 'ô', 'ê', 'e', 'ă', 'â', 'ư', 'a', 'o', 'i', 'u', 'y']
        accents = ['í', 'ỉ', 'ĩ', 'ì', 'ị']
        accents = [unicodedata.normalize('NFKD', a)[1] for a in accents]
        additional_keystrokes = ['s', 'r', 'x', 'f', 'j']
        self.additional_keystrokes = additional_keystrokes

        accent_to_telex = dict()
        for i in range(len(accents)):
            accent_to_telex[accents[i]] = additional_keystrokes[i]

        self.accent_to_telex = accent_to_telex

        accent_telex_errors = dict()

        for c in chars:
            for i, a in enumerate(accents):
                text = ''.join([c, a])
                merged = unicodedata.normalize('NFC', text)

                keystroke = additional_keystrokes[i]
                pattern = f'{c}(.*){keystroke}'
                accent_telex_errors[pattern] = merged + '\\1'

        self.accent_telex_errors = accent_telex_errors


# %%
if __name__ == "__main__":
    corrector = TelexErrorCorrector()
    fixed = corrector.fix_telex_sentence('Quaayx. J&T Leen .naof Cacs Bajn Owi')
    print(fixed)
# %%
