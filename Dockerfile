FROM python:3.7

WORKDIR /fastapi-spell

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN apt-get -y update && apt-get -y install nano

RUN pip install transformers

RUN pip install unidecode pandas numpy nltk dill

RUN pip install fastapi uvicorn[standard]

RUN pip install underthesea

RUN pip install https://github.com/kpu/kenlm/archive/master.zip

RUN pip install fasttext

RUN pip install visen

RUN pip install tensorflow

RUN pip install torch torchtext

COPY . .

RUN mkdir -p tone/weights/

RUN mkdir -p autocorrection/weights/

EXPOSE 8080

CMD ["python", "app.py"]