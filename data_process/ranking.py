import os
import numpy as np
import pandas as pd

# 3. 리뷰 랭킹 점수 계산 파일 

def review_function(x):
    if 0 <= x <= 100:
        return 3 * np.log(x + 1) / np.log(3)
    elif 100 < x <= 1000:
        return 2 * np.sqrt(x / 10) + 6.28
    elif x >= 1000:
        return 20 * np.log10(x) - 33.72
    else:
        raise ValueError("x must be greater than 0.")

# 폴더 경로
folder_path = '/home/t24329/ai/final/data/Musinsa/products'

# 폴더 내 모든 CSV 파일 처리
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):  # CSV 파일만 처리
        file_path = os.path.join(folder_path, file_name)
        print(f"처리 중: {file_path}")

        # 파일 읽기
        df = pd.read_csv(file_path)
        # '리뷰개수' 열에서 '리뷰 없음'을 0으로 변환하고 데이터 타입을 int로 변경
        df['리뷰 개수'] = df['리뷰 개수'].replace('리뷰 없음', 0).astype(int)
        # 리뷰 랭킹 점수 계산   

        reviews_score = df['리뷰 개수'].astype(int).apply(review_function)

        # 긍정 비율 계산
        positive = df['긍정 리뷰 개수']
        negative = df['부정 리뷰 개수']
        total_reviews = positive + negative
        positive_score = (positive / total_reviews).fillna(0)  # NaN 처리

        # 랭킹 점수 계산
        df['랭킹 점수'] = ((reviews_score * 0.8) + (positive_score * 100 * 0.2)).round(2)

        # 데이터 확인용 출력
        show_df = df[['상품명', '리뷰 개수', '긍정 리뷰 개수', '부정 리뷰 개수', '랭킹 점수']]
        print(show_df.head())

        # 원본 파일 저장 (업데이트된 데이터 포함)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"업데이트된 파일이 저장되었습니다: {file_path}")
