from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

# GPU 사용 및 Chrome 경로 설정
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # 백그라운드 실행
options.add_argument("--no-sandbox")   # 샌드박스 비활성화
options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 비활성화
options.add_argument("--enable-webgl")  # WebGL 활성화
options.add_argument("--disable-software-rasterizer")  # 소프트웨어 렌더링 비활성화
options.add_argument("--use-gl=desktop")  # GPU 렌더링 사용
options.binary_location = "/home/t24329/chrome/opt/google/chrome/google-chrome"  # Chrome 실행 파일 경로
driver_service = Service("/home/t24329/chrome/chromedriver")  # ChromeDriver 실행 파일 경로

# 크롬 드라이버 초기화
driver = webdriver.Chrome(service=driver_service, options=options)
def scrape_reviews(file_path):
    # CSV 파일 읽기
    data = pd.read_csv(file_path)
    
    if '상품ID' not in data.columns:
        print(f"'{file_path}'에 '상품ID' 열이 없습니다.")
        return
    
    review_counts = []

    for idx, product_id in enumerate(data['상품ID']):
        try:
            product_url = f"https://zigzag.kr/catalog/products/{product_id}"
            driver.get(product_url)
            time.sleep(2)

            # 여러 XPath 시도
            review_xpaths = [
                '//*[@id="__next"]/div[1]/div/div[5]/span',
                '//*[@id="__next"]/div[1]/div/div[4]/span'
            ]
            
            total_reviews = 0
            for xpath in review_xpaths:
                try:
                    review_button = driver.find_element(By.XPATH, xpath)
                    total_reviews_text = review_button.text
                    total_reviews = int(''.join(filter(str.isdigit, total_reviews_text)))
                    break  # 리뷰 버튼을 찾으면 루프 종료
                except:
                    continue
            
            if total_reviews == 0:
                print(f"[상품 ID: {product_id}] 리뷰 버튼을 찾지 못했습니다.")
            
            print(f"[상품 ID: {product_id}] 리뷰 개수: {total_reviews}")
            review_counts.append(total_reviews)

        except Exception as e:
            print(f"[상품 ID: {product_id}] 크롤링 실패: {e}")
            review_counts.append(0)

    # 결과 저장
    data['리뷰개수'] = review_counts
    output_file_path = file_path.replace('.csv', '_updated.csv')
    data.to_csv(output_file_path, index=False)
    print(f"크롤링 완료: {output_file_path}")

# 사용 예시
csv_files = ["zigzagouter.csv", "zigzagpants.csv", "zigzagshoes.csv", "zigzagskirt.csv", "zigzagtop.csv"]
for file in csv_files:
    scrape_reviews(file)

# 크롤링 완료 후 드라이버 종료
driver.quit()