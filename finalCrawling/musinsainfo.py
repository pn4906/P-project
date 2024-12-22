import pandas as pd  # CSV 저장을 위한 pandas 임포트
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os  # 폴더 생성 및 경로 작업을 위한 모듈
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 크롬 드라이버 실행 (GPU 활성화 및 헤드리스 모드 설정)
options = Options()
options.add_argument('--headless')  # GUI 없이 실행
options.add_argument('--use-gl=desktop')  # GPU 렌더링 활성화
options.add_argument('--enable-gpu')  # GPU 사용 명시적 활성화
options.add_argument('--enable-logging')  # 디버그 로그 활성화
options.add_argument('--v=1')  # 디버그 레벨 로그
options.add_argument('--no-sandbox')  # 샌드박스 비활성화
options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 비활성화
options.binary_location = "/home/t24329/chrome/opt/google/chrome/google-chrome"  # Chrome 실행 경로

# ChromeDriver 경로 설정
driver_service = Service("/home/t24329/chrome/chromedriver")

# WebDriver 초기화
driver = webdriver.Chrome(service=driver_service, options=options)

try:
    # 1. 카테고리 리스트 정의 (URL 순차 크롤링)
    category_urls = {
        'https://www.musinsa.com/category/002?gf=M': 'mumouter.csv',  # 아우터
        'https://www.musinsa.com/category/001?gf=M': 'mumtop.csv',  # 상의
        'https://www.musinsa.com/category/003?gf=M': 'mumpants.csv',  # 바지

        'https://www.musinsa.com/category/002?gf=F': 'muwouter.csv',  # 아우터
        'https://www.musinsa.com/category/001?gf=F': 'muwtop.csv',  # 상의
        'https://www.musinsa.com/category/003?gf=F': 'muwpants.csv',  # 바지
    }

    # 데이터 수집을 위한 변수
    MAX_PRODUCTS = 100  # 각 카테고리별 최대 상품 수
    prev_product_count = 0
    MAX_RETRIES = 5  # 최대 스크롤 시도 횟수
    retry_count = 0  # 현재 시도 횟수

    # `newmu` 폴더가 없다면 생성
    if not os.path.exists('newmu'):
        os.makedirs('newmu')

    # 각 카테고리별로 크롤링 진행
    for category_url, file_name in category_urls.items():
        print(f"카테고리 크롤링 시작: {category_url}")
        driver.get(category_url)
        time.sleep(3)

        total_products = []  # 카테고리별 상품 데이터

        # URL에서 성별 추출 (gf=M이면 남성, gf=F이면 여성)
        gender = 'M' if 'gf=M' in category_url else 'F'  # URL에서 성별 추출

        # URL에서 카테고리 코드 추출
        category_code = category_url.split('/category/')[1].split('?')[0]
        category_name = {
            '002': '아우터',
            '001': '상의',
            '003': '바지'
        }.get(category_code, '기타')  # 카테고리 코드에 맞는 카테고리명 추출

        while retry_count < MAX_RETRIES and len(total_products) < MAX_PRODUCTS:
            # 현재 화면에 있는 상품 요소들 수집
            product_containers_xpath = '//*[@id="commonLayoutContents"]/div[3]/div/div/div/div'
            product_containers = driver.find_elements(By.XPATH, product_containers_xpath)

            for container in product_containers:
                try:
                    # 상품 이미지 경로
                    product_image_xpath = './/div[1]/div/a/div/img'
                    product_image = container.find_element(By.XPATH, product_image_xpath).get_attribute("src")

                    # 상품 이름 (상품이 없으면 건너뛰기)
                    product_name_xpath = './/div[2]/div/div[1]/a[2]/span'
                    try:
                        product_name = container.find_element(By.XPATH, product_name_xpath).text.strip()
                        if not product_name:  # 이름이 비어있는 경우
                            continue  # 해당 상품 건너뛰기
                    except Exception:
                        continue  # 이름을 찾지 못하면 건너뛰기

                    # 상품 가격 (WebDriverWait 적용)
                    try:
                        product_price_xpath = './/div[2]/div/div[1]/div/span[2]'
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, product_price_xpath))
                        )
                        product_price = container.find_element(By.XPATH, product_price_xpath).text.strip()
                    except Exception:
                        product_price = "가격 정보 없음"  # 가격이 없을 경우 기본값 설정

                    # 할인율
                    discount_xpath = './/div[2]/div/div[1]/div/span[1]'
                    try:
                        discount = container.find_element(By.XPATH, discount_xpath).text.strip()
                    except Exception:
                        discount = "할인 없음"

                    # 상품 상세 페이지 경로
                    product_detail_xpath = './/div[1]/div/a'
                    product_detail_link = container.find_element(By.XPATH, product_detail_xpath).get_attribute("href")

                    # 상품 ID 추출 (URL에서 ID만 가져옴)
                    product_id = product_detail_link.split('/')[-1]

                    # 브랜드명
                    brand_xpath = './/div[2]/div/div[1]/a[1]/span'
                    try:
                        brand = container.find_element(By.XPATH, brand_xpath).text.strip()
                    except Exception:
                        brand = "정보 없음"

                    # 플랫폼명 및 카테고리
                    platform = "musinsa"

                    # 중복 제거
                    if product_id not in [prod['상품ID'] for prod in total_products]:
                        total_products.append({
                            '상품명': product_name,
                            '상품가격': product_price,
                            '이미지경로': product_image,
                            '상품ID': product_id,
                            '할인율': discount,
                            '성별': gender,
                            '브랜드': brand,
                            '플랫폼': platform,
                            '카테고리': category_name,
                            '상품상세페이지 링크': product_detail_link  # 상세페이지 링크 추가
                        })
                except Exception as e:
                    print(f"오류 발생: {e}")
                    continue

                # 상품이 300개를 초과하면 종료
                if len(total_products) >= MAX_PRODUCTS:
                    print("상품 300개를 초과하여 수집을 중단합니다.")
                    break

            # 상품이 300개를 초과하면 종료
            if len(total_products) >= MAX_PRODUCTS:
                break

            # 현재까지 로드된 상품 수 출력
            print(f"현재까지 로드된 상품 개수: {len(total_products)}")

            # 스크롤 다운
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.END)
            time.sleep(3)  # 스크롤 후 로딩 시간 대기

            # 새로운 상품이 더 이상 로드되지 않으면 종료
            if len(total_products) == prev_product_count:
                retry_count += 1  # 새로운 상품이 없으면 시도 횟수 증가
                print(f"새로운 상품이 없습니다. 재시도 {retry_count}/{MAX_RETRIES}")
            else:
                retry_count = 0  # 새로운 상품이 로드되면 시도 횟수 초기화

            prev_product_count = len(total_products)

        # 시도 횟수 초과 시 종료
        if retry_count >= MAX_RETRIES:
            print("최대 시도 횟수를 초과하여 종료합니다.")

        # 데이터 저장: 각 카테고리별로 `newmu` 폴더에 CSV로 저장
        file_path = f'newmu/{file_name}'  # 새로운 폴더 'newmu' 안에 저장
        products_df = pd.DataFrame(total_products)
        products_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"데이터가 '{file_path}' 파일로 저장되었습니다.")

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    driver.quit()