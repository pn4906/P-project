import pandas as pd  # CSV 저장을 위한 pandas 임포트
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import os  # 폴더 경로 작업을 위한 모듈

# 크롬 드라이버 실행 (헤드리스 모드 및 GPU 활성화)
options = Options()
options.add_argument('--headless')  # 브라우저를 띄우지 않음
options.add_argument('--use-gl=desktop')  # GPU 렌더링 활성화
options.add_argument('--enable-gpu')  # GPU 사용 명시적 활성화
options.add_argument('--disable-gpu')  # GPU 비활성화 (Windows에서 필수)
options.add_argument('--no-sandbox')  # 샌드박스 비활성화 (Linux에서 권장)
options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 사용 비활성화 (Linux에서 권장)

# Chrome 경로 및 ChromeDriver 경로 설정
options.binary_location = "/home/t24329/chrome/opt/google/chrome/google-chrome"  # Chrome 실행 경로
driver_service = Service("/home/t24329/chrome/chromedriver")  # ChromeDriver 경로

# WebDriver 초기화
driver = webdriver.Chrome(service=driver_service, options=options)

# `newmu` 폴더 내 모든 CSV 파일 읽기
try:
    # newmu 폴더 내의 CSV 파일 목록을 가져오기
    csv_folder_path = '/home/t24329/chrome/newmu'
    csv_files = [f for f in os.listdir(csv_folder_path) if f.endswith('.csv')]  # `.csv` 파일만 필터링

    if not csv_files:
        print("`newmu` 폴더에 CSV 파일이 없습니다.")
    
    # 각 CSV 파일 처리
    for file_name in csv_files:
        file_path = os.path.join(csv_folder_path, file_name)  # 전체 경로 생성
        print(f"CSV 파일 읽기 시작: {file_path}")
        
        # CSV 파일 읽기
        products_df = pd.read_csv(file_path)
        product_ids = products_df['상품ID']  # 상품ID만 가져오기
        print(f"총 {len(product_ids)}개의 상품ID를 읽어왔습니다. ({file_name})")

        # 리뷰 개수를 저장할 리스트
        review_counts = []

        # 각 상품에 대해 반복
        for product_id in product_ids:
            # 상품 상세 페이지 URL 생성
            product_url = f'https://www.musinsa.com/products/{product_id}'
            driver.get(product_url)
            print(f"상품 페이지로 이동 완료! URL: {product_url}")
            time.sleep(3)  # 페이지 로딩 대기

            # 리뷰 개수 추출
            try:
                review_count_elements = driver.find_elements(By.XPATH, '//*[@class="text-xs font-normal cursor-pointer text-gray-600 font-pretendard" and contains(text(), "후기")]')

                if review_count_elements:
                    review_count_text = review_count_elements[0].text.strip()  # 첫 번째 요소에서 텍스트 추출
                    review_count = re.findall(r'\d+', review_count_text)  # 숫자만 추출
                    review_count = review_count[0] if review_count else '0'
                    print(f"[상품ID: {product_id}] 총 리뷰 개수: {review_count}")
                else:
                    review_count = '0'
                    print(f"[상품ID: {product_id}] 리뷰 개수 추출 실패: 리뷰 정보가 없음.")
            except Exception as e:
                review_count = '0'
                print(f"[상품ID: {product_id}] 리뷰 개수 추출 실패: {e}")

            # 결과 리스트에 추가
            review_counts.append({
                '상품ID': product_id,
                '리뷰개수': review_count
            })

        # CSV 파일에 리뷰 개수 추가
        review_count_df = pd.DataFrame(review_counts)
        reviews_df = pd.merge(products_df, review_count_df, on="상품ID", how="left")
        
        # 'newmu' 폴더에 저장
        reviews_df.to_csv(file_path, index=False, encoding='utf-8-sig')  # 리뷰 개수를 추가한 데이터로 덮어쓰기
        print(f"리뷰 개수 데이터가 '{file_path}' 파일에 저장되었습니다.")

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    driver.quit()