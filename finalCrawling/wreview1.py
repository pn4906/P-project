import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import random
import logging
from datetime import datetime
import json
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
    StaleElementReferenceException
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# User Agent 목록
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
]

class ReviewCrawler:
    def __init__(self, input_dir, output_dir):
        self.input_directory = input_dir
        self.output_directory = output_dir
        self.max_retries = 3
        self.max_reviews_per_product = 100
        self.progress_file = "crawling_progress.json"
        self.driver = None

    def get_driver(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--enable-webgl")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--use-gl=desktop")
            options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
            options.add_argument("--headless=new")
            
            options.binary_location = "/home/t24329/chrome/opt/google/chrome/google-chrome"
            driver_service = Service("/home/t24329/chrome/chromedriver")
            driver = webdriver.Chrome(service=driver_service, options=options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            logging.error(f"드라이버 초기화 실패: {e}")
            raise

    def load_progress(self):
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"진행 상황 로드 실패: {e}")
            return {}

    def save_progress(self, progress):
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"진행 상황 저장 실패: {e}")

    def convert_star_width_to_score(self, width):
        try:
            width = int(width)
            if width == 100: return 5
            elif width >= 80: return 4
            elif width >= 60: return 3
            elif width >= 40: return 2
            elif width >= 20: return 1
            else: return 0
        except:
            return "별점 변환 실패"

    def handle_alert(self, driver):
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            logging.info(f"알림 발견: {alert.text}")
            alert.accept()
        except TimeoutException:
            pass
        except Exception as e:
            logging.warning(f"알림 처리 실패: {e}")

    def check_no_reviews(self, driver):
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="reviewList"]/table/tbody'))
            )
            no_review_element = driver.find_element(By.XPATH, 
                '//*[@id="reviewList"]/table/tbody/tr/td[contains(@class, "no_data")]')
            return "첫 리뷰어가 되어 보세요!" in no_review_element.text
        except (TimeoutException, NoSuchElementException):
            return False
        except Exception as e:
            logging.warning(f"리뷰 확인 중 오류: {e}")
            return False

    def get_reviews_on_page(self, driver, page_number, product_id, all_reviews):
        reviews = []
        review_rows_xpath = '//*[@id="reviewList"]/table/tbody/tr'
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, review_rows_xpath))
            )
            review_rows = driver.find_elements(By.XPATH, review_rows_xpath)
            logging.info(f"현재 {page_number}페이지 리뷰 개수: {len(review_rows)}개")
            
            if not review_rows:
                logging.warning("현재 페이지에서 리뷰를 찾을 수 없습니다.")
                return reviews
                
        except Exception as e:
            logging.error(f"리뷰 데이터를 가져오는데 실패: {e}")
            return reviews

        for row in review_rows:
            try:
                review_data = self.extract_review_data(row, product_id, page_number)
                if review_data:
                    reviews.append(review_data)
                    if len(all_reviews) + len(reviews) >= self.max_reviews_per_product:
                        logging.info(f"최대 {self.max_reviews_per_product}개 리뷰를 가져왔습니다.")
                        break
            except StaleElementReferenceException:
                logging.warning("페이지 요소가 변경되었습니다. 다음 리뷰로 진행합니다.")
                continue
            except Exception as e:
                logging.error(f"리뷰 추출 중 오류 발생: {e}")
                continue

        return reviews

    def extract_review_data(self, row, product_id, page_number):
        try:
            # 별점 추출
            star_element = WebDriverWait(row, 5).until(
                EC.presence_of_element_located((By.XPATH, './td[1]/div/div/div/strong'))
            )
            star_style = star_element.get_attribute("style")
            if not star_style:
                raise ValueError("별점 스타일 속성이 없습니다")
            
            star_width = star_style.split("width:")[1].split("%")[0].strip()
            star = self.convert_star_width_to_score(star_width)
            
            # 나머지 데이터 추출
            author = row.find_element(By.XPATH, './td[2]/div[1]/p/em').text
            date = row.find_element(By.XPATH, './td[2]/div[1]/p/span').text
            review_text = row.find_element(By.XPATH, './td[2]/div[2]/p').text

            return {
                "product_id": product_id,
                "page": page_number,
                "star": star,
                "author": author,
                "date": date,
                "review_text": review_text
            }
        except Exception as e:
            logging.error(f"리뷰 데이터 추출 실패: {e}")
            return None

    def move_to_next_page(self, driver, current_page):
        if current_page < 10:
            next_page_xpath = f'//*[@id="reviewList"]/ul/li[{current_page + 3}]/a'
        else:
            next_page_xpath = '//*[@id="reviewList"]/ul/li[@class="next"]/a'
        
        for _ in range(self.max_retries):
            try:
                next_page_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, next_page_xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", next_page_button)
                logging.info(f"{current_page + 1} 페이지로 이동 시도")
                driver.execute_script("arguments[0].click();", next_page_button)
                time.sleep(random.uniform(1.5, 3))
                return True
            except Exception as e:
                logging.warning(f"{current_page + 1} 페이지로 이동 실패: {e}")
                time.sleep(random.uniform(1, 2))
        return False

    def save_reviews_to_csv(self, reviews, filename):
        if not reviews:
            logging.warning("저장할 리뷰가 없습니다.")
            return
            
        try:
            keys = reviews[0].keys()
            with open(filename, mode="w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=keys)
                writer.writeheader()
                writer.writerows(reviews)
            logging.info(f"리뷰 데이터를 {filename}에 저장했습니다.")
        except Exception as e:
            logging.error(f"CSV 저장 중 오류 발생: {e}")

    def crawl_product_reviews(self, product_id, all_reviews):
        if not self.driver:
            self.driver = self.get_driver()
        
        url = f"https://www.wconcept.co.kr/Product/{product_id}#review"
        try:
            self.driver.get(url)
            self.handle_alert(self.driver)

            if self.check_no_reviews(self.driver):
                logging.info("리뷰 없음 확인됨. 다음 상품으로 넘어갑니다.")
                return

            current_page = 1
            while len(all_reviews) < self.max_reviews_per_product:
                logging.info(f"{current_page}페이지 리뷰 크롤링 시작...")
                reviews = self.get_reviews_on_page(self.driver, current_page, product_id, all_reviews)
                all_reviews.extend(reviews)
                logging.info(f"{current_page}페이지 리뷰 크롤링 완료: {len(reviews)}개")

                if not reviews or not self.move_to_next_page(self.driver, current_page):
                    logging.info("더 이상 이동할 페이지가 없습니다. 크롤링 종료.")
                    break

                current_page += 1

        except Exception as e:
            logging.error(f"상품 {product_id} 크롤링 중 오류 발생: {e}")
            # 드라이버 재시작
            self.restart_driver()

    def restart_driver(self):
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        finally:
            self.driver = self.get_driver()

    def process_file(self, filename):
        # 이 두 파일만 처리
        allowed_files = []
        if filename not in allowed_files:
            logging.info(f"스킵: {filename} (처리 대상 파일이 아님)")
            return

        file_path = os.path.join(self.input_directory, filename)
        output_file = os.path.join(self.output_directory, filename.replace(".csv", "_review.csv"))
        
        # 진행 상황 체크를 건너뛰고 바로 처리 시작
        all_reviews = []
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                product_ids = [line.strip().split(",")[0] for line in file.readlines()][1:11]

            start_index = 0
            for idx, product_id in enumerate(product_ids[start_index:], start=start_index):
                logging.info(f"상품 ID: {product_id} 리뷰 크롤링 시작 ({idx + 1}/{len(product_ids)})")
                
                for attempt in range(self.max_retries):
                    try:
                        self.crawl_product_reviews(product_id, all_reviews)
                        break
                    except Exception as e:
                        logging.error(f"시도 {attempt + 1}/{self.max_retries} 실패: {e}")
                        if attempt == self.max_retries - 1:
                            raise
                        self.restart_driver()
                
                # 제품 간 딜레이
                time.sleep(random.uniform(2, 5))

            self.save_reviews_to_csv(all_reviews, output_file)
            
        except Exception as e:
            logging.error(f"파일 처리 중 오류 발생: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def run(self):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        for filename in os.listdir(self.input_directory):
            if filename.endswith(".csv") and not filename.endswith("_review.csv"):
                logging.info(f"파일 처리 시작: {filename}")
                self.process_file(filename)
                logging.info(f"파일 처리 완료: {filename}")

def main():
    input_directory = "/home/t24329/chrome"
    output_directory = "/home/t24329/chrome/wreviews"
    
    crawler = ReviewCrawler(input_directory, output_directory)
    crawler.run()

if __name__ == "__main__":
    main()      