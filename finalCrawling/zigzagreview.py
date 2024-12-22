import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

# 크롬 드라이버 실행 설정
options = Options()
options.add_argument('--headless')  # 브라우저를 띄우지 않음
options.add_argument('--use-gl=desktop')  # GPU 렌더링 활성화
options.add_argument('--no-sandbox')  # 샌드박스 비활성화 (Linux에서 권장)
options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 사용 비활성화 (Linux에서 권장)

# Chrome 경로 및 ChromeDriver 경로 설정
options.binary_location = "/home/t24329/chrome/opt/google/chrome/google-chrome"  # Chrome 실행 파일 경로
driver_service = Service("/home/t24329/chrome/chromedriver")  # ChromeDriver 실행 파일 경로

driver = webdriver.Chrome(service=driver_service, options=options)

# CSV 파일에서 상품 ID 읽기 및 출력
def read_product_ids_from_csv(file_paths):
    product_ids = []
    for csv_file in file_paths:
        try:
            print(f"CSV 파일 `{csv_file}`을(를) 열고 상품 ID를 가져왔습니다.")
            data = pd.read_csv(csv_file)
            product_ids.extend(data.iloc[:, 0].dropna().astype(str).tolist())  # 첫 번째 열에서 상품 ID 가져오기
        except Exception as e:
            print(f"CSV 파일 {csv_file} 읽기 중 오류 발생: {e}")
    return product_ids

# 리뷰 크롤링 함수
def crawl_reviews(product_id, max_reviews=3000):
    reviews = []
    url = f"https://zigzag.kr/review/list/{product_id}"
    driver.get(url)

    print(f"[상품 ID: {product_id}] 리뷰 크롤링 시작")

    review_count = 0
    while review_count < max_reviews:
        # 리뷰 컨테이너 접근
        review_containers = driver.find_elements(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[2]/div/div')

        if not review_containers:
            print(f"[상품 ID: {product_id}] 더 이상 리뷰가 없습니다.")
            break

        for container in review_containers:
            if review_count >= max_reviews:
                break

            try:
                # 작성자 정보
                author_elements = container.find_elements(By.XPATH, './div[1]/div[1]/div[1]/div[2]/p')
                author = author_elements[0].text if author_elements else "작성자 정보 없음"

                # 별점 계산
                empty_stars = len(container.find_elements(By.XPATH, './div[1]/div[1]/div[2]/div[1]/div/div/svg/path[@fill="none"]'))
                rating = 5 - empty_stars  # 전체 별 5개에서 빈 별 개수 차감

                # 작성 날짜
                date_elements = container.find_elements(By.XPATH, './div[1]/div[1]/div[2]/div[2]/span[2]')
                date = date_elements[0].text if date_elements else "작성 날짜 없음"

                # 리뷰 본문
                review_text_elements = container.find_elements(By.XPATH, './div[1]/div[3]/span')

                # "더보기" 버튼이 있을 경우 클릭하여 본문 확장
                more_button = container.find_elements(By.XPATH, './/span[contains(text(), "더보기")]')
                if more_button:
                    more_button[0].click()
                    time.sleep(1)
                    review_text_elements = container.find_elements(By.XPATH, './div[1]/div[3]/span')

                review_text = review_text_elements[0].text if review_text_elements else "리뷰 내용 없음"

                # 리뷰 저장
                reviews.append({
                    '상품 ID': product_id,
                    '작성자': author,
                    '별점': rating,
                    '작성 날짜': date,
                    '리뷰 본문': review_text
                })

                review_count += 1
                print(f"[상품 ID: {product_id}] 리뷰 {review_count}개 수집 완료.")

            except Exception as e:
                print(f"[상품 ID: {product_id}] 리뷰 데이터 수집 중 오류 발생: {e}")

        # 스크롤을 내려서 추가 리뷰 로드
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)

    return reviews

# 크롤링 결과를 CSV로 저장
def save_reviews_to_csv(reviews, output_file):
    if reviews:
        df = pd.DataFrame(reviews)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"[저장 완료] 리뷰 데이터가 {output_file}에 저장되었습니다.")
    else:
        print(f"[저장 실패] 리뷰 데이터가 없어 {output_file}에 저장되지 않았습니다.")

# 실행 흐름
if __name__ == "__main__":
    csv_files = [
        "zigzagouter_updated.csv",
        "zigzagpants_updated.csv",
        "zigzagshoes_updated.csv",
        "zigzagskirt_updated.csv",
        "zigzagtop_updated.csv"
    ]
    
    for csv_file in csv_files:
        try:
            product_ids = read_product_ids_from_csv([csv_file])  # CSV에서 상품 ID 읽기
            all_reviews = []  # 동일 파일의 모든 리뷰를 저장

            for product_id in product_ids:
                reviews = crawl_reviews(product_id, max_reviews=200)  # 상품 리뷰 크롤링 (최대 500개)
                all_reviews.extend(reviews)  # 동일 CSV의 모든 리뷰를 저장

            # CSV 파일명에 `_review` 추가하여 저장
            review_file = csv_file.replace(".csv", "_review.csv")
            save_reviews_to_csv(all_reviews, review_file)  # 동일 파일의 리뷰를 저장

        except Exception as e:
            print(f"[파일 처리 오류] {csv_file}: {e}")
    
    print("모든 크롤링 작업이 완료되었습니다.")
    driver.quit()