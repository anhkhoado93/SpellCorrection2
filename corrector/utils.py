import re
import unicodedata
from underthesea import word_tokenize
import fasttext

LEGAL = " !\"#$%&'()*+,-./0123456789:;<=>?@[\\]^_`abcdefghijklmnopqrstuvwxyzáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ{|}~"
PUNCT = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

def separate_number_chars(s):
    res = re.split('([-+]?\d+\.\d+)|([-+]?\d+)', s.strip())
    res_f = [r.strip() for r in res if r is not None and r.strip() != '']
    return ' '.join(res_f)

def match_case(src, predicted):
    src = src.strip()
    out = []
    if len(predicted.split()) == len(src.split()):
        for i in range(len(predicted)):
            if src[i].isupper():
                out.append(predicted[i].upper())
            elif src[i] in PUNCT or src[i] not in LEGAL:
                out.append(src[i])
            else:
                out.append(predicted[i])
        return ''.join(out)
    else:
        return predicted

def create_label(text):

    '''
    Take a string -> intext and label
    '''
    tokens = word_tokenize(text)
    words = []
    ids_punct = {',':[], '.':[]}
    i = 0
    for token in tokens:
        if token not in ids_punct.keys():
            words.append(token)
            i+=1
        else:
            ids_punct[token].append(i-1)

    label = [0]*len(words)
    for pun, ids in ids_punct.items():
        for index in ids:
            label[index] = 1 if pun == ',' else 2
    return label

def match_punct(src_sent, predicted_sent):
    if len(predicted_sent.split()) == len(src_sent.split()):
        label = create_label(predicted_sent)
        words = word_tokenize(src_sent)
        
        convert = {0: '', 1: ',', 2: '.', 3: ''}
        seq = [ word+convert[label[i]] for i, word in enumerate(words)]
        seq = ' '.join(seq)
    
        return '. '.join(map(lambda s: s.strip().capitalize(), seq.split('.')))
    else:
        return src_sent


def preprocess(sent, remove_punct=True):
    # if remove_punct:
    #     sent = re.sub('[,.!?|]', " ", sent)
    sent = separate_number_chars(sent)
    sent = unicodedata.normalize("NFC", sent)
    sent = re.sub('\n', '', sent)
    sent = re.sub(r'\s+', r' ', sent)
    sent = re.sub(r'^\s', '', sent)
    sent = re.sub(r'\s$', '', sent)
    sent = sent.rstrip('_+!@#$?^')
    sent = sent.lstrip('_+!@#$?^')
    return sent

def processing_after(sent):
    sent = re.sub('\n', '', sent)
    sent = re.sub(r'\s+', r' ', sent)
    sent = re.sub(r'^\s', '', sent)
    sent = re.sub(r'\s$', '', sent)
    sent = re.sub(r'\s\.\s', '.', sent)
    sent = re.sub(r'\s/\s', '/', sent)
    sent = re.sub(r'\s+(?=(\.|,))', '', sent)
    sent = re.sub(r'\s+/\s+', '/', sent)
    sent = re.sub(r'\s,\s', ', ', sent)
    sent = re.sub(r'\s.\s', '. ', sent)
    return sent