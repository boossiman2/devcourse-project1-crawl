import json
import os
import time
from datetime import datetime
from typing import Final

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm # type: ignore
from webdriver_manager.chrome import ChromeDriverManager

from constant import CRAWLER_OUTPUT_FILE_PATH

OUTPUT_FILE_PATH: Final = CRAWLER_OUTPUT_FILE_PATH

class MovieCrawler:
    def initialize_driver(self):
        """
        Chrome WebDriver를 초기화하는 함수
        
        :return: 초기화된 WebDriver 인스턴스
        """
        options = self.configure_chrome_options()
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def configure_chrome_options(self):
        """
        Chrome WebDriver 옵션을 설정하는 함수
        
        :return: 설정된 ChromeOptions 객체
        """
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 필요시 headless 모드 활성화
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return options

    def click_button(self, driver, wait, xpath: str):
        """
        주어진 XPATH로 버튼을 클릭하는 함수

        :param driver: Selenium WebDriver 인스턴스
        :param wait: WebDriverWait 인스턴스 (타임아웃 설정)
        :param xpath: 클릭할 버튼의 XPATH
        """
        button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        ActionChains(driver).click(button).perform()

    def transform_content_to_result(self, content: dict, country: str) -> dict:
        """
        추출한 콘텐츠를 요구되는 JSON 구조로 변환하는 함수

        :param content: 추출된 콘텐츠 (딕셔너리)
        :param country: 영화가 속한 국가
        :return: 변환된 JSON 구조
        """
        return {
            "country": country,
            "movie": {
                "title": content.get("title"),
                "release_year": content.get("year"),
                "score": content.get("score"),
                "summary": content.get("summary"),
                "image_url": content.get("img"),
                "genres": content.get("genre", []),
                "actors": content.get("stars", [])
            },
            "rank": content["rank"]
        }

    def __init__(self, country_codes_filepath=OUTPUT_FILE_PATH, top_n=10):
        """
        크롤러 초기화 함수

        :param country_codes_filepath: 국가 코드가 저장된 JSON 파일 경로
        :param top_n: 크롤링할 영화의 수
        """
        self.BASE_URL = 'https://www.imdb.com/search/title/?countries={}'
        self.BASE_XPATH = '/html/body/div[4]/div[2]/div/div[2]/div/div'
        self.RELATIVE_XPATHS = {
            'img': '/div[1]/div[1]/div/div/img',
            'title': '/div[1]/div[2]/div[1]/a/h3',
            'year': '/div[1]/div[2]/ul[1]/li[1]',
            'score': '/div[1]/div[2]/div[2]/span/span[1]',
            'summary': '/div[2]'
        }
        self.ELEMENTS_PATH = {
            'genre': '/div[1]/div[2]/ul[2]/li[{}]',
            'stars': '/div[3]/div/ul/li[{}]'
        }
        self.CLOSE_BUTTON_XPATH = '/html/body/div[4]/div[2]/div/div[1]/button'
        self.BUTTON_XPATH_TEMPLATE = (
            '//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/'
            'div[2]/div[2]/ul/li[{}]/div/div/div/div[1]/div[3]/button'
        )
        self.save_at:Final = 'app/data/crawl/movies_data_country.json'
        self.country_codes_filepath = country_codes_filepath
        self.top_n = top_n
        
    def load_country_codes(self, filepath=OUTPUT_FILE_PATH):
        """국가 코드 로드"""
        if not os.path.exists(filepath):
            print(f"{filepath} 파일이 존재하지 않습니다. 기본 데이터를 생성합니다.")
            self.create_default_country_code_file(filepath)

        # 파일을 열고 데이터를 로드
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def create_default_country_code_file(self, filepath: str = OUTPUT_FILE_PATH):
        """기본 국가 코드 데이터를 json 파일로 생성하는 함수."""
        # 기본 국가 코드 데이터
        default_data = {
            "KR": "South Korea",
            "US": "United States",
            "GB": "United Kingdom",
            "AU": "Australia",
            "BR": "Brazil",
            "ZA": "South Africa"
        }

        # 디렉토리 생성 (경로에 디렉토리가 없으면 생성)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # 기본 데이터를 파일로 작성
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        
        print(f"기본 국가 코드 파일이 {filepath}에 생성되었습니다.")
    
    def initialize_driver(self):
        """WebDriver 초기화"""
        options = self.configure_chrome_options()
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def scrape_modal_content(self, wait, base_xpath: str, relative_xpaths: dict) -> dict:
        """
        모달 창에서 콘텐츠를 추출하는 함수

        :param wait: WebDriverWait 인스턴스 (타임아웃 설정)
        :param base_xpath: 모든 요소에 공통으로 사용되는 XPATH
        :param relative_xpaths: 각 요소별 상대적인 XPATH가 담긴 딕셔너리
        :return: 추출된 콘텐츠(img_url, 제목, 개봉년도, 평점, 요약)가 담긴 딕셔너리
        """
        extracted_content = {}
        for element_name, relative_xpath in relative_xpaths.items():
            try:
                full_xpath = base_xpath + relative_xpath
                if element_name == 'img':
                    # 이미지의 경우 'src' 속성을 가져옴
                    extracted_content[element_name] = wait.until(
                        EC.presence_of_element_located((By.XPATH, full_xpath))
                    ).get_attribute('src')
                else:
                    # 나머지 요소는 텍스트를 가져옴
                    extracted_content[element_name] = wait.until(
                        EC.presence_of_element_located((By.XPATH, full_xpath))
                    ).text
            except Exception as e:
                print(f"Error fetching {element_name}: {e}")
        return extracted_content

    def scrape_modal_data(self, driver, base_xpath: str, relative_xpaths: dict) -> dict:
        """
        모달 창에서 반복적으로 나타나는 데이터를 추출하는 함수

        :param driver: Selenium WebDriver 인스턴스
        :param base_xpath: 모든 요소에 공통으로 사용되는 XPATH
        :param relative_xpaths: 각 요소별 상대적인 XPATH 템플릿이 담긴 딕셔너리
        :return: 추출된 데이터(장르 리스트, 출연진 리스트) 가 담긴 딕셔너리
        """
        extracted_data = {}
        # 상대 XPATH 템플릿을 기준으로 반복
        for element_name, xpath_template in relative_xpaths.items():
            values = []
            index = 1
            while True:
                try:
                    full_xpath = f"{base_xpath}{xpath_template.format(index)}"
                    element = driver.find_element(By.XPATH, full_xpath)
                    values.append(element.text)
                    index += 1
                except Exception:
                    break
            # 추출한 값들을 딕셔너리에 저장 (키는 element_name, 값은 values 리스트)
            extracted_data[element_name] = values
        return extracted_data

    def process_movie(self, driver, wait, country, country_code, rank):
        """
        단일 영화 항목을 처리하는 함수

        :param driver: Selenium WebDriver 인스턴스
        :param wait: WebDriverWait 인스턴스 (타임아웃 설정)
        :param country: 영화가 속한 국가
        :param country_code: 국가 코드
        :param rank: 영화의 순위
        :return: 추출된 영화 정보가 담긴 딕셔너리
        """
        content = {}
        try:
            print(f"Processing item {rank} for {country}({country_code})")
            # 버튼 클릭
            button_xpath = self.BUTTON_XPATH_TEMPLATE.format(rank)
            self.click_button(driver, wait, button_xpath)
            time.sleep(0.5)
            # 콘텐츠 크롤링 -> img_url, 제목, 개봉년도, 평점, 요약
            content = self.scrape_modal_content(wait, self.BASE_XPATH, self.RELATIVE_XPATHS)
            # 국가 추가
            content['country'] = country
            # 추가 데이터 -> 장르, 출연진
            content.update(self.scrape_modal_data(driver, self.BASE_XPATH, self.ELEMENTS_PATH))
            # 순위 추가
            content['rank'] = rank
            # 모달 닫기
            self.click_button(driver, wait, self.CLOSE_BUTTON_XPATH)
            time.sleep(0.5)
        except Exception as e:
            self.log_error(country, rank, e)
        return content
    
    def log_error(self, country, rank, error):
        """
        에러 발생 시 로그를 기록하는 함수
        
        :param country: 영화가 속한 국가
        :param rank: 영화의 순위
        :param error: 발생한 예외
        """
        print(f"Error processing item {rank} for {country}: {error}")
    
    def save_dict_as_json(self, data, file_path):
        """
        딕셔너리 데이터를 JSON 파일로 저장하는 함수
        
        :param data: 저장할 데이터 (딕셔너리)
        :param file_path: 저장할 파일 경로
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("JSON 파일이 성공적으로 저장되었습니다!")
        except Exception as e:
            print(f"An error occured:{e}")
    
    def crawling(self):
        """크롤링 메인 함수"""
        result = {"movies": []}

        try:
            # 국가 코드 로드
            country_code_dict = self.load_country_codes()
        except FileNotFoundError:
            print("Country code file not found. Creating default file.")
            self.create_default_country_code_file(self.country_codes_filepath)
            country_code_dict = self.load_country_codes()
        except json.JSONDecodeError:
            print("Error decoding the country code file. Please check the file format.")
            return result
        except Exception as e:
            print(f"Unexpected error while loading country codes: {e}")
            return result

        for country_code, country in country_code_dict.items():
            try:
                with self.initialize_driver() as driver:
                    wait = WebDriverWait(driver, 10)
                    driver.get(self.BASE_URL.format(country_code))

                    for rank in range(1, self.top_n + 1):
                        try:
                            content = self.process_movie(driver, wait, country, country_code, rank)
                            if content:
                                result["movies"].append(self.transform_content_to_result(content, country))
                        except Exception as e:
                            self.log_error(country, rank, e)
            except webdriver.WebDriverException:
                print(f"WebDriver error while processing country: {country} ({country_code})")
            except Exception as e:
                print(f"Unexpected error for country {country} ({country_code}): {e}")

        try:
            self.save_dict_as_json(result, self.save_at)
        except IOError:
            print("Failed to save results due to file I/O error.")
        except Exception as e:
            print(f"Unexpected error while saving results: {e}")

        return result