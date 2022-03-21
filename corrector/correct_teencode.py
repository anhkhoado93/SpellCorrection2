import itertools
import json
import os
import re
import string
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import kenlm
import unidecode

from corrector.params import (ENG_DICT_PATH, SHORT_WORD_PATH,
                              LM_THRESHOLD, SINGLE_WORD_PATH,
                              TEENCODE_REGEX_PATH, VOWEL_PATH, WLM_PATH)
from corrector.utils import *

kenlm_model = kenlm.Model(WLM_PATH)


def read_file(file_path):
    fi = open(file_path, 'r', encoding='utf-8')
    ls = fi.readlines()
    return ls

vowel_file = open(VOWEL_PATH, encoding='utf-8')
vowel_dic = json.load(vowel_file)

short_word_file = open(SHORT_WORD_PATH, encoding='utf-8')
short_word_dic = json.load(short_word_file)

teencode_re_file = open(TEENCODE_REGEX_PATH, encoding='utf-8')
teencode_re_dic = json.load(teencode_re_file)

single_word_dic = read_file(SINGLE_WORD_PATH)
single_word_dic = [re.sub('\n', '', s) for s in single_word_dic]

eng_file = open(ENG_DICT_PATH, 'r')
eng_dic = json.load(eng_file)


def remove_accent(text, remove_punct=True):
    if remove_punct:
        text = text.translate(str.maketrans('', '', string.punctuation))
    return unidecode.unidecode(text)


def unique_charaters(sent):
    i = 0
    new_sent = ''
    while i < len(sent):
        j = i + 1
        while (not sent[i].isdigit()) and j < len(sent) and sent[i] == sent[j]:
            j = j + 1
        new_sent += sent[i]
        i = j
    return new_sent


def replace_one_one(word, dictionary = short_word_dic):
    '''
    replace teencode with correct one by using dictionary
    Input: 
        word        :str - teencode word 
        dictionary  : pd.Dataframe - 1-1 dictionary
    return: 
        new_word    :str - correct word
    '''
    new_word = dictionary.get(word.lower(), word)
    if new_word == word and type(new_word) == str:
        uni_word = replace_with_regex(word, teencode_re_dic, dictionary)
        new_word = dictionary.get(uni_word, word)
    return new_word


def replace_with_regex(word, regex_list, dic_one_one, check=0):
    '''
    replace teencode with correct one by using rule (regex)
    Input:
        word        : str - teencode word
        regex_list  : pd.DataFrame - teencode regex 
        dic_one_one : pd.DataFrame - 1-1 dictionary
        check       : boolean - number of times using this method
    return: 
        new_word    : str - correct word
    '''
    new_word = unique_charaters(word)
    for pattern in regex_list.keys():
        if re.search(pattern, new_word):
            new_word = re.sub(pattern, regex_list[pattern], new_word)
            break
    if dic_one_one.get(new_word, new_word) != new_word and type(dic_one_one.get(new_word, new_word)) == str: 
        return dic_one_one.get(new_word, new_word)
    if check == 2 or unidecode.unidecode(new_word) in single_word_dic: 
        return new_word
    new_word = replace_with_regex(new_word, teencode_re_dic, short_word_dic, check + 1)
    return new_word


def correct_vowel(word, vowel_dictionary):
    '''
    correct sentence has vowel next to symbol by rule. Ex: a~ -> ã
    Input:
        sent    : str - teencode sentence
        vowel_dictionary: pd.DataFrame - vietnamese_vowel dictionary
    return:
        sent    : str - correct sentence
    '''
    pattern = r'[aăâeêuưiyoôơ][`~\']'
    p = re.search(pattern, word)
    new_word = word
    if p:
        idx = p.span()
        replace_vowel = vowel_dictionary[word[idx[0]]][word[idx[0] + 1]]
        new_word = re.sub(pattern, replace_vowel, new_word)
    return new_word


def correct_teencode_word(word, replace=False):
    word = preprocess(word)
    try:
        if eng_dic[word.lower()] == 1: return word
    except:
        new_word = word
        new_word = correct_vowel(new_word, vowel_dic)
        if replace:
            new_word = replace_one_one(new_word, short_word_dic)
        if word == new_word:
            new_word = replace_with_regex(new_word, teencode_re_dic, short_word_dic)
        return new_word

def correct_teencode_lm(sent):
    sent, lm_scores = correct_short_word_sent_lm(sent)
    words = re.findall('\w*[~`\']\w*|\w+&\w+|\w+\s?:|\w+|[^\s\w]+', sent)
    sent = ""
    for word in words:
        new_word = correct_teencode_word(word)
        sent += new_word + ' '
    sent = processing_after(sent)
    return sent, lm_scores
        

def correct_teencode(sent):
    '''
    correct teencode sentence
    Input: 
        sent    : str - teencode sent
    Return:
        correct sent 
    '''
    sent = preprocess(sent)
    words = re.findall('\w*[~`\']\w*|\w+&\w+|\w+\s?:|\w+|[^\s\w]+', sent)
    sent = ""
    for word in words:
        new_word = correct_teencode_word(word)
        sent += new_word + ' '
    sent = processing_after(sent)
    return sent

def correct_short_word_sent(sent):
    sent = preprocess(sent)
    words = re.findall('\w+&\w+|\w+\s?:|\w+|[^\s\w]+', sent)
    sent = ""
    for word in words:
        new_word = replace_one_one(word)
        sent += new_word + ' '
    sent = processing_after(sent)
    return sent

def correct_short_word_sent_lm(text):
    text_cleaned = preprocess(text)
    words = re.findall('\w+&\w+|\w+\s?:|\w+|[^\s\w]+', text_cleaned)
    new_words = []
    for word in words:
        new_word = replace_one_one(word, short_word_dic)
        if type(new_word) == str:
            new_word = [new_word]
        new_words.append(new_word)
    sents = [' '.join(words) for words in list(itertools.product(*new_words))]
    sents = [processing_after(sent) for sent in sents]

    lm_scores = []
    for i in range(len(sents)):
        lm_scores.append({
            'text': sents[i],
            'score': kenlm_model.score(sents[i].lower())
        })
    best_lm_sent = max(lm_scores, key=lambda x: x['score'])['text']
    best_lm_score = max(lm_scores, key=lambda x: x['score'])['score']

    if best_lm_score < LM_THRESHOLD and len(lm_scores) > 1:
        # with open('data/extra.txt', 'a') as f:
        #     f.write(datetime.today().strftime("%d/%m/%Y %H:%M:%S") + '\t' + str(best_lm_sent) + '\t' + str(best_lm_score) + '\n')
        return text, lm_scores
    else:
        return best_lm_sent, lm_scores


if __name__ == '__main__':
    # WLM_PATH = "lm/data_chinh_ta.binary"
    # kenlm_model = KenLM.Model(WLM_PATH)
    # print(correct_short_word_sent("k c"))
    print(LM_THRESHOLD)
