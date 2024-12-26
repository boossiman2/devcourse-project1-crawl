# 표준 라이브러리
import base64
import os
import re
from io import BytesIO
from collections import Counter
from statistics import mean
from typing import Final

# 외부 라이브러리
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
from wordcloud import WordCloud
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

# 사용자 정의 모듈 (가정: 직접 정의한 함수나 데이터)
from app.Service.movie import get_movies_by_country_name
from app.utils.constant import *

class Visualizer:
    matplotlib.use('Agg')

    def __init__(self, country_name: str, db: Session, template_path: str = "app/templates/"):
        self.country_name = country_name
        self.movies = get_movies_by_country_name(db, self.country_name)  # 이미 SQLAlchemy 모델 객체 리스트
        self.mask_path = MASK_PATH
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.template = self.env.get_template("combined_visualization.html")

    def visualize_TOPK(self, k: int = 5):
        filtered_movies = [
            movie for movie in self.movies
            if any(ranking.rank <= k for ranking in movie.rankings)  # 'rankings'는 관계 설정을 의미
        ]
        movie_cards = ''.join([self.create_movie_card(movie) for movie in filtered_movies])
        return movie_cards

    def visualize_wordcloud(self, colormap: str = "magma"):
        text = " ".join(re.sub(r"[^\w\s]", "", movie.summary) for movie in self.movies)  # movie.summary로 접근
        mask_array = None
        if self.mask_path and os.path.exists(self.mask_path):
            mask_array = np.array(Image.open(self.mask_path).convert('L'))

        wordcloud = WordCloud(
            background_color="white",
            mask=mask_array,
            contour_color="black",
            contour_width=2,
            colormap=colormap,
            max_words=100,
            prefer_horizontal=True,
            stopwords=STOPWORDS
        ).generate(text)

        fig, ax = plt.subplots(figsize=(12, 12))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        img_base64 = self.convert_to_base64(fig)
        return img_base64

    def visualize_piechart(self, k: int = 8):
        all_genres = [genre for movie in self.movies for genre in movie.genres]  # movie.genres로 접근
        genre_counts = Counter(all_genres)
        top_genres = dict(genre_counts.most_common(k))

        labels = list(top_genres.keys())
        sizes = list(top_genres.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 12, 'weight': 'bold'}
        )
        ax.set_title("Genre Distribution", fontsize=18, weight="bold")
        img_base64 = self.convert_to_base64(fig)
        return img_base64

    def visualize_average_rating(self):
        average_rating = round(mean([float(movie.score) for movie in self.movies]), 3)  # movie.score로 접근
        stars_svg = self.display_svg_stars(average_rating)
        return average_rating, stars_svg

    def create_combined_html(self, topk_count=5) -> str:
        topk_section = self.visualize_TOPK(k=topk_count)
        wordcloud_image = self.visualize_wordcloud()
        piechart_image = self.visualize_piechart()
        average_rating, stars_svg = self.visualize_average_rating()

        rendered_html = self.template.render(
            country_name=self.country_name,
            movie_cards=topk_section,
            topk_count=topk_count,
            wordcloud_image=wordcloud_image,
            piechart_image=piechart_image,
            average_rating=average_rating,
            stars_svg=stars_svg
        )

        output_file = os.path.join(TEMPLATE_OUTPUT_PATH, f"{self.country_name}_combined_visualization.html")
        self.save_html(rendered_html, filepath=output_file)
        return output_file

    def create_movie_card(self, movie: 'Movie'):  # 'Movie'는 SQLAlchemy 모델
        stars_html = self.display_svg_stars(float(movie.score))  # movie.score로 접근
        return f"""
        <div style="display:inline-block; text-align:center; margin:10px; width:200px;">
            <img src="{movie.image_url}" style="width:150px; height:200px; object-fit:cover; border:1px solid #ccc; border-radius:8px;">
            <div style="margin-top:10px; font-weight:bold;">{movie.title}</div>
            <div style="font-size:12px; color:gray;">{movie.release_year}</div>
            <div style="margin-top:5px;">{stars_html}</div>
        </div>
        """

    def display_svg_stars(self, rating: float):
        rating = rating / 2
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        return full_star_svg * full_stars + half_star_svg * half_star + empty_star_svg * empty_stars

    def save_html(self, content: str, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"HTML 파일이 '{filepath}'에 저장되었습니다.")

    def convert_to_base64(self, fig=None, format="png", dpi=300, bbox_inches="tight"):
        if fig is None:
            fig = plt.gcf()
        buffer = BytesIO()
        plt.savefig(buffer, format=format, dpi=dpi, bbox_inches=bbox_inches)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        buffer.close()
        return image_base64