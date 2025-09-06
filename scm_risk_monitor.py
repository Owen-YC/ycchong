import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import numpy as np
import pytz
import logging
from markupsafe import escape
import folium
from streamlit_folium import st_folium
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

# CSS 스타일 (접근성 개선: 폰트 크기 확대, 대비 강화)
st.markdown("""
<style>
    .stApp {
        background: #fafafa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        animation: slideInFromTop 0.8s ease-out;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 3s infinite;
    }
    .main-title {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    .main-subtitle {
        font-size: 1rem;
        opacity: 0.8;
        margin: 0.25rem 0 0 0;
        position: relative;
        z-index: 1;
    }
    .unified-info-card {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }
    .unified-info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    .info-title {
        font-size: 1rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
        text-align: center;
    }
    .info-content {
        font-size: 0.9rem;
        color: #4b5e6a;
        margin: 0;
        text-align: center;
    }
    .search-section {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: fadeInUp 0.8s ease-out;
    }
    .stTextInput > div > div > input {
        border: 1px solid #e1e5e9 !important;
        border-radius: 6px !important;
        box-shadow: none !important;
        outline: none !important;
    }
    .stTextInput > div > div > input:focus {
        border: 1px solid #3498db !important;
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2) !important;
    }
    .stButton > button {
        background: #3498db !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: #2980b9 !important;
        transform: translateY(-1px) !important;
    }
    .news-item {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #3498db;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    .news-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(52, 152, 219, 0.1), transparent);
        transition: left 0.5s ease;
    }
    .news-item:hover::before {
        left: 100%;
    }
    .news-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        border-left-color: #2980b9;
    }
    .news-title {
        font-size: 1rem;
        font-weight: 500;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
        line-height: 1.3;
        transition: color 0.3s ease;
    }
    .news-item:hover .news-title {
        color: #2980b9;
    }
    .news-description {
        font-size: 0.85rem;
        color: #4b5e6a;
        margin: 0.25rem 0 0.5rem 0;
        line-height: 1.4;
        font-style: italic;
    }
    .news-meta {
        display: flex;
        gap: 0.75rem;
        font-size: 0.8rem;
        color: #4b5e6a;
        margin-bottom: 0.5rem;
    }
    .news-source {
        background: #3498db;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 3px;
        font-size: 0.8rem;
        transition: all 0.3s ease;
    }
    .news-source:hover {
        background: #2980b9;
        transform: scale(1.05);
    }
    .news-link {
        color: #3498db;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .news-link:hover {
        color: #2980b9;
        transform: translateX(2px);
    }
    .map-wrapper {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: fadeInUp 0.8s ease-out;
        overflow: hidden;
        max-width: 100%;
    }
    .map-container {
        max-width: 100%;
        overflow: hidden;
    }
    .risk-item {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.4rem;
        margin-bottom: 0.4rem;
        font-size: 0.8rem;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
        position: relative;
    }
    .risk-item:hover {
        transform: scale(1.02);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .risk-high { border-left: 3px solid #e74c3c; }
    .risk-medium { border-left: 3px solid #f39c12; }
    .risk-low { border-left: 3px solid #27ae60; }
    .risk-title {
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.2rem 0;
        font-size: 0.85rem;
    }
    .risk-desc {
        color: #4b5e6a;
        margin: 0;
        font-size: 0.8rem;
    }
    .cute-flag {
        display: inline-block;
        animation: wave 2s ease-in-out infinite;
        transform-origin: bottom center;
    }
    .market-info {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.6rem;
        margin-bottom: 0.5rem;
        font-size: 0.8rem;
        animation: fadeInUp 0.6s ease-out;
    }
    .market-title {
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.25rem 0;
        font-size: 0.9rem;
    }
    .market-item {
        display: flex;
        justify-content: space-between;
        margin: 0.15rem 0;
        color: #4b5e6a;
        font-size: 0.8rem;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.75rem 0;
        padding-bottom: 0.25rem;
        border-bottom: 2px solid #3498db;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: #4b5e6a;
        font-size: 0.9rem;
    }
    @keyframes slideInFromTop {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    @keyframes wave {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(10deg); }
        75% { transform: rotate(-10deg); }
    }
</style>
""", unsafe_allow_html=True)

def get_korean_time():
    """한국 시간 정보 가져오기"""
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    return now.strftime('%Y년 %m월 %d일'), now.strftime('%H:%M:%S')

def get_seoul_weather():
    """서울 날씨 정보 가져오기 (OpenWeatherMap API)"""
    try:
        api_key = "YOUR_OPENWEATHERMAP_API_KEY"  # 실제 API 키로 교체
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={api_key}&units=metric&lang=kr"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "condition": data["weather"][0]["description"],
            "temperature": round(data["main"]["temp"], 1),
            "humidity": data["main"]["humidity"],
            "feels_like": round(data["main"]["feels_like"], 1),
            "wind_speed": round(data["wind"]["speed"], 1),
            "location": "서울"
        }
    except Exception as e:
        logging.error(f"Weather API error: {e}")
        st.error("날씨 데이터를 불러오지 못했습니다. 기본 데이터를 표시합니다.")
        return {
            "condition": "맑음",
            "temperature": 22,
            "humidity": 60,
            "feels_like": 22,
            "wind_speed": 5,
            "location": "서울"
        }

def get_exchange_rates():
    """실시간 환율 정보 가져오기 (시뮬레이션, 실제 API 주석)"""
    try:
        # 실제 API 예시 (ExchangeRate-API):
        # api_key = "YOUR_EXCHANGERATE_API_KEY"
        # url = f"https://api.exchangerate-api.com/v4/latest/USD"
        # response = requests.get(url)
        # data = response.json()
        # rates = {"USD/KRW": data["rates"]["KRW"], ...}
        
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
    """주요 광물 시세 가져오기 (시뮬레이션, 실제 API 주석)"""
    try:
        # 실제 API 예시 (Quandl):
        # api_key = "YOUR_QUANDL_API_KEY"
        # url = f"https://www.quandl.com/api/v3/datasets/LME/{commodity}"
        # response = requests.get(url)
        # data = response.json()
        
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
    """SCM Risk 지도 생성"""
    risk_locations = get_scm_risk_locations()
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='CartoDB positron'
    )
    risk_colors = {
        "high": "#dc2626",
        "medium": "#f59e0b",
        "low": "#10b981"
    }
    for location in risk_locations:
        news_links_html = ""
        for i, news in enumerate(location['news'], 1):
            news_links_html += f"""
            <div style="margin: 8px 0; padding: 8px; background: #f8fafc; border-radius: 6px; border-left: 3px solid #3b82f6;">
                <div style="color: #1e40af; font-size: 12px; font-weight: 500;">
                    {i}. {news}
                </div>
            </div>
            """
        popup_html = f"""
        <div style="width: 300px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            <div style="display: flex; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid {risk_colors[location['risk_level']]};">
                <span style="font-size: 24px; margin-right: 8px;">{location['flag']}</span>
                <div>
                    <h4 style="margin: 0; color: #1e293b; font-size: 16px; font-weight: 700;">{location['name']}</h4>
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                        <span style="background: {risk_colors[location['risk_level']]}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">
                            {location['risk_level'].upper()} 위험
                        </span>
                        <span style="background: #64748b; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">
                            {location['risk_type']}
                        </span>
                    </div>
                    <div style="margin-top: 4px;">
                        <span style="color: #64748b; font-size: 11px;">{location['description']}</span>
                    </div>
                </div>
            </div>
            <div style="margin-top: 12px;">
                <h5 style="margin: 0 0 8px 0; color: #1e40af; font-size: 14px; font-weight: 600;">📰 관련 뉴스</h5>
                {news_links_html}
            </div>
        </div>
        """
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=folium.Popup(popup_html, max_width=350),
            icon=folium.Icon(
                color=risk_colors[location['risk_level']],
                icon='info-sign',
                prefix='fa'
            ),
            tooltip=f"{location['flag']} {location['name']} - {location['risk_level'].upper()} 위험"
        ).add_to(m)
    return m, risk_locations

@st.cache_data(ttl=3600)  # 1시간 캐싱
def crawl_scm_risk_news(num_results: int = 20, search_query: str = None) -> List[Dict]:
    """SCM Risk 관련 뉴스 크롤링"""
    try:
        if search_query:
            enhanced_query = f"{search_query} supply chain OR logistics OR manufacturing OR shipping"
            encoded_query = urllib.parse.quote(enhanced_query)
        else:
            scm_keywords = [
                "supply chain risk",
                "logistics disruption",
                "global supply chain",
                "manufacturing shortage",
                "shipping crisis",
                "port congestion",
                "trade war",
                "semiconductor shortage",
                "energy crisis",
                "food security"
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
                article = {
                    'title': title,
                    'url': link,
                    'source': source,
                    'published_time': formatted_date,
                    'description': f"{title} - {source}에서 제공하는 SCM Risk 관련 뉴스입니다.",
                    'views': random.randint(100, 5000)
                }
                articles.append(article)
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
        },
        {
            "title": "Energy Crisis Disrupts Global Supply Chains",
            "description": "에너지 위기로 인한 전력 부족이 공급망 전반에 걸쳐 영향을 주고 있습니다."
        },
        {
            "title": "Trade War Escalates Supply Chain Risks",
            "description": "무역 분쟁 심화로 글로벌 공급망의 불확실성이 증가하고 있습니다."
        },
        {
            "title": "Logistics Disruption Hits Global Commerce",
            "description": "물류 혼잡으로 인한 배송 지연이 전 세계 상거래에 영향을 미치고 있습니다."
        },
        {
            "title": "Manufacturing Shortage Creates Supply Chain Bottlenecks",
            "description": "제조업 부품 부족으로 인한 공급망 병목 현상이 심화되고 있습니다."
        },
        {
            "title": "Port Congestion Delays Global Shipping",
            "description": "항구 혼잡으로 인한 해상 운송 지연이 전 세계적으로 확산되고 있습니다."
        },
        {
            "title": "Supply Chain Risk Management Strategies",
            "description": "기업들이 공급망 위험 관리 전략을 강화하고 있습니다."
        },
        {
            "title": "Global Trade Tensions Impact Supply Chains",
            "description": "글로벌 무역 긴장으로 인한 공급망 불안정성이 지속되고 있습니다."
        },
        {
            "title": "Food Security Concerns Rise Amid Supply Chain Issues",
            "description": "공급망 문제로 인한 식량 안보 우려가 전 세계적으로 확산되고 있습니다."
        },
        {
            "title": "Automotive Industry Faces Supply Chain Challenges",
            "description": "자동차 산업이 공급망 위기로 인한 생산 중단을 겪고 있습니다."
        },
        {
            "title": "Technology Supply Chain Under Pressure",
            "description": "기술 산업의 공급망이 심각한 압박을 받고 있습니다."
        },
        {
            "title": "Healthcare Supply Chain Disruptions Continue",
            "description": "의료용품 공급망 중단이 지속되며 의료 서비스에 영향을 주고 있습니다."
        },
        {
            "title": "Retail Supply Chain Adapts to New Challenges",
            "description": "소매업계가 새로운 공급망 도전에 적응하고 있습니다."
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
        color_discrete_map={"high": "#dc2626", "medium": "#f59e0b", "low": "#10b981"}
    )
    return fig

def main():
    # 메인 헤더
    st.markdown("""
    <div class="main-header">
        <div class="main-title">SCM Risk Monitor</div>
        <div class="main-subtitle">Global Supply Chain Risk Monitoring</div>
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
            <div class="info-title">🇰🇷 Seoul Info</div>
            <div class="info-content">
                <strong>{date_str}</strong><br>
                <strong style="font-size: 1.1rem;">{time_str}</strong><br><br>
                ☁️ {weather_info['condition']}<br>
                <strong>{weather_info['temperature']}°C</strong><br>
                체감 {weather_info['feels_like']}°C
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 검색 기능
        st.markdown("""
        <div class="search-section">
            <h4 style="font-size: 1rem; margin: 0 0 0.5rem 0; color: #2c3e50;">🔍 Search</h4>
        </div>
        """, unsafe_allow_html=True)
        search_query = st.text_input("", placeholder="Search SCM news...", key="search_input")
        if st.button("Search", key="search_button"):
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

        # 뉴스 헤더
        if st.session_state.scm_articles:
            load_time = st.session_state.get('scm_load_time', datetime.now().strftime('%H:%M'))
            search_status = ""
            if 'search_query' in st.session_state and st.session_state.search_query:
                search_status = f" | 🔍 검색어: {escape(st.session_state.search_query)}"
            st.markdown(f"""
            <div class="unified-info-card">
                <h3 class="section-header">SCM Risk 뉴스 ({len(st.session_state.scm_articles)}개)</h3>
                <p style="font-size: 0.9rem; color: #4b5e6a; margin: 0;">최근 업데이트: {load_time}{search_status}</p>
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
            st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
            st_folium(risk_map, width=320, height=220, returned_objects=[])
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            logging.error(f"Map rendering error: {e}")
            st.error(f"지도 렌더링 오류: {e}")

        st.markdown("""
        <div class="market-info">
            <div class="market-title">🚩 리스크 수준</div>
            <div class="risk-item risk-high">
                <div class="risk-title"><span class="cute-flag">🔴</span> 고위험</div>
                <div class="risk-desc">즉각적인 조치 필요</div>
            </div>
            <div class="risk-item risk-medium">
                <div class="risk-title"><span class="cute-flag">🟠</span> 중위험</div>
                <div class="risk-desc">면밀히 모니터링 필요</div>
            </div>
            <div class="risk-item risk-low">
                <div class="risk-title"><span class="cute-flag">🟢</span> 저위험</div>
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
            unit = ""
            if commodity in ["Gold", "Silver"]:
                unit = "/oz"
            elif commodity == "Oil":
                unit = "/barrel"
            elif commodity == "Copper":
                unit = "/ton"
            elif commodity == "Uranium":
                unit = "/lb"
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
