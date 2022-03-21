import re
import json
import unicodedata
import unidecode
from corrector.params import WORDS_PATH, TELEX_RULE_PATH
import visen

words_file = open(WORDS_PATH, 'r')
WORDS = json.load(words_file)

telex_rule_file = open(TELEX_RULE_PATH, 'r')
telex_rule = json.load(telex_rule_file)

def know2(words):
    possible_words = []
    for w in words:
        if w.lower() in WORDS:
            possible_words.append(w)
    return possible_words

def telex_processor(word):
    "Process text before training"
    # Path to telex rule file
    # rule = "af as ax aj ar aa aw aaf afa aas asa aax axa aaj aja aar ara awf afw aws asw  awr arw awx axw awj ajw".split()
    # Possible typo endword in Vietnamese
    ends = "a e o f s r x j w d".split()
    possible_words = []
    
    
    if word[:2] in ["dd", "DD", "Dd"]:
        word = telex_rule[word[:2]]+word[2:]
                
    if word[-2:] in ["oa", "ao", "oe", "eo"]:
        possible_words.append(word) 
                

    if len(word) > 2:
        if word[-2] in ends:  
            # TODO: Consider this error with word_length = 3, loi voi tu oa, ao, oe, eo
            if len(word) == 3:
                if word[0:2] in ["oa", "ao", "oe", "eo"] or word[1:] in ["oa", "ao", "oe", "eo"]:
                    if word[0] + word[2] in telex_rule:
                        chain = word[0] + word[2]
                        temp  = telex_rule[chain] + word[1]
                        possible_words.append(temp)
                    elif word[0] + word[2] in telex_rule:
                        chain = word[1] + word[2]
                        temp  = word [0] + telex_rule[chain]
                        possible_words.append(temp)
                    # else:

                else:
                    chain = str(word[1]+word[2])
                    if chain in telex_rule:
                        temp = word[0]+telex_rule[chain]
                        possible_words.append(temp)
                    else:
                        possible_words.append(word)
            else:
                for i in range(len(word)):
                    #the case dupplicate the cosidering letter
                    # print(word[i])
                    if i < len(word[:-1]) - 1:
                        # print(word[i])
                        # TODO: The case: uow -> ươ
                        if word[i:i+2] == "uo":                       
                            # if (word[i:i+2] + lett for lett in word[i+2:end]) in telex_rule:
                            if (word[i:i+2]+word[-2]+word[-1]) in telex_rule:
                                chain = str(word[i:i+2]+word[-2]+word[-1])
                                temp = word[:i]+telex_rule[chain]+word[i+2:-2]
                                possible_words.append(temp)
                                
                            elif (word[i:i+2]+word[-2]) in telex_rule:
                                chain = str(word[i:i+2]+word[-2])
                                temp = word[:i]+telex_rule[chain]+word[i+2:-2]+word[-1]
                                possible_words.append(temp)
                                
                        if (word[i]+word[-2]+word[-1]) in telex_rule:
                            chain = str(word[i]+word[-2]+word[-1])
                            temp = word[:i]+telex_rule[chain]+word[i+1:-2]
                            possible_words.append(temp)
                            
                        elif (word[i]+word[-2]) in telex_rule:
                            chain = str(word[i]+word[-2])
                            temp = word[:i]+telex_rule[chain]+word[i+1:-2]+word[-1]
                            # print(temp)
                            possible_words.append(temp)
                            
                        elif(word[i] + word[-1]) in telex_rule:
                            chain = str(word[i]+word[-1])
                            temp = word[:i]+telex_rule[chain]+word[i+1:-1]
                            possible_words.append(temp)
                            
                    else:
                        # print(word[i])
                        if(word[i] + word[-1]) in telex_rule:
                            chain = str(word[i]+word[-1])
                            temp = word[:i]+telex_rule[chain]+word[i+1:-1]
                            possible_words.append(temp)
                            
                        else:
                            possible_words.append(word)
                    
        elif word[-1] in ends:
            for i in range(len(word)):
                if (i < len(word)-1):
                    # TODO: The case: uow -> ươ
                    if word[i:i+2] == "uo":                       
                        # if (word[i:i+2] + lett for lett in word[i+2:end]) in telex_rule:
                        if (word[i:i+3]+word[-1]) in telex_rule:
                            chain = str(word[i:i+3]+word[-1])
                            temp = word[:i]+telex_rule[chain]+word[i+3:-1]
                            possible_words.append(temp)
                            
                        elif (word[i:i+2]+word[-1]) == "uow":
                            temp = word[:i]+telex_rule["uow"]+word[i+2:-1]
                            possible_words.append(temp)
                            
                    if (word[i]+word[i+1]+word[-1]) in telex_rule:
                        # print(word[i]+word[i+1]+word[-1])
                        # Chain of letter may be telex
                        chain = str(word[i]+word[i+1]+word[-1])
                        temp = word[:i]+telex_rule[chain]+word[i+2:-1]
                        possible_words.append(temp)
                    elif (word[i]+word[-1]) in telex_rule:
                        chain = str(word[i]+word[-1])
                        # print(word[i]+word[-1])
                        # print(telex_rule[chain])
                        temp = word[:i]+telex_rule[chain]+word[i+1:-1]
                        possible_words.append(temp)
                        # Accept words only end normal
                        # if temp[-1] not in ends:
                        # possible_words.append(temp)
                    else:
                        possible_words.append(word)
                else:
                    pass
            # print("so 2")
        else:
            for i in range(len(word[:-1])):
                if (word[i:i+3]) in telex_rule:
                    chain = str(word[i:i+3])
                    temp = word[:i]+telex_rule[chain]+word[i+3:]
                    possible_words.append(temp)
                if (word[i]+word[i+1]) in telex_rule:
                    chain = str(word[i]+word[i+1])
                    temp = word[:i]+telex_rule[chain]+word[i+2:]
                    possible_words.append(temp)
                    
            possible_words.append(word)
                    
    elif len(word) == 2:
        if str(word) in telex_rule:
            possible_words.append(telex_rule[word])
        else:
            possible_words.append(word)
            
    # Remove unknow words
    possible_words  = know2(possible_words)
    # Remove duplicate
    possible_words = list(dict.fromkeys(possible_words))
    # print(possible_words)
    if possible_words:
        return str(possible_words[0])
    else:
        return word

def in_vietnamese_dict(word):
    try:
        return WORDS.get(word, False) != False
    except:
        return False


def fix_telex_sentence(sentence):
    sentence = unicodedata.normalize('NFC', sentence)
    words = re.findall('\w+&\w+|\w+\s?:|\w+|[^\s\w]+', sentence)
    words = [telex_processor(word) for word in words]
    words_vn_filter = [unidecode.unidecode(word) if not in_vietnamese_dict(word.lower()) else word for word in words]
    return visen.clean_tone(' '.join(words_vn_filter))

if __name__ == "__main__":
    sent = 'Ddaamff nayf gias thees naof banj?'
    print(fix_telex_sentence(sent))