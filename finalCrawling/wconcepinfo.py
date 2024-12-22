import pandas as pd  # CSV 저장을 위한 pandas 임포트
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# 크롬 드라이버 설정 (헤드리스 모드, GPU 비활성화)
options = Options()
options.add_argument('--headless')  # GUI 없이 실행
options.add_argument('--disable-gpu')  # GPU 비활성화
options.add_argument('--no-sandbox')  # 샌드박스 비활성화
options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 비활성화
options.binary_location = "/home/t24329/chrome/opt/google/chrome/google-chrome"  # Chrome 실행 파일 경로
driver_service = Service("/home/t24329/chrome/chromedriver")  # 서버 환경에 맞는 ChromeDriver 경로

# WebDriver 초기화
driver = webdriver.Chrome(service=driver_service, options=options)

# 카테고리 URL과 저장할 파일명 매핑
category_urls = {
    'https://display.wconcept.co.kr/category/women/001001': 'wwouter.csv',  # 여성 아우터
    'https://display.wconcept.co.kr/category/women/001004': 'wwtop.csv',  # 여성 상의 블라우스
    'https://display.wconcept.co.kr/category/women/001013': 'wwtop.csv',  # 여성 상의 셔츠
    'https://display.wconcept.co.kr/category/women/001003': 'wwtop.csv',  # 여성 상의 티셔츠
    'https://display.wconcept.co.kr/category/women/001002': 'wwtop.csv',  # 여성 상의 니트
    'https://display.wconcept.co.kr/category/women/001006': 'wwpants.csv',  # 여성 하의 팬츠
    'https://display.wconcept.co.kr/category/women/001007': 'wwpants.csv',  # 여성 하의 스커트
    'https://display.wconcept.co.kr/category/women/002': 'wwshoes.csv',  # 여성 신발
    'https://display.wconcept.co.kr/category/men/001001': 'wmouter.csv',  # 남성 아우터
    'https://display.wconcept.co.kr/category/men/001004': 'wmtop.csv',  # 남성 상의 셔츠
    'https://display.wconcept.co.kr/category/men/001002': 'wmtop.csv',  # 남성 상의 티셔츠
    'https://display.wconcept.co.kr/category/men/001003': 'wmtop.csv',  # 남성 상의 니트
    'https://display.wconcept.co.kr/category/men/001005': 'wmpants.csv',  # 남성 하의
    'https://display.wconcept.co.kr/category/men/002': 'wmshoes.csv',  # 남성 신발
}

# 데이터 수집을 위한 변수
MAX_PRODUCTS = 300  # 각 카테고리별 최대 상품 수
prev_product_count = 0
MAX_RETRIES = 5  # 최대 스크롤 시도 횟수
retry_count = 0  # 현재 시도 횟수

# 각 카테고리별로 크롤링 진행
for category_url, file_name in category_urls.items():
    print(f"카테고리 크롤링 시작: {category_url}")
    driver.get(category_url)
    time.sleep(3)

    total_products = []  # 카테고리별 상품 데이터

    # 성별 추출
    if "women" in category_url:
        gender = "여성"
    else:
        gender = "남성"

    while retry_count < MAX_RETRIES and len(total_products) < MAX_PRODUCTS:
        # 현재 화면에 있는 상품 요소들 수집
        product_containers_xpath = '//*[@id="container"]/div/div/div[2]/div/div/section/div[3]/div/div[1]/div/div[1]'
        product_containers = driver.find_elements(By.XPATH, product_containers_xpath)

        for container in product_containers:
            try:
                # 상품 이름
                name = container.find_element(By.XPATH, './/span/button/span[1]/span[2]').text.strip()

                # 브랜드명
                brand = container.find_element(By.XPATH, './/span/button/span[1]/span[1]').text.strip()

                # 상품 가격
                try:
                    price = container.find_element(By.XPATH, './/span/button/span[2]/span[3]/strong').text.strip()
                except Exception:
                    price = "가격 정보 없음"

                # 할인율
                try:
                    discount = container.find_element(By.XPATH, './/span/button/span[2]/span[2]/em').text.strip()
                except Exception:
                    discount = "할인 없음"

                # 상품 이미지
                image_url = container.find_element(By.XPATH, './/button/span/span/span/img').get_attribute('src')

                # 상세 페이지 URL
                detail_link = container.find_element(By.XPATH, './/a').get_attribute('href')

                # 상품 ID 추출 (URL에서 ID만 추출)
                product_id = detail_link.split('/')[-1]

                # 중복 확인 및 데이터 저장
                if product_id not in [prod['상품ID'] for prod in total_products]:
                    total_products.append({
                        '상품ID': product_id,
                        '상품명': name,
                        '브랜드': brand,
                        '가격': price,
                        '할인율': discount,
                        '이미지 URL': image_url,
                        '상세 페이지 URL': detail_link,
                        '성별': gender,
                        '플랫폼': 'wconcept',
                        '카테고리': category_url.split('/')[-1]
                    })
            except Exception as e:
                print(f"상품 데이터 수집 오류: {e}")
                continue

        # 상품이 300개에 도달하면 종료
        if len(total_products) >= MAX_PRODUCTS:
            print("상품 300개 수집 완료. 크롤링을 종료합니다.")
            break

        # 현재까지 로드된 상품 수 출력
        print(f"현재까지 수집된 상품 개수: {len(total_products)}")

        # 스크롤 다운
        body = driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.END)
        time.sleep(3)  # 스크롤 후 로딩 시간 대기

        # 더 이상 새로운 상품이 로드되지 않으면 종료
        if not product_containers:
            print("더 이상 로드할 상품이 없습니다.")
            break

    # 데이터 저장: 각 카테고리별로 CSV로 저장
    products_df = pd.DataFrame(total_products)
    products_df.to_csv(file_name, index=False, encoding='utf-8-sig')
    print(f"데이터가 '{file_name}' 파일로 저장되었습니다.")

# 크롤링 종료 후 드라이버 종료
driver.quit()