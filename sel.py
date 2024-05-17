from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from webdriver_manager.chrome import ChromeDriverManager

# Chrome WebDriver 설정
driver = webdriver.Chrome(ChromeDriverManager().install())

# 구글 지도 사이트 열기
driver.get("https://www.google.com/maps")

# 검색어 입력
search_box = driver.find_element_by_css_selector("input.tactile-searchbox-input")
search_query = "서울시청"  # 여기에 원하는 검색어 입력
search_box.send_keys(search_query)
search_box.send_keys(Keys.ENTER)

# 페이지 로딩 대기
time.sleep(5)

# BeautifulSoup을 사용하여 페이지 소스 가져오기
soup = BeautifulSoup(driver.page_source, 'html.parser')

# 원하는 정보 추출 예시: 장소 이름, 주소
place_name = soup.find("h1", class_="x3AX1-LfntMc-header-title-title gm2-headline-5").text
address = soup.find("div", class_="QSFF4-text gm2-body-2").text

print("장소 이름:", place_name)
print("주소:", address)

# 웹 드라이버 종료
driver.quit()
