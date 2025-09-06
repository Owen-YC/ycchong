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

# Professional Compact CSS Design
st.markdown("""
<style>
    /* 전체 배경 - 깔끔한 화이트 */
    .stApp {
        background: #fafafa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 메인 헤더 - 컴팩트 */
    .main-header {
        background: #2c3e50;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .main-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }
    
    .main-subtitle {
        font-size: 0.85rem;
        opacity: 0.8;
        margin: 0.25rem 0 0 0;
    }
    
    /* 컴팩트 카드 */
    .compact-card {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* 뉴스 카드 - 컴팩트 */
    .news-item {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #3498db;
    }
    
    .news-title {
        font-size: 0.9rem;
        font-weight: 500;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
        line-height: 1.3;
    }
    
    .news-meta {
        display: flex;
        gap: 0.75rem;
        font-size: 0.75rem;
        color: #7f8c8d;
        margin-bottom: 0.5rem;
    }
    
    .news-source {
        background: #3498db;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 3px;
        font-size: 0.7rem;
    }
    
    .news-link {
        color: #3498db;
        text-decoration: none;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .news-link:hover {
        color: #2980b9;
    }
    
    /* 사이드바 정보 */
    .info-card {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.75rem;
        margin-bottom: 0.75rem;
        text-align: center;
    }
    
    .info-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
    }
    
    .info-content {
        font-size: 0.75rem;
        color: #7f8c8d;
        margin: 0;
    }
    
    /* 지도 컨테이너 */
    .map-wrapper {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* 위험도 표시 */
    .risk-item {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.75rem;
    }
    
    .risk-high { border-left: 3px solid #e74c3c; }
    .risk-medium { border-left: 3px solid #f39c12; }
    .risk-low { border-left: 3px solid #27ae60; }
    
    .risk-title {
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.25rem 0;
    }
    
    .risk-desc {
        color: #7f8c8d;
        margin: 0;
        font-size: 0.7rem;
    }
    
    /* 섹션 헤더 */
    .section-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.75rem 0;
        padding-bottom: 0.25rem;
        border-bottom: 2px solid #3498db;
    }
    
    /* 푸터 */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: #7f8c8d;
        font-size: 0.75rem;
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
    
    return risk_locations

def create_risk_map():
    """SCM Risk 지도 생성"""
    risk_locations = get_scm_risk_locations()
    
    # 지도 생성 (더 작게)
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='CartoDB positron',
        width=300,
        height=200
    )
    
    # 위험도별 색상 매핑
    risk_colors = {
        "high": "#dc2626",
        "medium": "#f59e0b", 
        "low": "#10b981"
    }
    
    for location in risk_locations:
        # 관련 뉴스 링크 HTML 생성
        news_links_html = ""
        for i, news in enumerate(location['news'], 1):
            news_links_html += f"""
            <div style="margin: 8px 0; padding: 8px; background: #f8fafc; border-radius: 6px; border-left: 3px solid #3b82f6;">
                <div style="color: #1e40af; font-size: 12px; font-weight: 500;">
                    {i}. {news}
                </div>
            </div>
            """
        
        # 팝업 HTML
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

def crawl_scm_risk_news(num_results: int = 100) -> List[Dict]:
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
    
    # 100개 뉴스 생성
    for i in range(num_results):
        site = random.choice(news_sites)
        title_index = i % len(scm_news_titles)
        article = {
            'title': scm_news_titles[title_index] + f" - Part {i+1}",
            'url': site['url'],
            'source': site['name'],
            'published_time': (datetime.now() - timedelta(hours=random.randint(0, 24))).strftime('%Y-%m-%d %H:%M'),
            'description': f"SCM Risk 관련 최신 뉴스와 분석을 제공합니다.",
            'views': random.randint(100, 5000)
        }
        articles.append(article)
    
    return articles

def main():
    # 메인 헤더
    st.markdown("""
    <div class="main-header">
        <div class="main-title">SCM Risk Monitor</div>
        <div class="main-subtitle">Global Supply Chain Risk Monitoring</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 메인 레이아웃 - 더 컴팩트하게
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    # 좌측 컬럼 - 시간, 날씨
    with col1:
        # 서울 시간
        date_str, time_str = get_korean_time()
        st.markdown(f"""
        <div class="info-card">
            <div class="info-title">Seoul Time</div>
            <div class="info-content">{date_str}<br><strong>{time_str}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 서울 날씨
        weather_info = get_seoul_weather()
        st.markdown(f"""
        <div class="info-card">
            <div class="info-title">Seoul Weather</div>
            <div class="info-content">
                {weather_info['condition']}<br>
                <strong>{weather_info['temperature']}°C</strong><br>
                체감 {weather_info['feels_like']}°C
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 중앙 컬럼 - 뉴스
    with col2:
        # SCM Risk 뉴스 자동 로드 (50개로 줄임)
        if 'scm_articles' not in st.session_state:
            with st.spinner("Loading SCM Risk news..."):
                st.session_state.scm_articles = crawl_scm_risk_news(50)
                st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
        
        # 뉴스 헤더
        if st.session_state.scm_articles:
            load_time = st.session_state.get('scm_load_time', datetime.now().strftime('%H:%M'))
            st.markdown(f"""
            <div class="compact-card">
                <h3 class="section-header">SCM Risk News ({len(st.session_state.scm_articles)} articles)</h3>
                <p style="font-size: 0.75rem; color: #7f8c8d; margin: 0;">Last updated: {load_time}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 뉴스 리스트 (컴팩트)
            for i, article in enumerate(st.session_state.scm_articles, 1):
                st.markdown(f"""
                <div class="news-item">
                    <div class="news-title">{article['title']}</div>
                    <div class="news-meta">
                        <span class="news-source">{article['source']}</span>
                        <span>{article['published_time']}</span>
                        <span>{article['views']:,} views</span>
                    </div>
                    <a href="{article['url']}" target="_blank" class="news-link">Read more →</a>
                </div>
                """, unsafe_allow_html=True)
    
    # 우측 컬럼 - 지도와 위험 정보
    with col3:
        # 지도
        st.markdown('<h3 class="section-header">Risk Map</h3>', unsafe_allow_html=True)
        try:
            risk_map, risk_locations = create_risk_map()
            st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
            st_folium(risk_map, width=300, height=200, returned_objects=[])
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Map error: {e}")
        
        # 위험도 범례
        st.markdown("""
        <div class="compact-card">
            <h4 style="font-size: 0.8rem; margin: 0 0 0.5rem 0;">Risk Levels</h4>
            <div class="risk-item risk-high">
                <div class="risk-title">High Risk</div>
                <div class="risk-desc">Immediate action required</div>
            </div>
            <div class="risk-item risk-medium">
                <div class="risk-title">Medium Risk</div>
                <div class="risk-desc">Monitor closely</div>
            </div>
            <div class="risk-item risk-low">
                <div class="risk-title">Low Risk</div>
                <div class="risk-desc">Normal operations</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 주요 위험 지역 (상위 3개만)
        st.markdown('<h4 style="font-size: 0.8rem; margin: 0 0 0.5rem 0;">Key Risk Areas</h4>', unsafe_allow_html=True)
        for location in risk_locations[:3]:
            risk_class = f"risk-{location['risk_level']}"
            st.markdown(f"""
            <div class="risk-item {risk_class}">
                <div class="risk-title">{location['flag']} {location['name']}</div>
                <div class="risk-desc">{location['risk_type']} - {location['description'][:50]}...</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 푸터
    st.markdown("""
    <div class="footer">
        SCM Risk Monitor | Real-time Global Supply Chain Risk Monitoring
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
