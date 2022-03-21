from corrector.correct_telex import TelexErrorCorrector
import itertools
import unicodedata
import json
import re
import string
from corrector.params import *
import kenlm
kenlm_model = kenlm.Model(WLM_PATH)

telexCorrector = TelexErrorCorrector()

fi = open(WORDS_PATH, 'r', encoding='utf-8')
single_dict = json.load(fi)

fi = open(VIETNAMESE_DICT, 'r', encoding='utf-8')
vietnamese_dict = json.load(fi)

eng_file = open(ENG_DICT_PATH, 'r')
eng_dic = json.load(eng_file)

def read_close_charater_json():
    fi = open(CLOSE_CHAR)
    close_char = json.load(fi)
    for character in close_char.keys():
        close_char[character] = close_char[character].split('|')
    return close_char

close_char = read_close_charater_json()

def preprocess(sent):
    '''
    preprocess
        multi space, characters
        after a comma, semi-comma has space
    '''
    sent = sent.lower()
    sent = unicodedata.normalize("NFC", sent)
    sent = re.sub('\n', '', sent)
    sent = re.sub(r'\s+', r' ', sent)
    sent = re.sub(r'^\s', '', sent)
    sent = re.sub(r'\s$', '', sent)
    return sent

def processing_after(sent):
    sent = re.sub('\n', '', sent)
    sent = re.sub(r'\s+', r' ', sent)
    sent = re.sub(r'^\s', '', sent)
    sent = re.sub(r'\s$', '', sent)
    sent = re.sub(r'\s+(?=(\.|,))', '', sent)
    sent = re.sub(r'\s+/\s+', '/', sent)
    return sent

def in_single_dict(word):
    try:
        return single_dict[word]
    except:
        return 0

def in_vietnamese_dict(word):
    try:
        return vietnamese_dict[word] == 1
    except:
        return False

def gen_correct_word(word):
    if word in string.punctuation:
        return [word]
    ls_correct_word = []
    new_word = word
    new_word = telexCorrector.fix_telex_word(new_word)
    if in_single_dict(new_word): 
        ls_correct_word.append(new_word)
        return ls_correct_word
    for j in range(len(word)):
        try:
            i = len(word) - j - 1
            replace_char = close_char[word[i]]
            for new_ch in replace_char:
                new_word = word[:i] + new_ch + word[i + 1:]
                new_word = telexCorrector.fix_telex_word(new_word)
                if in_single_dict(new_word): 
                    ls_correct_word.append(new_word)
        except: 
            pass
    ls_correct_word.sort(key=lambda w: in_single_dict(w), reverse=True)
    return ls_correct_word

def find_correct_phrase(ls_1st, ls_2nd):
    for word_1st in ls_1st:
        for word_2nd in ls_2nd:
            new_word = word_1st + ' ' + word_2nd
            if in_vietnamese_dict(new_word):
                return word_1st, word_2nd
    return ls_1st[0], None
    
def correct_close_character_sent(sent):
    sent = preprocess(sent)
    words = re.findall('\w+&\w+|\w+\s?:|\w+|[^\s\w]+', sent)
    ls_cor_word = []
    for word in words:
        ls_cor_word.append(gen_correct_word(word))
    is_fix = [False] * len(words)
    for i in range(len(words)):
        if is_fix[i]: continue
        if len(ls_cor_word[i]) == 0: 
            is_fix[i] = True
            continue
        if len(ls_cor_word[i]) == 1 or i == len(words) - 1:
            is_fix[i] = True
            words[i] = ls_cor_word[i][0]
            continue
        
        new_word_1st, new_word_2nd = find_correct_phrase(ls_cor_word[i], ls_cor_word[i + 1])
        words[i] = new_word_1st
        is_fix[i] = True
        if new_word_2nd is not None:
            words[i + 1] = new_word_2nd
            is_fix[i + 1] = True
    sent = ' '.join(words)
    sent = processing_after(sent)
    return sent

def correct_close_character_sent_lm(sent):
    sent = preprocess(sent)
    words = re.findall('\w+&\w+|\w+\s?:|\w+|[^\s\w]+', sent)
    ls_cor_word = []
    for word in words:
        if in_single_dict(word):
            ls_cor_word.append([word])
        else:
            ls_cor_word.append(gen_correct_word(word))
    sents = [' '.join(words) for words in list(itertools.product(*ls_cor_word))]    # Combination candiates
    sents = [processing_after(sent) for sent in sents] 
    if len(sents) > 0:
        lm_scores = []
        for i in range(len(sents)):
            lm_scores.append({
                'text': sents[i],
                'score': kenlm_model.score(sents[i].lower())
            })
        
        best_lm_sent = max(lm_scores, key=lambda x: x['score'])['text']
        best_lm_score = max(lm_scores, key=lambda x: x['score'])['score']
        
        if best_lm_score < LM_THRESHOLD and len(lm_scores) > 1: # Set threshold
            return sent
        else:
            return best_lm_sent
    else:
        return sent

def read_file(file_path):
    fi = open(file_path, 'r', encoding='utf-8')
    ls = fi.readlines()
    return ls

if __name__ == '__main__':
    print(correct_close_character_sent_lm('Quaayx. J&T Leen .naof Cacs Bajn Owi'))