import pandas as pd

# === 4. 각 상품별 긍정 비율 산출 === 

# 파일 경로 설정
file_path = "/home/t24329/ai/final/data/Musinsa/products/products.csv"

# CSV 파일 읽기
df = pd.read_csv(file_path)

# 결측값 처리: 긍정 리뷰 개수와 부정 리뷰 개수의 결측값을 0으로 설정
df['긍정 리뷰 개수'] = df['긍정 리뷰 개수'].fillna(0).astype(int)
df['부정 리뷰 개수'] = df['부정 리뷰 개수'].fillna(0).astype(int)

# 긍정 비율 계산: 분모가 0일 경우 0으로 처리, 반올림 후 정수로 변환
df['긍정 비율'] = df.apply(
    lambda row: round(row['긍정 리뷰 개수'] / (row['긍정 리뷰 개수'] + row['부정 리뷰 개수']) * 100) 
    if (row['긍정 리뷰 개수'] + row['부정 리뷰 개수']) > 0 else 0, axis=1
).astype(int)

# 새로운 데이터프레임 확인
print(df[['긍정 리뷰 개수', '부정 리뷰 개수', '긍정 비율']])

# 변경된 내용을 동일 파일에 저장
df.to_csv(file_path, index=False, encoding='utf-8-sig')
print("소수점 반올림된 긍정 비율(INT) 열이 추가된 CSV 파일이 저장되었습니다.")
