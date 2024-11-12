from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

# 검색할 주제 리스트
Topics = [
    "Korean etiquette blog", "Daejeon culture blog", "Korean travel tips blog",
    "Daejeon history blog", "Korean customs blog", "Daejeon places to visit blog"
]

# Chrome WebDriver 설정
Driver = webdriver.Chrome()
Results = []

for Topic in Topics:
    # Bing에서 검색
    Driver.get("https://www.bing.com/")
    SearchBox = WebDriverWait(Driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    SearchBox.send_keys(f"{Topic} site:blog")
    SearchBox.send_keys(Keys.RETURN)
    
    try:
        # 검색 결과 로드
        WebDriverWait(Driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//li[@class='b_algo']//h2/a"))
        )

        # 링크 및 이미지 수집
        Links = Driver.find_elements(By.XPATH, "//li[@class='b_algo']")[:6]
        print(f"주제 '{Topic}': 검색 결과에서 {len(Links)}개의 링크를 찾았습니다")

        TopicResults = []

        for Link in Links:
            try:
                # URL 가져오기
                UrlElement = Link.find_element(By.XPATH, ".//h2/a")
                Url = UrlElement.get_attribute("href")
                
                # 이미지 가져오기
                try:
                    ImageElement = Link.find_element(By.XPATH, ".//img")
                    ImageUrl = ImageElement.get_attribute("src")
                except:
                    ImageUrl = None

                print(f"수집된 URL: {Url}, 이미지 URL: {ImageUrl}")
                
                # URL과 이미지 저장
                TopicResults.append({
                    "url": Url,
                    "image": ImageUrl
                })

            except Exception as E:
                print(f"주제 '{Topic}' 처리 중 오류 발생: {E}")

        # 주제 결과 추가
        Results.append({
            "category": Topic,
            "links": TopicResults
        })

    except Exception as E:
        print(f"주제 '{Topic}' 처리 중 오류 발생: {E}")

# 결과를 JSON 파일로 저장
if Results:
    with open("data.json", "w", encoding="utf-8") as F:
        json.dump(Results, F, ensure_ascii=False, indent=4)
    print("저장")
else:
    print("저장 링크 존재X")


Driver.quit()
