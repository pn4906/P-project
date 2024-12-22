from transformers import ElectraTokenizer, TFAutoModel
import tensorflow as tf
import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os

# === 1. Ai 모델로 각 리뷰의 키워드 및 긍*부정 산출  ===

# GPU 장치 확인
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"GPUs available: {len(gpus)}")
    for gpu in gpus:
        print("GPU:", gpu)
else:
    print("No GPU available. Using CPU.")

# KoELECTRA 모델과 토크나이저 로드
model_name = "monologg/koelectra-small-discriminator"
tokenizer = ElectraTokenizer.from_pretrained(model_name)
electra_model = TFAutoModel.from_pretrained(model_name, from_pt=True) 

# 데이터 로드
file_path = "/home/t24329/ai/sentiment/data/m_train_data.csv"
data_df = pd.read_csv(file_path)

# 데이터 정렬 함수
def align_labels_with_subwords(words, sentiments, aspects, tokenizer):
    input_ids = []
    sentiment_labels = []
    aspect_labels = []
    
    # [CLS] 토큰 추가
    input_ids.append(tokenizer.cls_token_id)
    sentiment_labels.append("O")
    aspect_labels.append("O")
    
    for word, sentiment, aspect in zip(words, sentiments, aspects):
        subwords = tokenizer.tokenize(word)
        subword_ids = tokenizer.convert_tokens_to_ids(subwords)
        input_ids.extend(subword_ids)
        
        sentiment_labels.append(sentiment)
        aspect_labels.append(aspect)
        
        for _ in range(1, len(subwords)):
            sentiment_labels.append("I-" + sentiment[2:] if sentiment != "O" else "O")
            aspect_labels.append("I-" + aspect[2:] if aspect != "O" else "O")
    
    # [SEP] 토큰 추가
    input_ids.append(tokenizer.sep_token_id)
    sentiment_labels.append("O")
    aspect_labels.append("O")
    
    return input_ids, sentiment_labels, aspect_labels

# 데이터 전처리
max_len = 128
data = []

current_sentence = None
current_words, current_sentiments, current_aspects = [], [], []

for i in range(len(data_df)):
    sentence = data_df["Sentence #"].iloc[i]
    word = data_df["Word"].iloc[i]
    sentiment = data_df["Sentiment"].iloc[i]
    aspect = data_df["Aspect"].iloc[i]

    if sentence != current_sentence:
        if current_sentence is not None:
            aligned_input_ids, aligned_sentiments, aligned_aspects = align_labels_with_subwords(
                current_words, current_sentiments, current_aspects, tokenizer)
            data.append({
                "sentence": current_sentence,
                "input_ids": aligned_input_ids,
                "sentiments": aligned_sentiments,
                "aspects": aligned_aspects
            })
        current_sentence = sentence
        current_words, current_sentiments, current_aspects = [], [], []

    current_words.append(word)
    current_sentiments.append(sentiment)
    current_aspects.append(aspect)

if current_sentence is not None:
    aligned_input_ids, aligned_sentiments, aligned_aspects = align_labels_with_subwords(
        current_words, current_sentiments, current_aspects, tokenizer)
    data.append({
        "sentence": current_sentence,
        "input_ids": aligned_input_ids,
        "sentiments": aligned_sentiments,
        "aspects": aligned_aspects
    })

# 데이터 패딩 및 라벨 인코딩
input_ids = [d["input_ids"] for d in data]
input_ids_padded = pad_sequences(input_ids, padding="post", maxlen=max_len)

unique_sentiments = list(set(l for d in data for l in d["sentiments"]))
sentiment2idx = {s: i for i, s in enumerate(unique_sentiments)}

sentiments = [[sentiment2idx[l] for l in d["sentiments"]] for d in data]
sentiments_padded = pad_sequences(sentiments, padding="post", maxlen=max_len, value=-1)
sentiments_categorical = np.array([
    tf.keras.utils.to_categorical(seq, num_classes=len(unique_sentiments)) for seq in sentiments_padded
])

unique_aspects = list(set(l for d in data for l in d["aspects"]))
aspect2idx = {a: i for i, a in enumerate(unique_aspects)}

aspects = [[aspect2idx[l] for l in d["aspects"]] for d in data]
aspects_padded = pad_sequences(aspects, padding="post", maxlen=max_len, value=-1)
aspects_categorical = np.array([
    tf.keras.utils.to_categorical(seq, num_classes=len(unique_aspects)) for seq in aspects_padded
])

# 모델 구축
input_ids_layer = tf.keras.Input(shape=(max_len,), dtype=tf.int32, name="input_ids")
attention_mask_layer = tf.keras.Input(shape=(max_len,), dtype=tf.int32, name="attention_mask")

electra_output = electra_model(input_ids=input_ids_layer, attention_mask=attention_mask_layer)
cls_token_output = electra_output.last_hidden_state

sentiment_output = tf.keras.layers.Dense(len(unique_sentiments), activation="softmax", name="sentiment_output")(cls_token_output)
aspect_output = tf.keras.layers.Dense(len(unique_aspects), activation="softmax", name="aspect_output")(cls_token_output)

model = tf.keras.Model(
    inputs=[input_ids_layer, attention_mask_layer],
    outputs=[sentiment_output, aspect_output]
)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=5e-5),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# 모델 학습
attention_mask = (input_ids_padded != 0).astype(int)

history = model.fit(
    {"input_ids": input_ids_padded, "attention_mask": attention_mask},
    {"sentiment_output": sentiments_categorical, "aspect_output": aspects_categorical},
    batch_size=32,
    epochs=5,
    validation_split=0.1
)

from sklearn.metrics import classification_report, accuracy_score
import numpy as np

# 예측 수행
predictions = model.predict({"input_ids": input_ids_padded, "attention_mask": attention_mask})
sentiment_preds = np.argmax(predictions[0], axis=-1)  # Sentiment 예측값
aspect_preds = np.argmax(predictions[1], axis=-1)    # Aspect 예측값

# 실제 값 (패딩 제외)
sentiment_true = np.argmax(sentiments_categorical, axis=-1)
aspect_true = np.argmax(aspects_categorical, axis=-1)

# 패딩 값과 I- 값 제거를 위한 함수
def filter_b_labels(true, preds, label_names):
    true_labels = []
    pred_labels = []
    for t_seq, p_seq in zip(true, preds):
        for t, p in zip(t_seq, p_seq):
            if t != -1 and label_names[t].startswith("B-"):  # 패딩과 I- 값 무시
                true_labels.append(label_names[t])
                pred_labels.append(label_names[p])
    return true_labels, pred_labels

# B-로 시작하는 라벨만 필터링
sentiment_true_filtered, sentiment_preds_filtered = filter_b_labels(sentiment_true, sentiment_preds, unique_sentiments)
aspect_true_filtered, aspect_preds_filtered = filter_b_labels(aspect_true, aspect_preds, unique_aspects)

# Sentiment 성능 지표 (B-만)
print("감성(긍부정) 성능 지표 : ")
print(classification_report(sentiment_true_filtered, sentiment_preds_filtered, zero_division=0))

# Aspect 성능 지표 (B-만)
print("카테고리 성능 지표 :")
print(classification_report(aspect_true_filtered, aspect_preds_filtered, zero_division=0))

# 정확도 출력
print("Sentiment Accuracy (B- labels only):", accuracy_score(sentiment_true_filtered, sentiment_preds_filtered))
print("Aspect Accuracy (B- labels only):", accuracy_score(aspect_true_filtered, aspect_preds_filtered))





# ===================================================================

# # 크롤링으로 추출한 리뷰들 
# # CSV 파일 읽기
# folder_path = "/home/t24329/ai/final/data/Musinsa/reviews"
# file_encoding = 'utf-8-sig'  # 파일 인코딩

# # 토크나이저 및 모델 정의
# # tokenizer, model은 이미 불러왔다고 가정
# max_len = 128  # max_len은 적절히 설정된 값

# # 카테고리 정의
# categories = ["사이즈", "디자인", "품질", "기능성/편의성", "가격"]

# for file_name in os.listdir(folder_path):
#     if file_name.endswith(".csv"):
#         file_path = os.path.join(folder_path, file_name)
#         print(f"처리 중: {file_path}")

#         # CSV 파일 읽기
#         test_df = pd.read_csv(file_path, encoding=file_encoding)

#         # 테스트할 문장들
#         test_sentences = test_df['리뷰본문'].tolist()

#         # 토크나이저로 문장 인코딩
#         test_encoded_inputs = tokenizer(
#             test_sentences,
#             padding="max_length",
#             truncation=True,
#             max_length=max_len,
#             return_tensors="tf"
#         )

#         test_input_ids = test_encoded_inputs["input_ids"]
#         test_attention_mask = test_encoded_inputs["attention_mask"]

#         # 모델 예측
#         test_predictions = model.predict({"input_ids": test_input_ids, "attention_mask": test_attention_mask})

#         # 결과 디코딩
#         test_sentiment_preds = test_predictions[0]  # 긍정/부정 예측
#         test_aspect_preds = test_predictions[1]  # 속성 예측

#         # ======================================================

#         # 레이블 처리

# category_labels = []
# sentiment_overall = []  # '긍부정' 카테고리 저장 리스트
# len_category = [] 
# for i, sentence in enumerate(test_sentences):
#     valid_token_mask = test_attention_mask.numpy()[i] == 1

#     # Sentiments and Aspects
#     sentiment_result = [
#         unique_sentiments[np.argmax(s)] for s, valid in zip(test_sentiment_preds[i], valid_token_mask) if valid
#     ]
#     aspect_result = [
#         unique_aspects[np.argmax(a)] for a, valid in zip(test_aspect_preds[i], valid_token_mask) if valid
#     ]

#     # 카테고리 초기화
#     category_values = {cat: 0 for cat in categories}

#     # 매핑 및 레이블링
#     b_positive_count = 0
#     b_negative_count = 0

#     for aspect, sentiment in zip(aspect_result, sentiment_result):
#         # "B-"와 "I-" 접두사 제거
#         clean_aspect = aspect.split("-")[-1]
#         sentiment_type = sentiment.split("-")[-1]  # 긍정, 부정, 중립 추출

#         # B-긍정 및 B-부정 카운트
#         if sentiment.startswith("B-"):
#             if sentiment_type == "긍정":
#                 b_positive_count += 1
#             elif sentiment_type == "부정":
#                 b_negative_count += 1

#         # Aspect가 categories에 포함된 경우에만 처리
#         if clean_aspect in categories:
#             if sentiment_type == "긍정":
#                 category_values[clean_aspect] = 1
#             elif sentiment_type == "부정":
#                 category_values[clean_aspect] = 2

#     category_label = "".join(str(category_values.get(cat, 0)) for cat in categories)
#     category_labels.append(category_label)

#     # '긍부정' 값 계산 (B-긍정 vs B-부정)
#     if b_positive_count > b_negative_count:
#         sentiment_overall.append(1)  # 긍정
#     elif b_negative_count > b_positive_count:
#         sentiment_overall.append(2)  # 부정
#     else:
#         sentiment_overall.append(0)  # 중립

# # 데이터프레임에 새로운 컬럼 추가
# test_df['Category'] = category_labels
# test_df['긍부정'] = sentiment_overall

# # 저장 (덮어쓰기)
# test_df.to_csv(file_path, index=False, encoding=file_encoding)
# print(f"저장 완료: {file_path}")

