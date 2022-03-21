import kenlm
import unidecode
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from autocorrection.correct import AutoCorrection
from autocorrection.params import MODEL_NAME
from corrector.correct_close_character import correct_close_character_sent_lm
from corrector.correct_teencode import (correct_short_word_sent_lm,
                                        correct_teencode_lm, preprocess,
                                        processing_after)
from corrector.correct_telex import TelexErrorCorrector
from corrector.correct_telex_new import fix_telex_sentence
from corrector.params import LM_THRESHOLD, WLM_PATH
from corrector.utils import *
from tone.params import MODEL_PATH, SRC_VOCAB_PATH, TGT_VOCAB_PATH
from tone.tone_predict import TonePredictor

description = """
# API sửa lỗi chính tả (bản TEST)
"""

app = FastAPI(
    title="Spell Correction",
    description=description,
    version="0.0.1"
)

class Request(BaseModel):
    text: str
    

# Sửa lỗi teencode
@app.post("/correct-teencode")
def teencode(data: Request):
    data = data.dict()
    corrected, _ = correct_teencode_lm(data["text"])
    return {
        "result": {
            "text": corrected,
            "score": kenlm_model.score(corrected.lower())
        }
    }

# Sửa lỗi telex
@app.post("/correct-telex")
def telex(data: Request):
    data = data.dict()
    corrected = telex.fix_telex_sentence(data["text"])
    # corrected = fix_telex_sentence(data['text'])
    return {
        "result": {
            "text": corrected,
            "score": kenlm_model.score(corrected.lower())
        }
    }

# sửa lỗi viết tắt
@app.post("/correct-short")
def accent(data: Request):
    data = data.dict()
    corrected, lm_scores = correct_short_word_sent_lm(data["text"])
    return {
        "result": {
            "text": corrected,
            "score": sorted(lm_scores, key=lambda d: d['score'], reverse=True)
        }
    }

# gồm sửa lỗi viết tắt, telex, teencode
@app.post("/correct-sentence")
def correct_sentence(data: Request):
    data = data.dict()
    sent = data["text"]

    sent, _ = correct_teencode_lm(sent)
    corrected = telex.fix_telex_sentence(sent)
    return {
        "result": {
            "text": corrected,
            "score": kenlm_model.score(corrected.lower())
        }
    }

# Autocorrection
@app.post("/auto-correction")
def correct_sentence(data: Request):
    data = data.dict()
    sent = data["text"]
    sent = preprocess(sent)
    try:
        corrected = autocorrection.correction(sent)
    except:
        corrected = sent
    corrected = processing_after(corrected)
    return {
        "result": {
            "text": corrected,
            "score": kenlm_model.score(corrected.lower())
        }
    }

# Spell correct
@app.post("/spell-correct")
def correct_sentence(data: Request):
    data = data.dict()
    sent_input = data["text"].lower()

    sent_processed = preprocess(sent_input)

    ### TELEX
    sent_telex = fix_telex_sentence(sent_processed)
    # sent_telex = telex.fix_telex_sentence(sent_processed)

    ### SHORT WORD
    sent_short_word, lm_scores_short_word = correct_teencode_lm(sent_telex)

    # try:
    #     sent_corrector = autocorrection.correction(sent_short_word)
    # except:
    #     sent_corrector = sent_short_word
    sent_corrector = sent_short_word

    ### ADD TONE
    # remove tone
    sent_remove_tone = unidecode.unidecode(sent_corrector)
    # add tone
    sent_tone_added = tonePredictor.predict_line([sent_remove_tone])
    sent_tone_added = tonePredictor.match_tone(sent_tone_added, sent_corrector)

    sent_max_lm_score = sent_tone_added if kenlm_model.score(sent_tone_added.lower()) > kenlm_model.score(sent_corrector.lower()) else sent_corrector

    ### CLOSE CHARACTER
    # sent_max_lm_score = correct_close_character_sent_lm(sent_max_lm_score)

    result = sent_max_lm_score if kenlm_model.score(sent_tone_added.lower()) >= LM_THRESHOLD else sent_corrector


    ### SHORT WORD
    result, _ = correct_teencode_lm(result)
    result = processing_after(result)

    # match punct and match case
    # try:
    #     sent_processed_punct = preprocess(sent_input, remove_punct=False)
    #     result = match_punct(result, sent_processed_punct)
    # except:
    #     result = result
    # result = match_case(sent_processed_punct, result)

    return {
        "result": {
            "text": result,
            "score": kenlm_model.score(result.lower())
        },
        "input_text": {
            "text": sent_input,
            "score": kenlm_model.score(sent_processed.lower())
        },
        "telex": {
            "text": sent_telex,
            "score": kenlm_model.score(sent_telex.lower())
        },
        "short_word_replace": sorted(lm_scores_short_word, key=lambda d: d['score'], reverse=True),
        'tone_added': {
            'text': processing_after(sent_tone_added),
            'score': kenlm_model.score(sent_tone_added.lower())
        }
    }


if __name__ == "__main__":
    tonePredictor = TonePredictor(SRC_VOCAB_PATH, TGT_VOCAB_PATH, MODEL_PATH, WLM_PATH)
    kenlm_model = kenlm.Model(WLM_PATH)
    telex = TelexErrorCorrector()
    autocorrection = AutoCorrection(model_name=MODEL_NAME)
    uvicorn.run(app, host="0.0.0.0", port=8080)
    
    