# Spell Correction
1. Download pretrained autocorrection weight at [here](https://drive.google.com/file/d/18tK7DKkREuzzcuGARREcgo-lXMLGEDNm/view?usp=sharing) and put at `autocorrection/weights/`
2. Download pretrained tone prediction weight at [here](https://drive.google.com/file/d/17nmXZGM0Qt7Yc6AjOOqeNMw_g1PVB0C4/view?usp=sharing) and put at `tone/weights/`
3. Download pretrained kenlm language model at [here](https://drive.google.com/file/d/1AhrTbhPk62IV0RmiO6cDQFmRisntNvA7/view?usp=sharing) `and put at corrector/lm/`
4. Run API:
```bash
python app.py
```
5. Run Demo page
```bash
streamlit run frontend.py
```
Data for training (Hume) can be download at [here](https://drive.google.com/file/d/1lcJu9a4cTHpXDUuBBgZQ-0ukcJN9AQje/view?usp=sharing)

## Training autocorrection
1. Create data (add noise):
```bash
python autocorrection/generate_dataset/create_data.py\
--file_text=autocorrection/dataset/Data/data_chinh_ta_hume_label_full.txt\
--file_csv=autocorrection/dataset/Data/data_chinh_ta_hume_noise.csv\
--n_sents=500000
```
2. Preprocess data:
```bash
python autocorrection/generate_dataset/preprocess_data.py\
--file_csv=autocorrection/dataset/Data/Hume/data_chinh_ta_hume_noise.csv
```
3. Training model:
```bash
python autocorrection/train.py\
--model_name='trans'
```