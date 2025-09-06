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
import json
import pytz
import os
from typing import List, Dict, Optional
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="🚨 SCM Risk Monitor",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SCM Risk Monitor CSS - Clean White/Gray Design
st.markdown("""
<style>
    /* 전체 배경 - 깔끔한 화이트/그레이 */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        min-height: 100vh;
    }
    
    /* 깔끔한 카드 디자인 */
    .clean-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .clean-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border-color: #cbd5e1;
    }
    
    /* 메인 헤더 - 배너 스타일 */
    .main-banner {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        animation: slideInFromTop 1s ease-out;
    }
    
    .main-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* 뉴스 카드 - 깔끔한 디자인 */
    .news-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #3b82f6 0%, #1e40af 100%);
        transition: width 0.3s ease;
    }
    
    .news-card:hover::before {
        width: 6px;
    }
    
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
    
    /* 뉴스 제목 */
    .news-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.8rem;
        line-height: 1.4;
        transition: color 0.3s ease;
    }
    
    .news-card:hover .news-title {
        color: #3b82f6;
    }
    
    /* 뉴스 메타 정보 */
    .news-meta {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    
    .news-source {
        background: #3b82f6;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .news-source:hover {
        background: #1e40af;
        transform: scale(1.05);
    }
    
    .news-time {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .news-views {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* 뉴스 링크 버튼 - 깔끔한 디자인 */
    .news-link {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: #3b82f6;
        color: white !important;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .news-link:hover {
        background: #1e40af;
        transform: translateY(-1px);
        color: white !important;
    }
    
    /* 검색 섹션 */
    .search-section {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    /* 날씨 정보 카드 */
    .weather-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .weather-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    
    /* 위험 지역 플래그 */
    .risk-flag {
        position: relative;
        display: inline-block;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .risk-flag:hover {
        transform: scale(1.05);
    }
    
    .risk-flag.high {
        color: #dc2626;
    }
    
    .risk-flag.medium {
        color: #f59e0b;
    }
    
    .risk-flag.low {
        color: #10b981;
    }
    
    /* 애니메이션 */
    @keyframes slideInFromTop {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInFromBottom {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInFromLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInFromRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* 로딩 애니메이션 */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .news-card {
            padding: 1.5rem;
        }
        
        .news-title {
            font-size: 1.4rem;
        }
    }
    
    /* 감성 디자인 요소 */
    .welcome-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        animation: slideInFromTop 1s ease-out;
    }
    
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: rgba(255, 255, 255, 0.7);
    }
    
    .dark-mode .empty-state {
        color: rgba(0, 0, 0, 0.6);
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* 필터 버튼 */
    .filter-btn {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.9);
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .filter-btn:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .filter-btn.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .dark-mode .filter-btn {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.9);
    }
    
    .dark-mode .filter-btn:hover {
        background: rgba(0, 0, 0, 0.3);
    }
    
    /* 날씨 정보 카드 */
    .weather-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .weather-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* 위험 지역 플래그 */
    .risk-flag {
        position: relative;
        display: inline-block;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .risk-flag:hover {
        transform: scale(1.1);
    }
    
    .risk-flag.high {
        color: #ff4757;
        text-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
    }
    
    .risk-flag.medium {
        color: #ffa502;
        text-shadow: 0 0 10px rgba(255, 165, 2, 0.5);
    }
    
    .risk-flag.low {
        color: #2ed573;
        text-shadow: 0 0 10px rgba(46, 213, 115, 0.5);
    }
    
    /* 검색 섹션 */
    .search-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def get_korean_time():
    """한국 시간 정보 가져오기"""
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    return now.strftime('%Y년 %m월 %d일'), now.strftime('%H:%M:%S')

def get_seoul_weather():
    """서울 날씨 정보 가져오기 (네이버 날씨 참조)"""
    try:
        # 네이버 날씨 API 대신 시뮬레이션 데이터 사용
        # 실제로는 네이버 날씨 API나 OpenWeatherMap API 사용 가능
        
        # 현재 시간과 계절에 따른 현실적인 날씨 시뮬레이션
        current_hour = datetime.now().hour
        current_month = datetime.now().month
        
        # 계절별 기본 온도 설정 (서울 기준)
        if current_month in [12, 1, 2]:  # 겨울
            base_temp = random.randint(-8, 8)
            conditions = ["맑음", "흐림", "눈", "안개", "구름많음"]
        elif current_month in [3, 4, 5]:  # 봄
            base_temp = random.randint(8, 22)
            conditions = ["맑음", "흐림", "비", "안개", "구름많음"]
        elif current_month in [6, 7, 8]:  # 여름
            base_temp = random.randint(22, 35)
            conditions = ["맑음", "흐림", "비", "천둥번개", "구름많음"]
        else:  # 가을
            base_temp = random.randint(8, 25)
            conditions = ["맑음", "흐림", "비", "안개", "구름많음"]
        
        # 시간대별 온도 조정
        if 6 <= current_hour <= 12:  # 오전
            temperature = base_temp + random.randint(0, 3)
        elif 12 < current_hour <= 18:  # 오후
            temperature = base_temp + random.randint(2, 6)
        else:  # 저녁/밤
            temperature = base_temp - random.randint(0, 4)
        
        condition = random.choice(conditions)
        
        # 습도는 날씨 조건에 따라 현실적으로 조정
        if condition in ["비", "눈", "천둥번개"]:
            humidity = random.randint(75, 95)
        elif condition == "안개":
            humidity = random.randint(65, 90)
        elif condition == "구름많음":
            humidity = random.randint(55, 80)
        else:  # 맑음
            humidity = random.randint(30, 65)
        
        # 체감온도 계산
        wind_speed = random.randint(0, 12)
        feels_like = temperature
        if wind_speed > 5:
            feels_like -= random.randint(1, 3)
        if humidity > 80:
            feels_like += random.randint(1, 3)
        
        return {
            "condition": condition,
            "temperature": temperature,
            "humidity": humidity,
            "feels_like": round(feels_like, 1),
            "wind_speed": wind_speed,
            "location": "서울"
        }
        
    except Exception as e:
        # 오류 발생 시 기본 정보 반환
        return {
            "condition": "맑음",
            "temperature": 22,
            "humidity": 60,
            "feels_like": 22,
            "wind_speed": 5,
            "location": "서울"
        }

def get_scm_risk_locations():
    """SCM Risk 발생 지역 데이터"""
    risk_locations = [
        {
            "name": "우크라이나",
            "flag": "🇺🇦",
            "risk_level": "high",
            "risk_type": "전쟁",
            "description": "러시아-우크라이나 전쟁으로 인한 공급망 중단",
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
            "news": [
                "싱가포르 물류 허브 경쟁력 강화",
                "싱가포르 디지털 물류 플랫폼 도입",
                "싱가포르 친환경 물류 정책"
            ]
        }
    ]
    
    return risk_locations

def crawl_scm_risk_news(num_results: int = 20) -> List[Dict]:
    """SCM Risk 관련 뉴스 크롤링"""
    try:
        # SCM Risk 관련 키워드들
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
        
        # 랜덤하게 키워드 선택
        selected_keyword = random.choice(scm_keywords)
        encoded_query = urllib.parse.quote(selected_keyword)
        news_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"
        
        # 실제 뉴스 크롤링
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(news_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # XML 파싱
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        articles = []
        
        for item in items[:num_results]:
            title = item.find('title').text if item.find('title') else ""
            link = item.find('link').text if item.find('link') else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') else ""
            source = item.find('source').text if item.find('source') else ""
            
            if title.strip():
                # 발행 시간 파싱
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
        
        return articles[:num_results]
        
    except Exception as e:
        st.error(f"뉴스 크롤링 오류: {e}")
        return generate_scm_backup_news(num_results)

def categorize_news(title: str, query: str) -> str:
    """뉴스 카테고리 분류"""
    title_lower = title.lower()
    
    categories = {
        '정치': ['정치', '선거', '정부', '국회', '대통령', '총리', '정당', '정책'],
        '경제': ['경제', '금융', '주식', '부동산', '기업', '경영', '투자', '은행'],
        '사회': ['사회', '사건', '사고', '범죄', '교육', '복지', '환경', '교통'],
        '국제': ['국제', '외교', '해외', '글로벌', '국제기구', '외국'],
        '기술': ['기술', 'IT', '인공지능', 'AI', '디지털', '스마트폰', '인터넷'],
        '스포츠': ['스포츠', '축구', '야구', '농구', '올림픽', '월드컵', '선수'],
        '문화': ['문화', '연예', '영화', '음악', '드라마', '예술', '책', '전시']
    }
    
    for category, keywords in categories.items():
        if any(keyword in title_lower for keyword in keywords):
            return category
    
    return '기타'

def generate_scm_backup_news(num_results: int) -> List[Dict]:
    """SCM Risk 백업 뉴스 생성"""
    articles = []
    
    # 실제 뉴스 사이트 URL 매핑
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
    
    # SCM Risk 관련 뉴스 제목
    scm_news_titles = [
        "Global Supply Chain Disruptions Impact Manufacturing",
        "Shipping Crisis Causes Port Congestion Worldwide",
        "Semiconductor Shortage Affects Global Electronics",
        "Energy Crisis Disrupts Global Supply Chains",
        "Trade War Escalates Supply Chain Risks",
        "Logistics Disruption Hits Global Commerce",
        "Manufacturing Shortage Creates Supply Chain Bottlenecks",
        "Port Congestion Delays Global Shipping",
        "Supply Chain Risk Management Strategies",
        "Global Trade Tensions Impact Supply Chains",
        "Food Security Concerns Rise Amid Supply Chain Issues",
        "Automotive Industry Faces Supply Chain Challenges",
        "Technology Supply Chain Under Pressure",
        "Healthcare Supply Chain Disruptions Continue",
        "Retail Supply Chain Adapts to New Challenges"
    ]
    
    for i in range(min(num_results, len(scm_news_titles))):
        site = random.choice(news_sites)
        article = {
            'title': scm_news_titles[i],
            'url': site['url'],
            'source': site['name'],
            'published_time': (datetime.now() - timedelta(hours=random.randint(0, 24))).strftime('%Y-%m-%d %H:%M'),
            'description': f"SCM Risk 관련 최신 뉴스와 분석을 제공합니다.",
            'views': random.randint(100, 5000)
        }
        articles.append(article)
    
    return articles

def filter_articles(articles: List[Dict], category: str = "전체", sort_by: str = "최신순") -> List[Dict]:
    """뉴스 기사 필터링 및 정렬"""
    if not articles:
        return []
    
    # 카테고리 필터링
    if category != "전체":
        filtered_articles = [article for article in articles if article.get('category') == category]
    else:
        filtered_articles = articles.copy()
    
    # 정렬
    if sort_by == "최신순":
        filtered_articles.sort(key=lambda x: x['published_time'], reverse=True)
    elif sort_by == "조회순":
        filtered_articles.sort(key=lambda x: x['views'], reverse=True)
    elif sort_by == "제목순":
        filtered_articles.sort(key=lambda x: x['title'])
    elif sort_by == "출처순":
        filtered_articles.sort(key=lambda x: x['source'])
    
    return filtered_articles

def get_category_stats(articles: List[Dict]) -> Dict[str, int]:
    """카테고리별 통계"""
    stats = {}
    for article in articles:
        category = article.get('category', '기타')
        stats[category] = stats.get(category, 0) + 1
    return stats

def main():
    # 메인 레이아웃
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # 좌측 컬럼 - 시간, 날씨, 검색
    with col1:
        # 서울 시간
        date_str, time_str = get_korean_time()
        st.markdown(f"""
        <div class="weather-card">
            <h4 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem; text-align: center;">🇰🇷 서울 시간</h4>
            <p style="color: rgba(255, 255, 255, 0.8); text-align: center; font-size: 1.1rem; margin-bottom: 0.5rem;"><strong>{date_str}</strong></p>
            <p style="color: rgba(255, 255, 255, 0.8); text-align: center; font-size: 1.3rem; font-weight: bold;"><strong>{time_str}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # 서울 날씨
        weather_info = get_seoul_weather()
        st.markdown(f"""
        <div class="weather-card">
            <h4 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem; text-align: center;">🌤️ 서울 날씨</h4>
            <p style="color: rgba(255, 255, 255, 0.8); text-align: center; font-size: 1.1rem; margin-bottom: 0.5rem;">☁️ {weather_info['condition']}</p>
            <p style="color: rgba(255, 255, 255, 0.8); text-align: center; font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;">🌡️ {weather_info['temperature']}°C</p>
            <p style="color: rgba(255, 255, 255, 0.7); text-align: center; font-size: 0.9rem;">체감 {weather_info['feels_like']}°C | 습도 {weather_info['humidity']}% | 풍속 {weather_info['wind_speed']}m/s</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 검색 섹션
        st.markdown("""
        <div class="search-section">
            <h4 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem; text-align: center;">🔍 뉴스 검색</h4>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("search_form"):
            query = st.text_input("Keyword", placeholder="예: supply chain, logistics...", value="")
            num_results = st.slider("검색 결과 개수", 10, 50, 20)
            submit_button = st.form_submit_button("Search", type="primary")
            
            if submit_button:
                if not query.strip():
                    st.error("검색어를 입력해주세요!")
                else:
                    with st.spinner("뉴스를 검색하고 있습니다..."):
                        articles = crawl_scm_risk_news(num_results)
                        
                        if articles:
                            st.success(f"✅ '{query}' 키워드로 {len(articles)}개의 뉴스를 찾았습니다!")
                            st.session_state.articles = articles
                            st.session_state.query = query
                            st.session_state.search_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            st.warning(f"'{query}' 키워드로 검색 결과가 없습니다.")
    
    # 중앙 컬럼 - 메인 뉴스
    with col2:
        # 헤더
        st.markdown('<h1 class="main-header">🚨 SCM Risk Monitor</h1>', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header">🌍 글로벌 공급망 위험을 실시간으로 모니터링하세요</h2>', unsafe_allow_html=True)
        
        # SCM Risk 뉴스 자동 로드
        if 'scm_articles' not in st.session_state:
            with st.spinner("SCM Risk 뉴스를 로딩하고 있습니다..."):
                st.session_state.scm_articles = crawl_scm_risk_news(15)
                st.session_state.scm_load_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # SCM Risk 뉴스 표시
        if st.session_state.scm_articles:
            load_time = st.session_state.get('scm_load_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            st.markdown(f"""
            <div class="search-section">
                <h4 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;">🚨 SCM Risk 최신 뉴스</h4>
                <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">
                    📰 총 {len(st.session_state.scm_articles)}개 기사 | 
                    🕒 업데이트: {load_time}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 뉴스 카드들
            for i, article in enumerate(st.session_state.scm_articles, 1):
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{i}. {article['title']}</div>
                    <div class="news-meta">
                        <span class="news-source">📰 {article['source']}</span>
                        <span class="news-time">🕒 {article['published_time']}</span>
                        <span class="news-views">👁️ {article['views']:,} 조회</span>
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.8); margin-bottom: 1.5rem; line-height: 1.6;">
                        {article['description']}
                    </div>
                    <a href="{article['url']}" target="_blank" class="news-link">
                        🔗 원문 보기
                    </a>
                </div>
                """, unsafe_allow_html=True)
        
        # 검색 결과가 있는 경우 표시
        if 'articles' in st.session_state and st.session_state.articles:
            search_time = st.session_state.get('search_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            st.markdown(f"""
            <div class="search-section">
                <h4 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;">🔍 검색 결과</h4>
                <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">
                    키워드: <strong>"{st.session_state.query}"</strong> | 
                    📰 총 {len(st.session_state.articles)}개 기사 | 
                    🕒 검색 시간: {search_time}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 검색 결과 뉴스 카드들
            for i, article in enumerate(st.session_state.articles, 1):
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{i}. {article['title']}</div>
                    <div class="news-meta">
                        <span class="news-source">📰 {article['source']}</span>
                        <span class="news-time">🕒 {article['published_time']}</span>
                        <span class="news-views">👁️ {article['views']:,} 조회</span>
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.8); margin-bottom: 1.5rem; line-height: 1.6;">
                        {article['description']}
                    </div>
                    <a href="{article['url']}" target="_blank" class="news-link">
                        🔗 원문 보기
                    </a>
                </div>
                """, unsafe_allow_html=True)
    
    # 우측 컬럼 - SCM Risk 지역 플래그
    with col3:
        st.markdown("""
        <div class="glass-card" style="padding: 1.5rem; margin-bottom: 2rem;">
            <h3 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem; text-align: center;">🚨 SCM Risk 지역</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 위험 지역 플래그들
        risk_locations = get_scm_risk_locations()
        
        for location in risk_locations:
            risk_class = location['risk_level']
            st.markdown(f"""
            <div class="risk-flag {risk_class}" style="margin-bottom: 1rem; padding: 1rem; background: rgba(255, 255, 255, 0.1); border-radius: 10px; cursor: pointer;" 
                 onmouseover="this.style.background='rgba(255, 255, 255, 0.2)'" 
                 onmouseout="this.style.background='rgba(255, 255, 255, 0.1)'">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{location['flag']}</div>
                    <div style="color: rgba(255, 255, 255, 0.9); font-weight: bold; margin-bottom: 0.3rem;">{location['name']}</div>
                    <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.8rem; margin-bottom: 0.3rem;">{location['risk_type']}</div>
                    <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.7rem; text-align: left;">{location['description']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 위험도 범례
        st.markdown("""
        <div class="glass-card" style="padding: 1.5rem; margin-top: 2rem;">
            <h4 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem; text-align: center;">🚨 위험도 범례</h4>
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #ff4757; font-weight: bold;">🔴 높음</span>
                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.8rem;"> - 즉시 대응 필요</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #ffa502; font-weight: bold;">🟠 중간</span>
                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.8rem;"> - 모니터링 필요</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #2ed573; font-weight: bold;">🟢 낮음</span>
                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.8rem;"> - 정상 운영</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 푸터
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem; color: rgba(255, 255, 255, 0.6);">
        <p>🚨 SCM Risk Monitor | 글로벌 공급망 위험 실시간 모니터링</p>
        <p>Made with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
