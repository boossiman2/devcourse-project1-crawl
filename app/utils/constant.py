from typing import Final

# crawler.py
CRAWLER_OUTPUT_FILE_PATH: Final = 'app/data/crawl/country_code.json'

# visualizer.py
TEMPLATE_OUTPUT_PATH: Final = 'app/templates/'
# 별점을 SVG 형태로 생성하기 위한 상수
full_star_svg: Final = \
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" width="30" style="fill:gold;"><path d="M528.1 171.5l-146.4-21.3L316.7 17c-12.6-25.6-54.8-25.6-67.4 0l-65 132.9-146.4 21.3c-26.2 3.8-36.7 36-17.7 54.6l105.9 103-25 145.5c-4.5 26.2 23 46 46.4 33.7L288 439.6l130.6 68.6c23.4 12.3 50.9-7.4 46.4-33.7l-25-145.5 105.9-103c19-18.6 8.5-50.8-17.8-54.6z"/></svg>'
half_star_svg: Final = \
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" width="30" style="fill:gold;"><path d="M316.7 17L288 51.9 259.3 17c-12.6-25.6-54.8-25.6-67.4 0l-65 132.9L17 171.5C-9.2 175.3-19.6 207.5-.6 226.1l105.9 103L80.2 474.6c-4.5 26.2 23 46 46.4 33.7L288 439.6V51.9c12.6 0 25.3-12.6 28.7-17z"/></svg>'
empty_star_svg: Final = \
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" width="30" style="fill:lightgray;"><path d="M528.1 171.5l-146.4-21.3L316.7 17c-12.6-25.6-54.8-25.6-67.4 0l-65 132.9-146.4 21.3c-26.2 3.8-36.7 36-17.7 54.6l105.9 103-25 145.5c-4.5 26.2 23 46 46.4 33.7L288 439.6l130.6 68.6c23.4 12.3 50.9-7.4 46.4-33.7l-25-145.5 105.9-103c19-18.6 8.5-50.8-17.8-54.6z"/></svg>'

# wordcloud용 mask의 경로
MASK_PATH: Final = 'app/data/visualize/film_camera_mask.png'
HTML_PATH: Final = 'app/templates/' # html path

# 불용어
STOPWORDS: Final = {
    # 관사
    "a", "an", "the",
    
    # 대명사
    "he", "she", "it", "they", "him", "her", "them", "his", "their", 
    "this", "that", "these", "those",
    
    # 동사 및 조동사
    "is", "are", "was", "were", "be", "has", "have", "had", "will", 
    "can", "do", "does", "did",
    
    # 전치사
    "to", "of", "in", "with", "for", "on", "at", "by", "about", "such", "which",
    
    # 부사
    "very", "so", "just", "only", "more", "most", "many", "much", 
    "some", "like", "all",
    
    # 영화 관련 기타 단어
    "character", "story", "plot", "film", "movie", "scene", "part", 
    "role", "play", "actor", "actress", "series", "place", 
    "moment", "way", "world", "day", "night",
    
    # 숫자 및 순서 표현
    "first", "second", "one", "two",
    
    # 기타
    "Hui", "Ju"
}