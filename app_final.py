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
model = genai.GenerativeModel('gemini-pro')

# 페이지 설정
st.set_page_config(
    page_title="SCM Risk Management AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2025 트렌드에 맞는 CSS 스타일 - 흰색 배경, 푸른색 계열
st.markdown("""
<style>
    /* 전체 배경 - 깔끔한 흰색 */
    .stApp {
        background: #ffffff;
        min-height: 100vh;
    }
    
    /* 메인 헤더 - 2025 트렌드 */
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
    }
    
    /* 정보 카드 - 2025 트렌드 */
    .info-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.1);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(30, 64, 175, 0.15);
    }
    
    /* 뉴스 카드 - 2025 트렌드 */
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
    }
    
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
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
    }
    
    /* 뉴스 메타 정보 */
    .news-meta {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    /* 뉴스 설명 */
    .news-description {
        font-size: 1rem;
        color: #475569;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    /* 뉴스 링크 버튼 - 2025 트렌드 */
    .news-link {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
        position: relative;
        overflow: hidden;
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
        color: white;
        text-decoration: none;
    }
    
    /* Streamlit 버튼 - 2025 트렌드 */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
        transition: all 0.3s ease;
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
    }
    
    /* 챗봇 컨테이너 */
    .chatbot-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.1);
    }
    
    /* 필터 컨테이너 */
    .filter-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(30, 64, 175, 0.1);
    }
    
    /* 날씨 정보 */
    .weather-info {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(30, 64, 175, 0.2);
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
    """Google News API를 사용한 뉴스 크롤링 (시뮬레이션)"""
    try:
        # 실제 뉴스 데이터 (더 많은 기사)
        scm_risk_news = [
            {
                "title": "글로벌 SCM 위기, 기업들의 디지털 전환 가속화",
                "source": "SCM뉴스",
                "description": "공급망 관리(SCM) 시스템의 글로벌 위기로 인해 기업들이 AI와 IoT 기술을 활용한 디지털 전환을 가속화하고 있습니다.",
                "url": "https://www.scm-news.com/global-crisis-digital-transformation",
                "published_time": "2024-01-15T10:30:00Z",
                "views": random.randint(1000, 5000)
            },
            {
                "title": "반도체 부족으로 인한 자동차 생산 중단 확산",
                "source": "자동차뉴스",
                "description": "글로벌 반도체 부족으로 인해 주요 자동차 제조업체들의 생산 중단이 확산되고 있습니다.",
                "url": "https://www.autonews.com/semiconductor-shortage-production-disruption",
                "published_time": "2024-01-14T15:45:00Z",
                "views": random.randint(800, 4000)
            },
            {
                "title": "해운비 상승으로 인한 물류 비용 증가 심화",
                "source": "물류뉴스",
                "description": "글로벌 해운비 상승으로 인해 수출입 기업들의 물류 비용이 크게 증가하고 있습니다.",
                "url": "https://www.logistics-news.com/shipping-cost-increase",
                "published_time": "2024-01-13T09:20:00Z",
                "views": random.randint(1200, 6000)
            },
            {
                "title": "스마트 물류 시스템 도입으로 효율성 향상",
                "source": "스마트물류",
                "description": "AI와 자동화 기술을 활용한 스마트 물류 시스템이 급속히 도입되어 물류 효율성이 크게 향상되고 있습니다.",
                "url": "https://www.smart-logistics.com/ai-automation-efficiency",
                "published_time": "2024-01-12T14:15:00Z",
                "views": random.randint(900, 4500)
            },
            {
                "title": "공급망 투명성 확보의 중요성 증가",
                "source": "ESG뉴스",
                "description": "ESG 경영의 확산으로 공급망 투명성 확보의 중요성이 크게 증가하고 있습니다.",
                "url": "https://www.esg-news.com/supply-chain-transparency",
                "published_time": "2024-01-11T11:30:00Z",
                "views": random.randint(700, 3500)
            },
            {
                "title": "친환경 물류로의 전환 가속화",
                "source": "그린물류",
                "description": "탄소 중립 목표에 따라 친환경 물류 시스템으로의 전환이 가속화되고 있습니다.",
                "url": "https://www.green-logistics.com/carbon-neutral-transition",
                "published_time": "2024-01-10T16:45:00Z",
                "views": random.randint(600, 3000)
            },
            {
                "title": "실시간 재고 관리 시스템으로 비용 절감",
                "source": "재고관리",
                "description": "IoT 기술을 활용한 실시간 재고 관리 시스템이 기업들의 물류 비용을 크게 절감하고 있습니다.",
                "url": "https://www.inventory-management.com/iot-real-time-cost-reduction",
                "published_time": "2024-01-09T13:20:00Z",
                "views": random.randint(1100, 5500)
            },
            {
                "title": "드론 배송 시범 운영 확대",
                "source": "드론배송",
                "description": "드론을 활용한 배송 서비스의 시범 운영이 전 세계적으로 확대되고 있습니다.",
                "url": "https://www.drone-delivery.com/pilot-expansion",
                "published_time": "2024-01-08T10:10:00Z",
                "views": random.randint(800, 4000)
            },
            {
                "title": "SCM Risk 관리 시스템 도입 확대",
                "source": "리스크관리",
                "description": "기업들이 공급망 위험을 사전에 예측하고 대응하기 위한 시스템을 적극 도입하고 있습니다.",
                "url": "https://www.risk-management.com/scm-prediction-system",
                "published_time": "2024-01-07T12:30:00Z",
                "views": random.randint(1000, 5000)
            },
            {
                "title": "공급망 재구성 움직임 활발",
                "source": "경제분석",
                "description": "글로벌 공급망 위기로 인해 기업들이 지역별 공급망 재구성을 추진하고 있습니다.",
                "url": "https://www.economic-analysis.com/supply-chain-restructuring",
                "published_time": "2024-01-06T08:45:00Z",
                "views": random.randint(1300, 6500)
            },
            {
                "title": "AI 기반 공급망 예측 시스템 도입",
                "source": "AI뉴스",
                "description": "머신러닝과 AI를 활용한 공급망 예측 시스템이 기업들의 위험 관리 능력을 크게 향상시키고 있습니다.",
                "url": "https://www.ai-news.com/supply-chain-prediction",
                "published_time": "2024-01-05T14:20:00Z",
                "views": random.randint(1500, 7000)
            },
            {
                "title": "블록체인 기술로 공급망 투명성 확보",
                "source": "블록체인뉴스",
                "description": "블록체인 기술을 활용한 공급망 추적 시스템이 제품의 원산지부터 소비자까지의 모든 과정을 투명하게 관리합니다.",
                "url": "https://www.blockchain-news.com/supply-chain-transparency",
                "published_time": "2024-01-04T11:15:00Z",
                "views": random.randint(1200, 5800)
            },
            {
                "title": "글로벌 물류 허브 경쟁 심화",
                "source": "물류허브",
                "description": "아시아 지역의 물류 허브 경쟁이 심화되면서 각국이 인프라 투자를 확대하고 있습니다.",
                "url": "https://www.logistics-hub.com/global-competition",
                "published_time": "2024-01-03T09:30:00Z",
                "views": random.randint(1000, 4800)
            },
            {
                "title": "공급망 복원력 강화의 중요성",
                "source": "경영전략",
                "description": "코로나19 이후 공급망 복원력 강화가 기업의 생존과 성장에 핵심 요소로 부상하고 있습니다.",
                "url": "https://www.strategy-news.com/supply-chain-resilience",
                "published_time": "2024-01-02T16:45:00Z",
                "views": random.randint(1400, 6200)
            },
            {
                "title": "디지털 트윈으로 공급망 최적화",
                "source": "디지털트윈",
                "description": "디지털 트윈 기술을 활용한 가상 공급망 시뮬레이션이 실제 운영 효율성을 크게 향상시키고 있습니다.",
                "url": "https://www.digital-twin.com/supply-chain-optimization",
                "published_time": "2024-01-01T13:10:00Z",
                "views": random.randint(1100, 5200)
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
                'url': f"https://www.{query.lower()}-news.com/{len(articles) + 1}",
                'source': source,
                'published_time': published_time,
                'description': f'{query}와 관련된 {topic}에 대한 최신 동향과 분석을 제공합니다. SCM Risk 관리 관점에서 {query}의 중요성과 향후 전망을 살펴봅니다.',
                'views': random.randint(500, 3000)
            }
            articles.append(article)
        
        return articles[:num_results]
        
    except Exception as e:
        st.error(f"뉴스 생성 오류: {e}")
        return []

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
    risk_locations = [
        {"name": "중국 상하이", "lat": 31.2304, "lng": 121.4737, "risk": "높음", "description": "공급망 중단 위험", "color": "red", "news_keywords": ["중국", "상하이", "공급망", "중단"]},
        {"name": "미국 로스앤젤레스", "lat": 34.0522, "lng": -118.2437, "risk": "중간", "description": "항구 혼잡", "color": "orange", "news_keywords": ["미국", "로스앤젤레스", "항구", "혼잡"]},
        {"name": "독일 함부르크", "lat": 53.5511, "lng": 9.9937, "risk": "낮음", "description": "물류 지연", "color": "green", "news_keywords": ["독일", "함부르크", "물류", "지연"]},
        {"name": "싱가포르", "lat": 1.3521, "lng": 103.8198, "risk": "중간", "description": "운송 비용 증가", "color": "orange", "news_keywords": ["싱가포르", "운송", "비용"]},
        {"name": "한국 부산", "lat": 35.1796, "lng": 129.0756, "risk": "낮음", "description": "정상 운영", "color": "green", "news_keywords": ["한국", "부산", "항구"]},
        {"name": "일본 도쿄", "lat": 35.6762, "lng": 139.6503, "risk": "중간", "description": "지진 위험", "color": "orange", "news_keywords": ["일본", "도쿄", "지진"]},
        {"name": "인도 뭄바이", "lat": 19.0760, "lng": 72.8777, "risk": "높음", "description": "인프라 부족", "color": "red", "news_keywords": ["인도", "뭄바이", "인프라"]},
        {"name": "브라질 상파울루", "lat": -23.5505, "lng": -46.6333, "risk": "중간", "description": "정치적 불안정", "color": "orange", "news_keywords": ["브라질", "상파울루", "정치"]},
        {"name": "네덜란드 로테르담", "lat": 51.9225, "lng": 4.4792, "risk": "낮음", "description": "안정적 운영", "color": "green", "news_keywords": ["네덜란드", "로테르담"]},
        {"name": "아랍에미리트 두바이", "lat": 25.2048, "lng": 55.2708, "risk": "중간", "description": "지정학적 위험", "color": "orange", "news_keywords": ["아랍에미리트", "두바이", "지정학"]}
    ]
    
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='OpenStreetMap'
    )
    
    for location in risk_locations:
        popup_html = f"""
        <div style="width: 250px;">
            <h4 style="color: {location['color']}; margin: 0 0 10px 0;">{location['name']}</h4>
            <p style="margin: 5px 0;"><strong>위험도:</strong> <span style="color: {location['color']}; font-weight: bold;">{location['risk']}</span></p>
            <p style="margin: 5px 0; font-size: 12px;">{location['description']}</p>
            <button onclick="window.parent.postMessage({{'type': 'map_click', 'keywords': {location['news_keywords']}}}, '*')" 
                    style="background: #1e40af; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; margin-top: 10px;">
                관련 뉴스 보기
            </button>
        </div>
        """
        
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=folium.Popup(popup_html, max_width=300),
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
    
    # 사이드바 - 날짜, 시간, 날씨 정보
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
        
        # AI 챗봇 섹션
        st.markdown("### 🤖 AI 챗봇")
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
    
    with col2:
        # Risk 지도 섹션
        st.markdown("### 🗺️ 글로벌 SCM Risk 지도")
        
        try:
            risk_map, risk_locations = create_risk_map()
            folium_static(risk_map, width=400, height=400)
            
            # 위험도 범례
            st.markdown("#### 🚨 위험도 범례")
            st.markdown("🔴 **높음** - 즉시 대응 필요")
            st.markdown("🟠 **중간** - 모니터링 필요")
            st.markdown("🟢 **낮음** - 정상 운영")
            
            # 지도 클릭 이벤트 처리
            st.markdown("""
            <script>
            window.addEventListener('message', function(event) {
                if (event.data.type === 'map_click') {
                    // 지도 클릭 시 관련 뉴스 검색
                    console.log('Map clicked:', event.data.keywords);
                }
            });
            </script>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"지도 로딩 오류: {e}")

if __name__ == "__main__":
    main()
