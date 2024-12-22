import os
import pandas as pd

# ===== 2. 각 상품별 긍부정 리뷰 개수 산출 ===== 


# 고정된 파일 경로 설정
review_path = "/home/t24329/ai/final/data/Musinsa/reviews/reviews.csv"
product_path = "/home/t24329/ai/final/data/Musinsa/products/products.csv"

# CSV 파일 읽기
review_df = pd.read_csv(review_path)
product_df = pd.read_csv(product_path)

# 리뷰 개수를 상품ID 기준으로 집계
review_counts = review_df.groupby("상품ID").size().reset_index(name="리뷰 개수")


# 긍정, 부정 리뷰 개수 계산
positive_negative_counts = review_df.groupby(["상품ID", "긍부정"]).size().unstack(fill_value=0)
positive_negative_counts = positive_negative_counts.rename(columns={1: "긍정 리뷰 개수", 2: "부정 리뷰 개수"}).reset_index()

# product_df에서 기존 리뷰 개수 열 제거
product_df = product_df.drop(columns=["리뷰개수","0","1","리뷰 개수", "긍정 리뷰 개수", "부정 리뷰 개수"], errors="ignore")

# product_df와 리뷰 개수 결합
updated_df = product_df.merge(review_counts, on="상품ID", how="left")
updated_df = updated_df.merge(positive_negative_counts, on="상품ID", how="left")

# 결측값을 0으로 대체
updated_df["리뷰 개수"] = updated_df["리뷰 개수"].fillna(0).astype(int)
updated_df["긍정 리뷰 개수"] = updated_df["긍정 리뷰 개수"].fillna(0).astype(int)
updated_df["부정 리뷰 개수"] = updated_df["부정 리뷰 개수"].fillna(0).astype(int)

# 결과 저장
updated_df.to_csv(product_path, index=False, encoding='utf-8-sig')
print(f"업데이트된 파일이 저장되었습니다: {product_path}")
