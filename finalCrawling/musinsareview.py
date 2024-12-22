import pandas as pd  # CSV 저장을 위한 pandas 임포트
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys  # Keys 객체 임포트
import time
import re

# 크롬 드라이버 실행 (헤드리스 모드 및 GPU 활성화)
options = Options()
options.add_argument('--headless')  # 브라우저를 띄우지 않음
options.add_argument('--use-gl=desktop')  # GPU 렌더링 활성화
options.add_argument('--disable-gpu')  # Windows에서 GPU 사용 비활성화 (Linux에서는 필요 없음)
options.add_argument('--no-sandbox')  # 샌드박스 비활성화 (Linux에서 권장)
options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 사용 비활성화 (Linux에서 권장)

# Chrome 경로 및 ChromeDriver 경로 설정
options.binary_location = "/home/t24329/chrome/opt/google/chrome/google-chrome"  # Chrome 실행 파일 경로
driver_service = Service("/home/t24329/chrome/chromedriver")  # ChromeDriver 실행 파일 경로

# ChromeDriver 초기화
driver = webdriver.Chrome(service=driver_service, options=options)

try:
    # combined_products.csv에서 상품ID 가져오기
    products_df = pd.read_csv('/home/t24329/Crawling/Musinsa_2/combined_products.csv')
    product_ids = products_df['상품ID']  # 상품ID만 가져오기
    print(f"총 {len(product_ids)}개의 상품ID를 읽어왔습니다.")
    
    # 전체 리뷰 데이터를 저장할 리스트
    all_reviews = []

    # 각 상품에 대해 반복
    for product_id in product_ids:
        print(f"상품 ID: {product_id} 리뷰 크롤링 시작")
        review_url = f'https://www.musinsa.com/review/goods/{product_id}'
        driver.get(review_url)
        print(f"리뷰 페이지로 이동 완료! URL: {review_url}")
        time.sleep(3)

        # 리뷰 크롤링
        seen_reviews = set()  # 중복 제거를 위한 리뷰 ID 저장소
        total_reviews = []
        prev_review_count = 0

        while True:
            # 현재 화면에 있는 리뷰 요소들 수집
            review_containers_xpath = '//*[@id="commonLayoutContents"]/section/div/div[4]/div[8]/div/div[1]/div'
            review_containers = driver.find_elements(By.XPATH, review_containers_xpath)

            for container in review_containers:
                try:
                    # 작성자와 날짜
                    author_xpath = './/div/div[1]/a/div[2]/div[1]/span[1]'
                    date_xpath = './/div/div[1]/a/div[2]/div[1]/span[2]'
                    star_xpath = './/div/div[2]/span'  # 별점 XPath
                    content_xpaths = [
                        './/div/div[3]/div[3]/div/div',  # 첫 번째 본문 위치
                        './/div/div[3]/div[2]/div/div/div/span',  # 두 번째 본문 위치
                        './/div/div[3]/div[3]/div/div/div/span'  # 세 번째 본문 위치
                    ]
                    more_button_xpath = './/div/div[3]/div[3]/div/div/div/span/span[1]/span[3]/span/button'  # "더보기" 버튼 XPath

                    author = container.find_element(By.XPATH, author_xpath).text.strip()
                    date = container.find_element(By.XPATH, date_xpath).text.strip()
                    star_rating = container.find_element(By.XPATH, star_xpath).text.strip()  # 별점 가져오기

                    # "더보기" 버튼 처리
                    try:
                        more_button = container.find_element(By.XPATH, more_button_xpath)
                        if more_button.is_displayed():  # 버튼이 보이는 경우 클릭
                            driver.execute_script("arguments[0].click();", more_button)
                            time.sleep(1)  # 클릭 후 로딩 대기
                    except Exception:
                        pass  # "더보기" 버튼이 없는 경우 넘어감

                    # 본문 처리 (여러 XPath 시도)
                    content = "리뷰 본문 없음"
                    for xpath in content_xpaths:
                        try:
                            content = container.find_element(By.XPATH, xpath).text.strip()
                            break  # 본문을 찾으면 루프 종료
                        except Exception:
                            continue

                    # 리뷰 ID 생성 및 저장
                    review_id = f"{author}-{date}"
                    if review_id not in seen_reviews:
                        seen_reviews.add(review_id)
                        total_reviews.append({
                            '상품ID': product_id,
                            '작성자': author,
                            '작성날짜': date,
                            '리뷰본문': content,
                            '별점': star_rating
                        })
                except Exception as e:
                    continue  # 오류가 발생해도 다음 리뷰로 진행

            # 현재까지 로드된 리뷰 수 출력
            print(f"[상품ID: {product_id}] 현재까지 로드된 리뷰 개수: {len(total_reviews)}")

            # 리뷰 개수가 100개를 초과하면 종료
            if len(total_reviews) >= 3000:
                print(f"[상품ID: {product_id}] 리뷰 100개를 초과했습니다. 다음 상품으로 이동합니다.")
                break

            # 스크롤 다운
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.END)  # Keys 객체를 사용하여 스크롤 다운
            time.sleep(3)  # 스크롤 후 로딩 시간 대기

            # 새로운 리뷰가 더 이상 로드되지 않으면 종료
            if len(total_reviews) == prev_review_count:
                print("더 이상 새로운 리뷰가 없습니다.")
                break
            prev_review_count = len(total_reviews)

        # 현재 상품의 리뷰를 전체 리뷰에 추가
        if total_reviews:
            all_reviews.extend(total_reviews)
        else:
            # 리뷰가 없는 경우에도 기록
            all_reviews.append({
                '상품ID': product_id,
                '작성자': '리뷰 없음',
                '작성날짜': '리뷰 없음',
                '리뷰본문': '리뷰 없음',
                '별점': '리뷰 없음'
            })

    # 데이터 저장: 각 카테고리별로 CSV로 저장
    reviews_df = pd.DataFrame(all_reviews)
    reviews_df.to_csv('/home/t24329/Crawling/Musinsa_2/reviews_output.csv', index=False, encoding='utf-8-sig')
    print(f"리뷰 데이터가 'reviews_output.csv' 파일로 저장되었습니다.")

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    driver.quit()