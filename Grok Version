import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pytz
import logging
from markupsafe import escape
import folium
from streamlit_folium import st_folium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from newspaper import Article
import sqlite3
from typing import List, Dict, Optional

# 로깅 설정
logging.basicConfig(filename='app.log', level=logging.ERROR)

# 페이지 설정
st.set_page_config(
    page_title="🚨 SCM Risk Monitor",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2025년 트렌드 반영: 다크 모드, Neumorphism, Bold Typography
st.markdown("""
<style>
    :root {
        --bg-color: #1e1e2e;
        --text-color: #e0e0e0;
        --card-bg: #2a2a3c;
        --accent-color: #6366f1;
        --danger-color: #ef4444;
        --warning-color: #f59e0b;
        --success-color: #10b981;
    }
    .stApp {
        background: var(--bg-color);
        font-family: 'Inter', sans-serif;
        color: var(--text-color);
    }
    .main-header {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        animation: fadeIn 1s ease-out;
    }
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-subtitle {
        font-size: 1rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    .unified-info-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .unified-info-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    .info-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .info-content {
        font-size: 1rem;
        color: var(--text-color);
        opacity: 0.85;
        text-align: center;
    }
    .search-section {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .stTextInput > div > div > input {
        background: #3b3b4f;
        color: var(--text-color);
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }
    .stTextInput > div > div > input:focus {
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton > button {
        background: var(--accent-color) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: #4f46e5 !important;
        transform: scale(1.05) !important;
    }
    .news-item {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--accent-color);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
    }
    .news-item:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        border-left-color: #4f46e5;
    }
    .news-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 0.5rem;
        transition: color 0.3s ease;
    }
    .news-item:hover .news-title {
        color: var(--accent-color);
    }
    .news-description {
        font-size: 1rem;
        color: var(--text-color);
        opacity: 0.7;
        margin-bottom: 0.5rem;
    }
    .news-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.9rem;
        color: var(--text-color);
        opacity: 0.6;
        margin-bottom: 0.5rem;
    }
    .news-source {
        background: var(--accent-color);
        color: white;
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        font-size: 0.9rem;
    }
    .news-link {
        color: var(--accent-color);
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .news-link:hover {
        color: #4f46e5;
    }
    .map-wrapper {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .risk-item {
        background: var(--card-bg);
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .risk-item:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    .risk-high { border-left: 4px solid var(--danger-color); }
    .risk-medium { border-left: 4px solid var(--warning-color); }
    .risk-low { border-left: 4px solid var(--success-color); }
    .risk-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-color);
    }
    .risk-desc {
        font-size: 0.9rem;
        color: var(--text-color);
        opacity: 0.7;
    }
    .market-info {
        background: var(--card-bg);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .market-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 0.5rem;
    }
    .market-item {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
        color: var(--text-color);
        opacity: 0.85;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--accent-color);
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: var(--text-color);
        opacity: 0.6;
        font-size: 1rem;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

def get_korean_time():
    """한국 시간 정보 가져오기"""
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    return now.strftime('%Y년 %m월 %d일'), now.strftime('%H:%M:%S')

def get_seoul_weather():
    """서울 날씨 정보 가져오기 (네이버 날씨 크롤링)"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://weather.naver.com/today/09140105")
        time.sleep(3)
        temp_element = driver.find_element(By.CSS_SELECTOR, ".current")
        temperature = float(temp_element.text.replace("현재 온도", "").replace("°", "").strip())
        condition_element = driver.find_element(By.CSS_SELECTOR, ".weather")
        condition = condition_element.text.strip()
        summary_list = driver.find_elements(By.CSS_SELECTOR, ".summary_list .summary_item")
        humidity = None
        wind_speed = None
        feels_like = temperature
        for item in summary_list:
            text = item.text
            if "습도" in text:
                humidity = int(text.replace("습도", "").replace("%", "").strip())
            elif "바람" in text:
                wind_speed = float(text.split("m/s")[0].replace("바람", "").strip())
            elif "체감" in text:
                feels_like = float(text.replace("체감", "").replace("°", "").strip())
        driver.quit()
        return {
            "condition": condition,
            "temperature": round(temperature, 1),
            "humidity": humidity or 60,
            "feels_like": round(feels_like, 1),
            "wind_speed": wind_speed or 5,
            "location": "서울"
        }
    except Exception as e:
        logging.error(f"Naver weather crawling error: {e}")
        st.error("네이버 날씨 데이터를 불러오지 못했습니다. 기본 데이터를 표시합니다.")
        return {
            "condition": "맑음",
            "temperature": 22,
            "humidity": 60,
            "feels_like": 22,
            "wind_speed": 5,
            "location": "서울"
        }

def get_exchange_rates():
    """실시간 환율 정보 가져오기 (시뮬레이션)"""
    try:
        base_rates = {
            "USD/KRW": 1320.50,
            "EUR/KRW": 1445.30,
            "JPY/KRW": 8.95,
            "CNY/KRW": 182.40,
            "GBP/KRW": 1675.80
        }
        exchange_rates = {}
        for pair, rate in base_rates.items():
            variation = random.uniform(-0.005, 0.005)
            new_rate = rate * (1 + variation)
            exchange_rates[pair] = round(new_rate, 2)
        return exchange_rates
    except Exception as e:
        logging.error(f"Exchange rate error: {e}")
        return base_rates

def get_lme_prices():
    """주요 광물 시세 가져오기 (시뮬레이션)"""
    try:
        base_prices = {
            "Gold": 2650.80,
            "Silver": 32.45,
            "Oil": 78.50,
            "Copper": 8425.50,
            "Uranium": 95.20
        }
        commodity_prices = {}
        for commodity, price in base_prices.items():
            variation = random.uniform(-0.01, 0.01)
            new_price = price * (1 + variation)
            commodity_prices[commodity] = round(new_price, 2)
        return commodity_prices
    except Exception as e:
        logging.error(f"Commodity price error: {e}")
        return base_prices

def get_scm_risk_locations():
    """SCM Risk 발생 지역 데이터"""
    return [
        {
            "name": "우크라이나",
            "flag": "🇺🇦",
            "risk_level": "high",
            "risk_type": "전쟁",
            "description": "러시아-우크라이나 전쟁으로 인한 공급망 중단",
            "lat": 48.3794,
            "lng": 31.1656,
            "news": [
                "우크라이나 곡물 수출 중단으로 글로벌 식량 위기",
                "러시아 에너지 공급 중단으로 유럽 에너지 위기",
                "우크라이나 항구 봉쇄로 해상 운송 혼잡"
            ]
        },
        {
            "name": "홍해",
            "flag": "🌊",
            "risk_level": "high",
            "risk_type": "해적활동",
            "description": "호세이드 해적 활동으로 인한 해상 운송 위험",
            "lat": 15.5527,
            "lng": 42.4497,
            "news": [
                "홍해 해적 활동 증가로 운송비 상승",
                "홍해 봉쇄로 글로벌 물류 혼잡",
                "홍해 해적 공격으로 화물선 운항 중단"
            ]
        },
        {
            "name": "대만",
            "flag": "🇹🇼",
            "risk_level": "medium",
            "risk_type": "지정학적",
            "description": "중국-대만 관계 악화로 인한 반도체 공급 위험",
            "lat": 23.6978,
            "lng": 120.9605,
            "news": [
                "대만 해협 긴장으로 반도체 공급망 위기",
                "중국-대만 관계 악화로 전자제품 공급 중단",
                "대만 반도체 산업 지리적 위험 증가"
            ]
        },
        {
            "name": "일본 후쿠시마",
            "flag": "🇯🇵",
            "risk_level": "medium",
            "risk_type": "환경",
            "description": "원전 오염수 방류로 인한 수산물 수출 제한",
            "lat": 37.7603,
            "lng": 140.4733,
            "news": [
                "후쿠시마 원전 오염수 방류로 수산물 수출 제한",
                "일본 원전 사고로 농수산물 교역 중단",
                "후쿠시마 방사능 오염으로 식품 안전 위기"
            ]
        },
        {
            "name": "중국 상하이",
            "flag": "🇨🇳",
            "risk_level": "medium",
            "risk_type": "정책",
            "description": "중국 제조업 생산 중단으로 인한 부품 부족",
            "lat": 31.2304,
            "lng": 121.4737,
            "news": [
                "상하이 봉쇄로 글로벌 공급망 위기",
                "중국 제조업 생산 중단으로 부품 부족",
                "상하이 항구 혼잡으로 물류 지연"
            ]
        },
        {
            "name": "미국 로스앤젤레스",
            "flag": "🇺🇸",
            "risk_level": "low",
            "risk_type": "노동",
            "description": "항구 혼잡과 노동자 파업 위험",
            "lat": 34.0522,
            "lng": -118.2437,
            "news": [
                "LA 항구 혼잡으로 물류 지연",
                "미국 서부 해안 노동자 파업 위기",
                "LA 항구 자동화 시스템 도입 확대"
            ]
        },
        {
            "name": "독일 함부르크",
            "flag": "🇩🇪",
            "risk_level": "low",
            "risk_type": "기술",
            "description": "물류 디지털화 가속화",
            "lat": 53.5511,
            "lng": 9.9937,
            "news": [
                "함부르크 항구 물류 효율성 향상",
                "독일 물류 디지털화 가속화",
                "함부르크 스마트 포트 프로젝트"
            ]
        },
        {
            "name": "싱가포르",
            "flag": "🇸🇬",
            "risk_level": "low",
            "risk_type": "기술",
            "description": "물류 허브 경쟁력 강화",
            "lat": 1.3521,
            "lng": 103.8198,
            "news": [
                "싱가포르 물류 허브 경쟁력 강화",
                "싱가포르 디지털 물류 플랫폼 도입",
                "싱가포르 친환경 물류 정책"
            ]
        }
    ]

def create_risk_map():
    """인터랙티브 SCM Risk 지도 생성 (Plotly)"""
    risk_locations = get_scm_risk_locations()
    risk_colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}
    df = pd.DataFrame(risk_locations)
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lng",
        color="risk_level",
        hover_name="name",
        hover_data={"description": True, "risk_type": True, "risk_level": False},
        color_discrete_map=risk_colors,
        size=[10] * len(df),
        projection="natural earth",
        title="SCM Risk Map"
    )
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)", landcolor="#2a2a3c"),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig, risk_locations

@st.cache_data(ttl=3600)
def crawl_scm_risk_news(num_results: int = 20, search_query: str = None) -> List[Dict]:
    """SCM Risk 관련 뉴스 크롤링 및 요약"""
    try:
        if search_query:
            enhanced_query = f"{search_query} supply chain OR logistics OR manufacturing OR shipping"
            encoded_query = urllib.parse.quote(enhanced_query)
        else:
            scm_keywords = [
                "supply chain risk", "logistics disruption", "global supply chain",
                "manufacturing shortage", "shipping crisis", "port congestion",
                "trade war", "semiconductor shortage", "energy crisis", "food security"
            ]
            selected_keyword = random.choice(scm_keywords)
            encoded_query = urllib.parse.quote(selected_keyword)
        
        news_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(news_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        articles = []
        conn = sqlite3.connect('scm_news.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS news
                     (title TEXT, url TEXT, source TEXT, published_time TEXT, description TEXT, views INTEGER)''')
        
        for item in items[:num_results]:
            title = item.find('title').text if item.find('title') else ""
            link = item.find('link').text if item.find('link') else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') else ""
            source = item.find('source').text if item.find('source') else ""
            if title.strip():
                try:
                    from email.utils import parsedate_to_datetime
                    parsed_date = parsedate_to_datetime(pub_date)
                    formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                # 뉴스 요약 생성
                try:
                    article = Article(link)
                    article.download()
                    article.parse()
                    article.nlp()
                    description = article.summary[:200] or f"{title} - {source}에서 제공하는 SCM Risk 관련 뉴스입니다."
                except:
                    description = f"{title} - {source}에서 제공하는 SCM Risk 관련 뉴스입니다."
                
                article_data = {
                    'title': title,
                    'url': link,
                    'source': source,
                    'published_time': formatted_date,
                    'description': description,
                    'views': random.randint(100, 5000)
                }
                articles.append(article_data)
                c.execute("INSERT INTO news VALUES (?, ?, ?, ?, ?, ?)",
                         (title, link, source, formatted_date, description, article_data['views']))
        conn.commit()
        conn.close()
        return articles
    except Exception as e:
        logging.error(f"News crawling failed: {e}")
        st.error(f"뉴스 데이터를 불러오지 못했습니다: {e}. 대체 데이터를 표시합니다.")
        return generate_scm_backup_news(num_results, search_query)

def generate_scm_backup_news(num_results: int, search_query: str = None) -> List[Dict]:
    """SCM Risk 백업 뉴스 생성"""
    articles = []
    news_sites = [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Bloomberg", "url": "https://www.bloomberg.com"},
        {"name": "WSJ", "url": "https://www.wsj.com"},
        {"name": "CNBC", "url": "https://www.cnbc.com"},
        {"name": "Financial Times", "url": "https://www.ft.com"},
        {"name": "BBC", "url": "https://www.bbc.com"},
        {"name": "CNN", "url": "https://www.cnn.com"},
        {"name": "AP", "url": "https://apnews.com"}
    ]
    scm_news_data = [
        {
            "title": "Global Supply Chain Disruptions Impact Manufacturing",
            "description": "글로벌 제조업체들이 공급망 중단으로 인한 생산 지연과 비용 증가를 겪고 있습니다."
        },
        {
            "title": "Shipping Crisis Causes Port Congestion Worldwide",
            "description": "전 세계 주요 항구에서 화물선 대기 시간이 길어지며 물류 비용이 급증하고 있습니다."
        },
        {
            "title": "Semiconductor Shortage Affects Global Electronics",
            "description": "반도체 부족 현상이 전자제품 생산에 심각한 영향을 미치고 있습니다."
        }
    ]
    filtered_news_data = scm_news_data
    if search_query:
        search_lower = search_query.lower()
        filtered_news_data = [
            news for news in scm_news_data
            if search_lower in news['title'].lower() or search_lower in news['description'].lower()
        ]
        if not filtered_news_data:
            filtered_news_data = scm_news_data
    conn = sqlite3.connect('scm_news.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news
                 (title TEXT, url TEXT, source TEXT, published_time TEXT, description TEXT, views INTEGER)''')
    for i in range(num_results):
        site = random.choice(news_sites)
        news_data = filtered_news_data[i % len(filtered_news_data)]
        title = news_data['title']
        if search_query and search_query.lower() in title.lower():
            title = title.replace(search_query, f"**{search_query}**")
        article = {
            'title': title,
            'url': site['url'],
            'source': site['name'],
            'published_time': (datetime.now() - timedelta(hours=random.randint(0, 24))).strftime('%Y-%m-%d %H:%M'),
            'description': news_data['description'],
            'views': random.randint(100, 5000)
        }
        articles.append(article)
        c.execute("INSERT INTO news VALUES (?, ?, ?, ?, ?, ?)",
                 (title, site['url'], site['name'], article['published_time'], news_data['description'], article['views']))
    conn.commit()
    conn.close()
    return articles

def plot_risk_distribution():
    """리스크 수준별 지역 수 시각화"""
    risk_locations = get_scm_risk_locations()
    risk_counts = pd.Series([loc["risk_level"] for loc in risk_locations]).value_counts()
    fig = px.bar(
        x=risk_counts.index,
        y=risk_counts.values,
        labels={"x": "리스크 수준", "y": "지역 수"},
        title="SCM 리스크 수준 분포",
        color=risk_counts.index,
        color_discrete_map={"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig

def check_high_risk_alert():
    """고위험 리스크 알림 확인"""
    risk_locations = get_scm_risk_locations()
    high_risk_count = sum(1 for loc in risk_locations if loc["risk_level"] == "high")
    if high_risk_count > st.session_state.get('last_high_risk_count', 0):
        st.toast(f"🚨 새로운 고위험 리스크 감지: {high_risk_count}건", icon="⚠️")
    st.session_state.last_high_risk_count = high_risk_count

def main():
    # 테마 토글
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"
    theme = st.sidebar.selectbox("테마", ["Dark", "Light"], index=0 if st.session_state.theme == "dark" else 1)
    if theme.lower() != st.session_state.theme:
        st.session_state.theme = theme.lower()
        st.markdown(f"""
        <style>
            .stApp {{ background: {'#fafafa' if theme == 'Light' else '#1e1e2e'}; }}
            .unified-info-card, .search-section, .news-item, .market-info, .risk-item {{
                background: {'#ffffff' if theme == 'Light' else '#2a2a3c'};
            }}
            .info-title, .news-title, .risk-title, .market-title, .section-header, .info-content, .news-description, .news-meta, .market-item, .risk-desc {{
                color: {'#2c3e50' if theme == 'Light' else '#e0e0e0'};
            }}
        </style>
        """, unsafe_allow_html=True)

    # 메인 헤더
    st.markdown("""
    <div class="main-header">
        <div class="main-title">SCM Risk Monitor</div>
        <div class="main-subtitle">Real-Time Global Supply Chain Risk Monitoring</div>
    </div>
    """, unsafe_allow_html=True)

    # 메인 레이아웃
    col1, col2, col3 = st.columns([1.2, 2.2, 1.1])

    # 좌측 컬럼 - 통합 정보
    with col1:
        date_str, time_str = get_korean_time()
        weather_info = get_seoul_weather()
        st.markdown(f"""
        <div class="unified-info-card">
            <div class="info-title">🇰🇷 서울 정보</div>
            <div class="info-content">
                <strong>{date_str}</strong><br>
                <strong style="font-size: 1.2rem;">{time_str}</strong><br><br>
                ☁️ {weather_info['condition']}<br>
                <strong>{weather_info['temperature']}°C</strong><br>
                체감 {weather_info['feels_like']}°C
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 검색 기능
        st.markdown("""
        <div class="search-section">
            <h4 style="font-size: 1.2rem; margin: 0 0 0.5rem 0;">🔍 검색</h4>
        </div>
        """, unsafe_allow_html=True)
        search_query = st.text_input("", placeholder="SCM 뉴스 검색...", key="search_input")
        if st.button("검색", key="search_button"):
            if search_query:
                with st.spinner(f"검색 중: {escape(search_query)}..."):
                    st.session_state.scm_articles = crawl_scm_risk_news(20, search_query)
                    st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                    st.session_state.search_query = search_query
                    st.session_state.page = 1
                    st.rerun()
            else:
                st.warning("검색어를 입력해주세요.")
        if 'search_query' in st.session_state and st.session_state.search_query:
            st.info(f"🔍 현재 검색어: {escape(st.session_state.search_query)}")
            if st.button("검색 초기화", key="clear_search"):
                st.session_state.search_query = ""
                st.session_state.scm_articles = crawl_scm_risk_news(20)
                st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                st.session_state.page = 1
                st.rerun()

    # 중앙 컬럼 - 뉴스
    with col2:
        if 'scm_articles' not in st.session_state:
            with st.spinner("SCM Risk 뉴스 로딩 중..."):
                st.session_state.scm_articles = crawl_scm_risk_news(20)
                st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                st.session_state.page = 1

        # 실시간 알림 체크
        check_high_risk_alert()

        # 뉴스 헤더
        if st.session_state.scm_articles:
            load_time = st.session_state.get('scm_load_time', datetime.now().strftime('%H:%M'))
            search_status = ""
            if 'search_query' in st.session_state and st.session_state.search_query:
                search_status = f" | 🔍 검색어: {escape(st.session_state.search_query)}"
            st.markdown(f"""
            <div class="unified-info-card">
                <h3 class="section-header">SCM Risk 뉴스 ({len(st.session_state.scm_articles)}개)</h3>
                <p style="font-size: 1rem; opacity: 0.6; margin: 0;">최근 업데이트: {load_time}{search_status}</p>
            </div>
            """, unsafe_allow_html=True)

            # 페이지네이션
            page_size = 10
            page = st.number_input("페이지", min_value=1, max_value=(len(st.session_state.scm_articles) // page_size) + 1, value=st.session_state.get('page', 1), key="page_input")
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            for i, article in enumerate(st.session_state.scm_articles[start_idx:end_idx], start_idx + 1):
                st.markdown(f"""
                <div class="news-item" role="article" aria-label="SCM Risk News Item {i}">
                    <div class="news-title">{escape(article['title'])}</div>
                    <div class="news-description">{escape(article['description'])}</div>
                    <div class="news-meta">
                        <span class="news-source">{escape(article['source'])}</span>
                        <span>{article['published_time']}</span>
                        <span>{article['views']:,} 조회</span>
                    </div>
                    <a href="{article['url']}" target="_blank" class="news-link">자세히 보기 →</a>
                </div>
                """, unsafe_allow_html=True)

        # 리스크 분포 차트
        st.markdown('<h3 class="section-header">리스크 분포</h3>', unsafe_allow_html=True)
        st.plotly_chart(plot_risk_distribution(), use_container_width=True)

    # 우측 컬럼 - 지도와 시장 정보
    with col3:
        st.markdown('<h3 class="section-header">리스크 지도</h3>', unsafe_allow_html=True)
        try:
            risk_map, risk_locations = create_risk_map()
            st.plotly_chart(risk_map, use_container_width=True)
        except Exception as e:
            logging.error(f"Map rendering error: {e}")
            st.error(f"지도 렌더링 오류: {e}")

        st.markdown("""
        <div class="market-info">
            <div class="market-title">🚩 리스크 수준</div>
            <div class="risk-item risk-high">
                <div class="risk-title">🔴 고위험</div>
                <div class="risk-desc">즉각적인 조치 필요</div>
            </div>
            <div class="risk-item risk-medium">
                <div class="risk-title">🟠 중위험</div>
                <div class="risk-desc">면밀히 모니터링 필요</div>
            </div>
            <div class="risk-item risk-low">
                <div class="risk-title">🟢 저위험</div>
                <div class="risk-desc">정상 운영</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        exchange_rates = get_exchange_rates()
        st.markdown("""
        <div class="market-info">
            <div class="market-title">💱 환율 정보</div>
        """, unsafe_allow_html=True)
        for pair, rate in exchange_rates.items():
            st.markdown(f"""
            <div class="market-item">
                <span>{pair}</span>
                <span>{rate}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        commodity_prices = get_lme_prices()
        st.markdown("""
        <div class="market-info">
            <div class="market-title">⛏️ 광물 시세</div>
        """, unsafe_allow_html=True)
        for commodity, price in commodity_prices.items():
            unit = "/oz" if commodity in ["Gold", "Silver"] else "/barrel" if commodity == "Oil" else "/ton" if commodity == "Copper" else "/lb"
            st.markdown(f"""
            <div class="market-item">
                <span>{commodity}</span>
                <span>${price:,}{unit}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 푸터
    st.markdown("""
    <div class="footer">
        SCM Risk Monitor | Real-time Global Supply Chain Risk Monitoring
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
