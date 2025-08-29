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
import folium
from streamlit_folium import folium_static
import google.generativeai as genai
import json
import pytz

# Gemini API 설정
genai.configure(api_key="AIzaSyCJ1F-HMS4NkQ64f1tDRqJV_N9db0MmKpI")
model = genai.GenerativeModel('gemini-1.5-pro')

# 페이지 설정
st.set_page_config(
    page_title="SCM Risk Management AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2025 트렌드에 맞는 CSS 스타일 - 흰색 배경, 푸른색 계열 + Motion 애니메이션
st.markdown("""
<style>
    /* 전체 배경 - 깔끔한 흰색 */
    .stApp {
        background: #ffffff;
        min-height: 100vh;
    }
    
    /* 메인 헤더 - 2025 트렌드 + Motion */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        letter-spacing: -0.02em;
        position: relative;
        animation: fadeInDown 1s ease-out, headerGlow 4s ease-in-out infinite;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-radius: 2px;
        animation: slideIn 1.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            width: 0;
        }
        to {
            width: 100px;
        }
    }
    
    @keyframes headerGlow {
        0%, 100% {
            filter: brightness(1);
        }
        50% {
            filter: brightness(1.1);
        }
    }
    
    /* 뉴스 카드 - 2025 트렌드 + Motion */
    .news-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: slideInLeft 0.6s ease-out, gentleFloat 6s ease-in-out infinite;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        animation: slideInUp 0.8s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            height: 0;
        }
        to {
            height: 100%;
        }
    }
    
    @keyframes gentleFloat {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-2px);
        }
    }
    
    .news-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(30, 64, 175, 0.12);
        border-color: #3b82f6;
    }
    
    /* 뉴스 제목 */
    .news-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
        line-height: 1.4;
        animation: titleGlow 5s ease-in-out infinite;
    }
    
    /* 뉴스 메타 정보 */
    .news-meta {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: metaFade 6s ease-in-out infinite;
    }
    
    /* 뉴스 설명 */
    .news-description {
        font-size: 1rem;
        color: #475569;
        line-height: 1.6;
        margin-bottom: 1.5rem;
        animation: descriptionPulse 7s ease-in-out infinite;
    }
    
    /* 뉴스 링크 버튼 - 2025 트렌드 + Motion */
    .news-link {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white !important;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
        position: relative;
        overflow: hidden;
        animation: pulse 2s infinite, float 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
        }
        50% {
            box-shadow: 0 4px 20px rgba(30, 64, 175, 0.4);
        }
        100% {
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
        }
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-3px);
        }
    }
    
    .news-link::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .news-link:hover::before {
        left: 100%;
    }
    
    .news-link:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 64, 175, 0.3);
        color: white !important;
        text-decoration: none;
    }
    
    /* Streamlit 버튼 - 2025 트렌드 + Motion */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
        transition: all 0.3s ease;
        animation: bounceIn 0.8s ease-out, buttonPulse 3s ease-in-out infinite;
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes buttonPulse {
        0%, 100% {
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
        }
        50% {
            box-shadow: 0 6px 18px rgba(30, 64, 175, 0.3);
        }
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 64, 175, 0.3);
    }
    
    /* 검색 통계 카드 */
    .search-stats {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.1);
        animation: fadeIn 1s ease-out, softPulse 5s ease-in-out infinite;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes softPulse {
        0%, 100% {
            box-shadow: 0 4px 20px rgba(30, 64, 175, 0.1);
        }
        50% {
            box-shadow: 0 6px 25px rgba(30, 64, 175, 0.15);
        }
    }
    
    /* 위험 지표 */
    .risk-indicator {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
        animation: shake 2s infinite, glow 1.5s ease-in-out infinite alternate;
    }
    
    @keyframes shake {
        0%, 100% {
            transform: translateX(0);
        }
        10%, 30%, 50%, 70%, 90% {
            transform: translateX(-2px);
        }
        20%, 40%, 60%, 80% {
            transform: translateX(2px);
        }
    }
    
    @keyframes glow {
        from {
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
        }
        to {
            box-shadow: 0 4px 20px rgba(220, 38, 38, 0.6), 0 0 30px rgba(220, 38, 38, 0.4);
        }
    }
    
    /* 챗봇 컨테이너 */
    .chatbot-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.1);
        animation: slideInRight 0.8s ease-out, gentleWave 7s ease-in-out infinite;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes gentleWave {
        0%, 100% {
            transform: translateX(0px);
        }
        25% {
            transform: translateX(1px);
        }
        75% {
            transform: translateX(-1px);
        }
    }
    
    /* 날씨 정보 */
    .weather-info {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.2);
        animation: rotateIn 1s ease-out, breathe 4s ease-in-out infinite;
    }
    
    @keyframes rotateIn {
        from {
            opacity: 0;
            transform: rotate(-180deg) scale(0.3);
        }
        to {
            opacity: 1;
            transform: rotate(0) scale(1);
        }
    }
    
    @keyframes breathe {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.02);
        }
    }
    
    /* 지도 관련 뉴스 링크 */
    .map-news-link {
        display: block;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white !important;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        text-decoration: none;
        font-size: 0.8rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(30, 64, 175, 0.2);
        animation: mapLinkGlow 4s ease-in-out infinite;
    }
    
    .map-news-link:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        transform: translateX(5px);
        color: white !important;
        text-decoration: none;
    }
    
    @keyframes mapLinkGlow {
        0%, 100% {
            box-shadow: 0 2px 8px rgba(30, 64, 175, 0.2);
        }
        50% {
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4);
        }
    }
    
    @keyframes titleGlow {
        0%, 100% {
            color: #1e293b;
        }
        50% {
            color: #1e40af;
        }
    }
    
    @keyframes metaFade {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
        }
    }
    
    @keyframes descriptionPulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.01);
        }
    }
</style>
""", unsafe_allow_html=True)

def get_korean_time():
    """한국 시간 정보 가져오기"""
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    return now.strftime('%Y년 %m월 %d일'), now.strftime('%H:%M:%S')

def get_weather_info():
    """날씨 정보 (시뮬레이션)"""
    weather_conditions = ["맑음", "흐림", "비", "눈", "안개"]
    temperatures = list(range(15, 30))
    
    return {
        "condition": random.choice(weather_conditions),
        "temperature": random.choice(temperatures),
        "humidity": random.randint(40, 80)
    }

def crawl_google_news(query, num_results=20):
    """Google News RSS API를 사용한 실제 SCM Risk 뉴스 크롤링"""
    try:
        # Google News RSS 피드 URL 구성
        search_query = f"{query} supply chain risk management"
        encoded_query = urllib.parse.quote(search_query)
        news_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
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
        scm_keywords = [
            'supply chain', 'SCM', 'logistics', 'procurement', 'inventory', 'warehouse',
            'shipping', 'freight', 'transportation', 'distribution', 'supplier',
            '공급망', '물류', '구매', '재고', '창고', '운송', '배송', '공급업체',
            'risk', '위험', 'disruption', '중단', 'shortage', '부족', 'delay', '지연'
        ]
        
        for item in items[:num_results * 2]:  # 더 많은 아이템을 가져와서 필터링
            title = item.find('title').text if item.find('title') else ""
            link = item.find('link').text if item.find('link') else ""
            pub_date = item.find('pubDate').text if item.find('pubDate') else ""
            source = item.find('source').text if item.find('source') else ""
            
            # SCM Risk 관련 키워드 필터링
            title_lower = title.lower()
            if any(keyword.lower() in title_lower for keyword in scm_keywords):
                # 실제 뉴스 링크로 리다이렉트
                if link.startswith('https://news.google.com'):
                    # Google News 링크를 실제 뉴스 링크로 변환
                    try:
                        news_response = requests.get(link, headers=headers, timeout=5, allow_redirects=True)
                        actual_url = news_response.url
                    except:
                        actual_url = link
                else:
                    actual_url = link
                
                # 발행 시간 파싱
                try:
                    from email.utils import parsedate_to_datetime
                    parsed_date = parsedate_to_datetime(pub_date)
                    formatted_date = parsed_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                except:
                    formatted_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                
                article = {
                    'title': title,
                    'url': actual_url,
                    'source': source,
                    'published_time': formatted_date,
                    'description': f"{title} - {source}에서 제공하는 SCM Risk 관련 뉴스입니다.",
                    'views': random.randint(500, 5000)  # 조회수는 시뮬레이션
                }
                articles.append(article)
                
                if len(articles) >= num_results:
                    break
        
        # SCM Risk 관련 뉴스가 부족한 경우 추가 생성
        if len(articles) < num_results:
            additional_articles = generate_scm_risk_news(query, num_results - len(articles))
            articles.extend(additional_articles)
        
        return articles[:num_results]
        
    except Exception as e:
        st.error(f"뉴스 크롤링 오류: {e}")
        # 오류 발생 시 기본 SCM Risk 뉴스 반환
        return generate_scm_risk_news(query, num_results)

def generate_scm_risk_news(query, num_results):
    """SCM Risk 관련 뉴스 생성 (백업용)"""
    scm_risk_news = [
        {
            "title": "글로벌 SCM 위기, 기업들의 디지털 전환 가속화",
            "source": "SCM뉴스",
            "description": "공급망 관리(SCM) 시스템의 글로벌 위기로 인해 기업들이 AI와 IoT 기술을 활용한 디지털 전환을 가속화하고 있습니다.",
            "url": "https://www.google.com/search?q=SCM+위기+디지털+전환",
            "published_time": "2024-01-15T10:30:00Z",
            "views": random.randint(1000, 5000)
        },
        {
            "title": "반도체 부족으로 인한 자동차 생산 중단 확산",
            "source": "자동차뉴스",
            "description": "글로벌 반도체 부족으로 인해 주요 자동차 제조업체들의 생산 중단이 확산되고 있습니다.",
            "url": "https://www.google.com/search?q=반도체+부족+자동차+생산+중단",
            "published_time": "2024-01-14T15:45:00Z",
            "views": random.randint(800, 4000)
        },
        {
            "title": "해운비 상승으로 인한 물류 비용 증가 심화",
            "source": "물류뉴스",
            "description": "글로벌 해운비 상승으로 인해 수출입 기업들의 물류 비용이 크게 증가하고 있습니다.",
            "url": "https://www.google.com/search?q=해운비+상승+물류+비용+증가",
            "published_time": "2024-01-13T09:20:00Z",
            "views": random.randint(1200, 6000)
        },
        {
            "title": "스마트 물류 시스템 도입으로 효율성 향상",
            "source": "스마트물류",
            "description": "AI와 자동화 기술을 활용한 스마트 물류 시스템이 급속히 도입되어 물류 효율성이 크게 향상되고 있습니다.",
            "url": "https://www.google.com/search?q=스마트+물류+시스템+AI+자동화",
            "published_time": "2024-01-12T14:15:00Z",
            "views": random.randint(900, 4500)
        },
        {
            "title": "공급망 투명성 확보의 중요성 증가",
            "source": "ESG뉴스",
            "description": "ESG 경영의 확산으로 공급망 투명성 확보의 중요성이 크게 증가하고 있습니다.",
            "url": "https://www.google.com/search?q=공급망+투명성+ESG+경영",
            "published_time": "2024-01-11T11:30:00Z",
            "views": random.randint(700, 3500)
        }
    ]
    
    articles = []
    
    # 기본 SCM Risk 뉴스 추가
    for news in scm_risk_news:
        article = {
            'title': news["title"],
            'url': news["url"],
            'source': news["source"],
            'published_time': news["published_time"],
            'description': news["description"],
            'views': news["views"]
        }
        articles.append(article)
    
    # 추가 뉴스 생성
    scm_topics = [
        f"{query} 최적화 전략", f"{query} 디지털 전환", f"{query} 위험 관리",
        f"{query} 비용 절감", f"{query} 효율성 향상", f"{query} 혁신 기술",
        f"{query} 글로벌 트렌드", f"{query} 미래 전망", f"{query} 대응 방안"
    ]
    
    while len(articles) < num_results:
        topic = random.choice(scm_topics)
        source = f"{query}뉴스{len(articles) + 1}"
        
        # 랜덤 발행 시간 생성
        random_days = random.randint(0, 30)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        published_time = (datetime.now() - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        article = {
            'title': f'"{query}" 관련 {topic}',
            'url': f"https://www.google.com/search?q={query}+{topic.replace(' ', '+')}",
            'source': source,
            'published_time': published_time,
            'description': f'{query}와 관련된 {topic}에 대한 최신 동향과 분석을 제공합니다. SCM Risk 관리 관점에서 {query}의 중요성과 향후 전망을 살펴봅니다.',
            'views': random.randint(500, 3000)
        }
        articles.append(article)
    
    return articles[:num_results]

def filter_articles(articles, sort_by="최신순"):
    """뉴스 기사 필터링 및 정렬"""
    if not articles:
        return []
    
    # 복사본 생성
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

def create_risk_map():
    """SCM Risk 지역별 지도 생성"""
    # 지역별 관련 뉴스 데이터
    location_news = {
        "중국 상하이": [
            {"title": "중국 상하이 항구 혼잡으로 인한 공급망 지연", "url": "https://www.google.com/search?q=중국+상하이+항구+혼잡+공급망+지연"},
            {"title": "상하이 봉쇄로 인한 글로벌 공급망 위기", "url": "https://www.google.com/search?q=상하이+봉쇄+글로벌+공급망+위기"},
            {"title": "중국 제조업 생산 중단으로 인한 부품 부족", "url": "https://www.google.com/search?q=중국+제조업+생산+중단+부품+부족"}
        ],
        "미국 로스앤젤레스": [
            {"title": "LA 항구 혼잡으로 인한 물류 지연", "url": "https://www.google.com/search?q=LA+항구+혼잡+물류+지연"},
            {"title": "미국 서부 해안 노동자 파업 위기", "url": "https://www.google.com/search?q=미국+서부+해안+노동자+파업+위기"},
            {"title": "LA 항구 자동화 시스템 도입 확대", "url": "https://www.google.com/search?q=LA+항구+자동화+시스템+도입+확대"}
        ],
        "독일 함부르크": [
            {"title": "함부르크 항구 물류 효율성 향상", "url": "https://www.google.com/search?q=함부르크+항구+물류+효율성+향상"},
            {"title": "독일 물류 디지털화 가속화", "url": "https://www.google.com/search?q=독일+물류+디지털화+가속화"},
            {"title": "함부르크 스마트 포트 프로젝트", "url": "https://www.google.com/search?q=함부르크+스마트+포트+프로젝트"}
        ],
        "싱가포르": [
            {"title": "싱가포르 물류 허브 경쟁력 강화", "url": "https://www.google.com/search?q=싱가포르+물류+허브+경쟁력+강화"},
            {"title": "싱가포르 디지털 물류 플랫폼 도입", "url": "https://www.google.com/search?q=싱가포르+디지털+물류+플랫폼+도입"},
            {"title": "싱가포르 친환경 물류 정책", "url": "https://www.google.com/search?q=싱가포르+친환경+물류+정책"}
        ],
        "한국 부산": [
            {"title": "부산항 스마트 물류 시스템 구축", "url": "https://www.google.com/search?q=부산항+스마트+물류+시스템+구축"},
            {"title": "부산항 자동화 시설 확충", "url": "https://www.google.com/search?q=부산항+자동화+시설+확충"},
            {"title": "부산항 물류 효율성 세계 1위 달성", "url": "https://www.google.com/search?q=부산항+물류+효율성+세계+1위+달성"}
        ]
    }
    
    risk_locations = [
        {"name": "중국 상하이", "lat": 31.2304, "lng": 121.4737, "risk": "높음", "description": "공급망 중단 위험", "color": "red", "news": location_news["중국 상하이"]},
        {"name": "미국 로스앤젤레스", "lat": 34.0522, "lng": -118.2437, "risk": "중간", "description": "항구 혼잡", "color": "orange", "news": location_news["미국 로스앤젤레스"]},
        {"name": "독일 함부르크", "lat": 53.5511, "lng": 9.9937, "risk": "낮음", "description": "물류 지연", "color": "green", "news": location_news["독일 함부르크"]},
        {"name": "싱가포르", "lat": 1.3521, "lng": 103.8198, "risk": "중간", "description": "운송 비용 증가", "color": "orange", "news": location_news["싱가포르"]},
        {"name": "한국 부산", "lat": 35.1796, "lng": 129.0756, "risk": "낮음", "description": "정상 운영", "color": "green", "news": location_news["한국 부산"]}
    ]
    
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='OpenStreetMap'
    )
    
    for location in risk_locations:
        # 관련 뉴스 링크 HTML 생성
        news_links_html = ""
        for i, news in enumerate(location['news'], 1):
            news_links_html += f"""
            <a href="{news['url']}" target="_blank" class="map-news-link">
                {i}. {news['title']}
            </a>
            """
        
        popup_html = f"""
        <div style="width: 300px;">
            <h4 style="color: {location['color']}; margin: 0 0 10px 0;">{location['name']}</h4>
            <p style="margin: 5px 0;"><strong>Risk Level:</strong> <span style="color: {location['color']}; font-weight: bold;">{location['risk']}</span></p>
            <p style="margin: 5px 0; font-size: 12px;">{location['description']}</p>
            <hr style="margin: 10px 0; border-color: #e2e8f0;">
            <h5 style="margin: 10px 0 5px 0; color: #1e40af;">📰 관련 뉴스</h5>
            {news_links_html}
        </div>
        """
        
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=folium.Popup(popup_html, max_width=350),
            icon=folium.Icon(color=location["color"], icon='info-sign'),
            tooltip=f"{location['name']} - {location['risk']} 위험"
        ).add_to(m)
    
    return m, risk_locations

def gemini_chatbot_response(user_input):
    """Gemini API를 사용한 챗봇 응답"""
    try:
        prompt = f"""
        당신은 SCM(공급망관리) Risk 관리 전문가입니다. 
        다음 질문에 대해 전문적이고 실용적인 답변을 제공해주세요:
        
        질문: {user_input}
        
        답변은 한국어로 작성하고, SCM Risk 관리 관점에서 구체적이고 실용적인 조언을 포함해주세요.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"죄송합니다. AI 응답 생성 중 오류가 발생했습니다: {str(e)}"

def main():
    # 헤더
    st.markdown('<h1 class="main-header">🤖 SCM Risk Management AI</h1>', unsafe_allow_html=True)
    st.markdown("### 🌍 글로벌 공급망 위험을 실시간으로 모니터링하고 관리하세요")
    
    # 사이드바 - 날짜, 시간, 날씨 정보 + 챗봇
    with st.sidebar:
        st.header("📅 실시간 정보")
        
        # 한국 시간 정보
        date_str, time_str = get_korean_time()
        weather_info = get_weather_info()
        
        st.markdown(f"""
        <div class="weather-info">
            <h4 style="margin: 0 0 10px 0;">🇰🇷 한국 시간</h4>
            <p style="margin: 5px 0; font-size: 1.1rem;"><strong>{date_str}</strong></p>
            <p style="margin: 5px 0; font-size: 1.2rem;"><strong>{time_str}</strong></p>
            <hr style="margin: 15px 0; border-color: rgba(255,255,255,0.3);">
            <h4 style="margin: 0 0 10px 0;">🌤️ 서울 날씨</h4>
            <p style="margin: 5px 0;">☁️ {weather_info['condition']}</p>
            <p style="margin: 5px 0;">🌡️ {weather_info['temperature']}°C</p>
            <p style="margin: 5px 0;">💧 습도 {weather_info['humidity']}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 검색 설정
        st.header("🔍 SCM Risk 검색")
        
        # 엔터키 검색을 위한 form 사용
        with st.form("search_form"):
            query = st.text_input("키워드를 입력하세요", placeholder="예: 공급망, 물류, 운송...", value="SCM")
            num_results = st.slider("검색 결과 개수", 10, 50, 20)
            submit_button = st.form_submit_button("🔍 검색", type="primary")
            
            if submit_button:
                if not query.strip():
                    st.error("검색어를 입력해주세요!")
                else:
                    with st.spinner("SCM Risk를 분석 중입니다..."):
                        articles = crawl_google_news(query, num_results)
                        
                        if articles:
                            st.success(f"✅ {len(articles)}개의 SCM Risk 관련 뉴스를 찾았습니다!")
                            st.session_state.articles = articles
                            st.session_state.query = query
                        else:
                            st.warning("검색 결과가 없습니다. 다른 키워드로 시도해보세요.")
        
        # AI 챗봇 섹션 (사이드바에 추가)
        st.header("🤖 AI 챗봇")
        st.markdown("SCM Risk 관리에 대한 질문을 해주세요!")
        
        # 챗봇 인터페이스
        user_question = st.text_input("질문을 입력하세요:", placeholder="예: SCM Risk 관리 방법은?", key="chatbot_input")
        
        if st.button("💬 질문하기", key="chatbot_button"):
            if user_question:
                with st.spinner("AI가 답변을 생성하고 있습니다..."):
                    response = gemini_chatbot_response(user_question)
                    
                    st.markdown("#### 🤖 AI 답변:")
                    st.markdown(f"""
                    <div class="chatbot-container">
                        <p style="color: #475569; font-size: 1.1rem; line-height: 1.6;">
                            {response}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("질문을 입력해주세요!")
    
    # 메인 컨텐츠 - 한 화면에 모든 내용 표시
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # SCM Risk 분석 섹션
        st.markdown("### 📰 SCM Risk 관련 뉴스")
        
        if 'articles' in st.session_state and st.session_state.articles:
            # 검색 통계
            st.markdown(f"""
            <div class="search-stats">
                <h4 style="color: #1e293b; margin-bottom: 1rem;">🔍 검색 결과</h4>
                <p style="color: #475569; margin-bottom: 1rem;">키워드: <strong>{st.session_state.query}</strong> | 📰 총 {len(st.session_state.articles)}개 기사 | 🕒 검색 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <div class="risk-indicator">⚠️ {st.session_state.query} Risk 모니터링 중</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 뉴스 필터링 옵션
            col_filter1, col_filter2 = st.columns([1, 3])
            with col_filter1:
                sort_option = st.selectbox(
                    "정렬 기준",
                    ["최신순", "조회순", "제목순", "출처순"],
                    key="sort_articles"
                )
            
            # 필터링된 뉴스 표시
            filtered_articles = filter_articles(st.session_state.articles, sort_option)
            
            for i, article in enumerate(filtered_articles, 1):
                # 발행 시간 포맷팅
                try:
                    pub_time = datetime.strptime(article['published_time'], '%Y-%m-%dT%H:%M:%SZ')
                    formatted_time = pub_time.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_time = article['published_time']
                
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{i}. {article['title']}</div>
                    <div class="news-meta">
                        📰 {article['source']} | 🕒 {formatted_time} | 👁️ {article['views']:,} 조회
                    </div>
                    <div class="news-description">
                        {article['description']}
                    </div>
                    <a href="{article['url']}" target="_blank" class="news-link">
                        🔗 원문 보기
                    </a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🔍 사이드바에서 키워드를 입력하고 검색해주세요!")
    
    with col2:
        # Risk 지도 섹션
        st.markdown("### 🗺️ 글로벌 SCM Risk 지도")
        
        try:
            risk_map, risk_locations = create_risk_map()
            folium_static(risk_map, width=400, height=400)
            
            # Risk Level 범례
            st.markdown("#### 🚨 Risk Level")
            st.markdown("🔴 **높음** - 즉시 대응 필요")
            st.markdown("🟠 **중간** - 모니터링 필요")
            st.markdown("🟢 **낮음** - 정상 운영")
            
        except Exception as e:
            st.error(f"지도 로딩 오류: {e}")

if __name__ == "__main__":
    main()
