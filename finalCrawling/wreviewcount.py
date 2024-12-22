import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # User Agent 랜덤 설정
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/109.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/109.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/109.0"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.binary_location = "/home/t24329/chrome/opt/google/chrome/google-chrome"
    driver_service = Service("/home/t24329/chrome/chromedriver")
    return webdriver.Chrome(service=driver_service, options=options)

def get_review_count(driver, product_id):
    try:
        url = f"https://www.wconcept.co.kr/Product/{product_id}"
        driver.get(url)
        time.sleep(random.uniform(1, 2))  # 랜덤 딜레이
        
        try:
            review_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="frmproduct"]/div[2]/p[3]'))
            )
            review_text = review_element.text
            review_count = int(re.findall(r'\d+', review_text)[0])
            return review_count
        except:
            return "리뷰 없음"
            
    except Exception as e:
        return "리뷰 없음"

def process_batch(product_batch):
    driver = get_driver()
    results = []
    try:
        for product_id in product_batch:
            review_count = get_review_count(driver, str(product_id))
            results.append((product_id, review_count))
            time.sleep(random.uniform(0.5, 1))  # 요청 간 짧은 랜덤 딜레이
    finally:
        driver.quit()
    return results

def update_file_with_review_counts(file_path):
    df = pd.read_csv(file_path)
    
    if '리뷰개수' not in df.columns:
        print(f"Adding review count column to {file_path}")
        df['리뷰개수'] = "리뷰 없음"
        
        # 상품 ID를 배치로 나누기
        batch_size = 10  # 각 쓰레드가 처리할 상품 수
        product_batches = [df['상품ID'][i:i + batch_size].tolist() 
                         for i in range(0, len(df), batch_size)]
        
        # ThreadPoolExecutor로 병렬 처리
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_batch = {executor.submit(process_batch, batch): batch 
                             for batch in product_batches}
            
            completed = 0
            for future in as_completed(future_to_batch):
                results = future.result()
                for product_id, review_count in results:
                    df.loc[df['상품ID'] == product_id, '리뷰개수'] = review_count
                
                completed += len(results)
                print(f"Progress: {completed}/{len(df)} products processed")
                
                # 중간 저장
                if completed % 50 == 0:
                    df.to_csv(file_path, index=False)
        
        # 최종 저장
        df.to_csv(file_path, index=False)
        print(f"Successfully updated {file_path} with review counts")

def main():
    input_directory = "/home/t24329/chrome"
    
    for filename in os.listdir(input_directory):
        if filename.endswith('.csv'):
            file_path = f"{input_directory}/{filename}"
            print(f"\nProcessing {filename}...")
            update_file_with_review_counts(file_path)

if __name__ == "__main__":
    main()  