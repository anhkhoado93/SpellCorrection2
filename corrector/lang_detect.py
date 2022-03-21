import fasttext
fasttext.FastText.eprint = lambda x: None

class LanguageDetection:

    def __init__(self):
        pretrained_lang_model = "corrector/fasttext_models/lid.176.ftz"
        self.model = fasttext.load_model(pretrained_lang_model)

    def predict(self, text, k=1):
        prediction, score = self.model.predict(text, k=k)
        return prediction, score

    def predict_label(self, text):
        prediction, score = self.model.predict(text, k=1)

        if score[0] < 0.5:
            prediction = [('__label__unk')]

        return prediction[0]