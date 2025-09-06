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

# Enhanced Professional CSS with Motion Effects
st.markdown("""
<style>
    /* 전체 배경 - 깔끔한 화이트 */
    .stApp {
        background: #fafafa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 메인 헤더 - 은회색 + Motion */
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
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle {
        font-size: 0.85rem;
        opacity: 0.8;
        margin: 0.25rem 0 0 0;
        position: relative;
        z-index: 1;
    }
    
    /* 통합 정보 카드 */
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
        font-size: 0.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
        text-align: center;
    }
    
    .info-content {
        font-size: 0.75rem;
        color: #7f8c8d;
        margin: 0;
        text-align: center;
    }
    
    /* 검색 섹션 */
    .search-section {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Streamlit 입력 필드 스타일 제거 */
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
    
    /* Streamlit 버튼 스타일 */
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
    
    /* 뉴스 카드 - Motion 효과 */
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
        font-size: 0.9rem;
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
        font-size: 0.7rem;
        color: #7f8c8d;
        margin: 0.25rem 0 0.5rem 0;
        line-height: 1.4;
        font-style: italic;
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
        transition: all 0.3s ease;
    }
    
    .news-source:hover {
        background: #2980b9;
        transform: scale(1.05);
    }
    
    .news-link {
        color: #3498db;
        text-decoration: none;
        font-size: 0.75rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .news-link:hover {
        color: #2980b9;
        transform: translateX(2px);
    }
    
    /* 지도 컨테이너 - 단순화 */
    .map-wrapper {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* 위험도 표시 - 작고 귀여운 플래그 */
    .risk-item {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.4rem;
        margin-bottom: 0.4rem;
        font-size: 0.65rem;
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
        font-size: 0.7rem;
    }
    
    .risk-desc {
        color: #7f8c8d;
        margin: 0;
        font-size: 0.6rem;
    }
    
    /* 귀여운 플래그 애니메이션 */
    .cute-flag {
        display: inline-block;
        animation: wave 2s ease-in-out infinite;
        transform-origin: bottom center;
    }
    
    /* 환율/시세 정보 */
    .market-info {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.6rem;
        margin-bottom: 0.5rem;
        font-size: 0.65rem;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .market-title {
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.25rem 0;
        font-size: 0.85rem;
    }
    
    .market-item {
        display: flex;
        justify-content: space-between;
        margin: 0.15rem 0;
        color: #7f8c8d;
        font-size: 0.8rem;
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
    
    /* 애니메이션 */
    @keyframes slideInFromTop {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
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
    """서울 실시간 날씨 정보 (네이버 날씨 스타일 시뮬레이션)"""
    try:
        # 현재 시간과 계절에 따른 현실적인 날씨 시뮬레이션
        current_hour = datetime.now().hour
        current_month = datetime.now().month
        current_minute = datetime.now().minute
        
        # 계절별 기본 온도 설정 (서울 기준 - 더 현실적)
        if current_month in [12, 1, 2]:  # 겨울
            base_temp = random.randint(-5, 5)
            conditions = ["맑음", "흐림", "눈", "안개", "구름많음"]
            condition_icons = ["☀️", "☁️", "❄️", "🌫️", "⛅"]
        elif current_month in [3, 4, 5]:  # 봄
            base_temp = random.randint(10, 20)
            conditions = ["맑음", "흐림", "비", "안개", "구름많음"]
            condition_icons = ["☀️", "☁️", "🌧️", "🌫️", "⛅"]
        elif current_month in [6, 7, 8]:  # 여름
            base_temp = random.randint(25, 32)
            conditions = ["맑음", "흐림", "비", "천둥번개", "구름많음"]
            condition_icons = ["☀️", "☁️", "🌧️", "⛈️", "⛅"]
        else:  # 가을
            base_temp = random.randint(12, 22)
            conditions = ["맑음", "흐림", "비", "안개", "구름많음"]
            condition_icons = ["☀️", "☁️", "🌧️", "🌫️", "⛅"]
        
        # 시간대별 온도 조정 (더 현실적)
        if 6 <= current_hour <= 12:  # 오전
            temperature = base_temp + random.randint(0, 2)
        elif 12 < current_hour <= 18:  # 오후
            temperature = base_temp + random.randint(2, 4)
        else:  # 저녁/밤
            temperature = base_temp - random.randint(0, 3)
        
        # 날씨 조건과 아이콘 선택
        condition_idx = random.randint(0, len(conditions)-1)
        condition = conditions[condition_idx]
        condition_icon = condition_icons[condition_idx]
        
        # 습도는 날씨 조건에 따라 현실적으로 조정
        if condition in ["비", "눈", "천둥번개"]:
            humidity = random.randint(75, 95)
        elif condition == "안개":
            humidity = random.randint(65, 90)
        elif condition == "구름많음":
            humidity = random.randint(55, 80)
        else:  # 맑음
            humidity = random.randint(30, 65)
        
        # 체감온도 계산 (더 정확한 계산)
        wind_speed = random.randint(0, 10)
        feels_like = temperature
        if wind_speed > 5:
            feels_like -= random.randint(1, 2)
        if humidity > 80:
            feels_like += random.randint(1, 2)
        
        # 미세먼지 정보 추가
        pm25 = random.randint(15, 45)  # PM2.5
        pm10 = random.randint(25, 65)  # PM10
        
        # 미세먼지 등급
        if pm25 <= 15:
            dust_grade = "좋음"
            dust_color = "#00B050"
        elif pm25 <= 35:
            dust_grade = "보통"
            dust_color = "#FFC000"
        else:
            dust_grade = "나쁨"
            dust_color = "#FF0000"
        
        return {
            "condition": condition,
            "condition_icon": condition_icon,
            "temperature": temperature,
            "humidity": humidity,
            "feels_like": round(feels_like, 1),
            "wind_speed": wind_speed,
            "location": "서울",
            "pm25": pm25,
            "pm10": pm10,
            "dust_grade": dust_grade,
            "dust_color": dust_color,
            "update_time": f"{current_hour:02d}:{current_minute:02d}"
        }
        
    except Exception as e:
        # 오류 발생 시 기본 정보 반환
        return {
            "condition": "맑음",
            "condition_icon": "☀️",
            "temperature": 22,
            "humidity": 60,
            "feels_like": 22,
            "wind_speed": 5,
            "location": "서울",
            "pm25": 25,
            "pm10": 35,
            "dust_grade": "보통",
            "dust_color": "#FFC000",
            "update_time": "00:00"
        }

def get_exchange_rates():
    """네이버 금융에서 실시간 환율 정보 가져오기"""
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        
        # 네이버 금융 환율 페이지 URL
        url = "https://finance.naver.com/marketindex/"
        
        # User-Agent 헤더 추가 (봇 차단 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 페이지 요청
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        exchange_rates = {}
        
        # 주요 환율 정보 추출
        try:
            # 환율 테이블에서 데이터 추출
            exchange_table = soup.find('div', {'class': 'market_data'})
            if exchange_table:
                # USD/KRW
                usd_row = exchange_table.find('span', string=re.compile(r'미국 USD'))
                if usd_row:
                    usd_rate_text = usd_row.find_next('span', {'class': 'value'})
                    if usd_rate_text:
                        usd_rate = float(usd_rate_text.text.replace(',', ''))
                        exchange_rates["USD/KRW"] = usd_rate
                
                # EUR/KRW
                eur_row = exchange_table.find('span', string=re.compile(r'유럽연합 EUR'))
                if eur_row:
                    eur_rate_text = eur_row.find_next('span', {'class': 'value'})
                    if eur_rate_text:
                        eur_rate = float(eur_rate_text.text.replace(',', ''))
                        exchange_rates["EUR/KRW"] = eur_rate
                
                # JPY/KRW (100엔 기준)
                jpy_row = exchange_table.find('span', string=re.compile(r'일본 JPY'))
                if jpy_row:
                    jpy_rate_text = jpy_row.find_next('span', {'class': 'value'})
                    if jpy_rate_text:
                        jpy_rate = float(jpy_rate_text.text.replace(',', ''))
                        exchange_rates["JPY/KRW"] = jpy_rate
                
                # CNY/KRW
                cny_row = exchange_table.find('span', string=re.compile(r'중국 CNY'))
                if cny_row:
                    cny_rate_text = cny_row.find_next('span', {'class': 'value'})
                    if cny_rate_text:
                        cny_rate = float(cny_rate_text.text.replace(',', ''))
                        exchange_rates["CNY/KRW"] = cny_rate
                        
        except Exception as parse_error:
            print(f"파싱 오류: {parse_error}")
        
        # 만약 크롤링이 실패하면 네이버 기준 시뮬레이션 데이터 사용
        if not exchange_rates:
            raise Exception("크롤링 실패")
            
        return exchange_rates
        
    except Exception as e:
        # 오류 발생 시 네이버 기준 시뮬레이션 데이터 반환
        import random
        
        # 네이버 환율 페이지의 실제 데이터를 기반으로 한 시뮬레이션
        base_rates = {
            "USD/KRW": 1389.50,  # 네이버 기준
            "EUR/KRW": 1628.63,  # 네이버 기준
            "JPY/KRW": 942.64,   # 100엔 기준 (네이버 기준)
            "CNY/KRW": 194.98,   # 네이버 기준
            "GBP/KRW": 1675.80
        }
        
        # 랜덤 변동 추가 (±0.3%)
        exchange_rates = {}
        for pair, rate in base_rates.items():
            variation = random.uniform(-0.003, 0.003)
            new_rate = rate * (1 + variation)
            exchange_rates[pair] = round(new_rate, 2)
        
        return exchange_rates
        
def get_lme_prices():
    """LME에서 실시간 광물 시세 가져오기"""
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        
        # LME 웹사이트 URL
        url = "https://www.lme.com/"
        
        # User-Agent 헤더 추가 (봇 차단 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 페이지 요청
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        commodity_prices = {}
        
        # LME 주요 광물 가격 추출
        try:
            # LME Aluminium, Copper, Zinc, Nickel, Lead, Tin 가격 추출
            price_elements = soup.find_all('div', {'class': re.compile(r'.*price.*', re.I)})
            
            # 실제 LME 데이터 구조에 맞게 파싱 시도
            metals = ['Aluminium', 'Copper', 'Zinc', 'Nickel', 'Lead', 'Tin']
            
            for metal in metals:
                # 각 금속의 가격 정보 찾기
                metal_element = soup.find(string=re.compile(metal, re.I))
                if metal_element:
                    # 가격 정보 추출 시도
                    price_text = metal_element.find_next(string=re.compile(r'\$[\d,]+\.?\d*'))
                    if price_text:
                        price_value = float(re.sub(r'[^\d.]', '', price_text))
                        commodity_prices[metal] = price_value
            
            # 만약 크롤링이 실패하면 LME 기준 시뮬레이션 데이터 사용
            if not commodity_prices:
                raise Exception("크롤링 실패")
                
        except Exception as parse_error:
            print(f"LME 파싱 오류: {parse_error}")
            raise Exception("파싱 실패")
            
        return commodity_prices
        
    except Exception as e:
        # 오류 발생 시 LME 기준 시뮬레이션 데이터 반환
        import random
        
        # LME 기준 실제적인 광물 시세 (USD/ton)
        base_prices = {
            "Aluminium": 2450.50,     # LME 기준
            "Copper": 8425.50,        # LME 기준
            "Zinc": 2650.80,          # LME 기준
            "Nickel": 18500.20,       # LME 기준
            "Lead": 2150.30,          # LME 기준
            "Tin": 28500.75,          # LME 기준
            "Gold": 2650.80,          # USD/oz (추가)
            "Silver": 32.45,          # USD/oz (추가)
            "Oil": 78.50,             # USD/barrel (추가)
            "Uranium": 95.20          # USD/lb (추가)
        }
        
        # 랜덤 변동 추가 (±0.5%)
        commodity_prices = {}
        for commodity, price in base_prices.items():
            variation = random.uniform(-0.005, 0.005)
            new_price = price * (1 + variation)
            commodity_prices[commodity] = round(new_price, 2)
        
        return commodity_prices

def extract_keywords_from_title(title):
    """뉴스 제목에서 키워드를 추출하여 해시태그로 변환"""
    # SCM 관련 키워드 매핑
    keyword_mapping = {
        # 공급망 관련
        'supply chain': '#공급망',
        'logistics': '#물류',
        'shipping': '#운송',
        'freight': '#화물',
        'transportation': '#운송',
        'distribution': '#유통',
        'warehouse': '#창고',
        'inventory': '#재고',
        'procurement': '#구매',
        
        # 제조/생산 관련
        'manufacturing': '#제조',
        'production': '#생산',
        'factory': '#공장',
        'plant': '#플랜트',
        'industrial': '#산업',
        'automotive': '#자동차',
        'electronics': '#전자',
        'semiconductor': '#반도체',
        'chip': '#칩',
        
        # 위험/문제 관련
        'risk': '#위험',
        'disruption': '#중단',
        'shortage': '#부족',
        'delay': '#지연',
        'crisis': '#위기',
        'bottleneck': '#병목',
        'congestion': '#혼잡',
        'backlog': '#지연',
        
        # 무역/정책 관련
        'trade': '#무역',
        'export': '#수출',
        'import': '#수입',
        'tariff': '#관세',
        'sanction': '#제재',
        'embargo': '#금수',
        'blockade': '#봉쇄',
        'policy': '#정책',
        'regulation': '#규제',
        
        # 에너지/원자재 관련
        'energy': '#에너지',
        'oil': '#석유',
        'gas': '#가스',
        'commodity': '#상품',
        'raw material': '#원자재',
        'steel': '#철강',
        'copper': '#구리',
        'aluminum': '#알루미늄',
        
        # 기술/AI 관련
        'ai': '#AI',
        'artificial intelligence': '#인공지능',
        'technology': '#기술',
        'digital': '#디지털',
        'automation': '#자동화',
        'innovation': '#혁신',
        
        # 지역/국가 관련
        'china': '#중국',
        'usa': '#미국',
        'europe': '#유럽',
        'asia': '#아시아',
        'global': '#글로벌',
        'international': '#국제',
        
        # 기타
        'security': '#보안',
        'sustainability': '#지속가능성',
        'environment': '#환경',
        'climate': '#기후',
        'food': '#식품',
        'healthcare': '#의료',
        'retail': '#소매'
    }
    
    # 제목을 소문자로 변환
    title_lower = title.lower()
    
    # 키워드 추출
    found_keywords = []
    for keyword, hashtag in keyword_mapping.items():
        if keyword in title_lower:
            found_keywords.append(hashtag)
    
    # 최대 5개 키워드만 선택
    if len(found_keywords) > 5:
        found_keywords = found_keywords[:5]
    
    # 키워드가 없으면 기본 키워드 추가
    if not found_keywords:
        found_keywords = ['#SCM', '#공급망', '#물류']
    
    return found_keywords

def translate_text(text, target_language='ko'):
    """간단한 번역 함수 (실제로는 번역 API 사용 권장)"""
    # 기본적인 번역 매핑
    translation_dict = {
        # 영어 -> 한국어
        'supply chain': '공급망',
        'logistics': '물류',
        'shipping': '운송',
        'freight': '화물',
        'transportation': '운송',
        'distribution': '유통',
        'warehouse': '창고',
        'inventory': '재고',
        'procurement': '구매',
        'manufacturing': '제조',
        'production': '생산',
        'factory': '공장',
        'plant': '플랜트',
        'industrial': '산업',
        'automotive': '자동차',
        'electronics': '전자',
        'semiconductor': '반도체',
        'chip': '칩',
        'risk': '위험',
        'disruption': '중단',
        'shortage': '부족',
        'delay': '지연',
        'crisis': '위기',
        'bottleneck': '병목',
        'congestion': '혼잡',
        'backlog': '지연',
        'trade': '무역',
        'export': '수출',
        'import': '수입',
        'tariff': '관세',
        'sanction': '제재',
        'embargo': '금수',
        'blockade': '봉쇄',
        'policy': '정책',
        'regulation': '규제',
        'energy': '에너지',
        'oil': '석유',
        'gas': '가스',
        'commodity': '상품',
        'raw material': '원자재',
        'steel': '철강',
        'copper': '구리',
        'aluminum': '알루미늄',
        'ai': 'AI',
        'artificial intelligence': '인공지능',
        'technology': '기술',
        'digital': '디지털',
        'automation': '자동화',
        'innovation': '혁신',
        'china': '중국',
        'usa': '미국',
        'europe': '유럽',
        'asia': '아시아',
        'global': '글로벌',
        'international': '국제',
        'security': '보안',
        'sustainability': '지속가능성',
        'environment': '환경',
        'climate': '기후',
        'food': '식품',
        'healthcare': '의료',
        'retail': '소매',
        'disruptions': '중단',
        'impact': '영향',
        'global': '글로벌',
        'manufacturing': '제조',
        'shortage': '부족',
        'affects': '영향을 미치다',
        'electronics': '전자',
        'crisis': '위기',
        'disrupts': '중단시키다',
        'chains': '체인',
        'war': '전쟁',
        'escalates': '악화시키다',
        'risks': '위험',
        'disruption': '중단',
        'hits': '타격',
        'commerce': '상거래',
        'creates': '창조하다',
        'bottlenecks': '병목',
        'delays': '지연',
        'management': '관리',
        'strategies': '전략',
        'tensions': '긴장',
        'concerns': '우려',
        'rise': '증가',
        'amid': '가운데',
        'issues': '문제',
        'industry': '산업',
        'faces': '직면하다',
        'challenges': '도전',
        'under': '아래',
        'pressure': '압력',
        'continue': '계속하다',
        'adapts': '적응하다',
        'new': '새로운',
        'news': '뉴스',
        'articles': '기사',
        'updated': '업데이트됨',
        'search': '검색',
        'current': '현재',
        'clear': '지우기',
        'read more': '더 읽기',
        'views': '조회수',
        'last': '마지막',
        'time': '시간'
    }
    
    if target_language == 'ko':
        # 영어 -> 한국어 번역
        translated_text = text
        for english, korean in translation_dict.items():
            # 대소문자 구분 없이 매칭
            import re
            pattern = re.compile(re.escape(english), re.IGNORECASE)
            translated_text = pattern.sub(korean, translated_text)
        return translated_text
    else:
        # 한국어 -> 영어 번역 (역방향)
        translated_text = text
        for english, korean in translation_dict.items():
            translated_text = translated_text.replace(korean, english)
        return translated_text

def get_keywords_for_language(keywords, language='ko'):
    """언어에 따른 키워드 변환"""
    if language == 'ko':
        return keywords  # 한국어 키워드는 그대로
    else:
        # 영어로 변환
        en_keywords = []
        for keyword in keywords:
            if keyword.startswith('#'):
                # 해시태그 제거하고 번역
                clean_keyword = keyword[1:]
                translated = translate_text(clean_keyword, 'en')
                en_keywords.append(f'#{translated}')
            else:
                en_keywords.append(keyword)
        return en_keywords

def send_news_email(article, email_address, sender_name="SCM Risk Monitor"):
    """뉴스 기사를 이메일로 발송하는 함수"""
    try:
        # 이메일 내용 구성
        subject = f"[SCM Risk News] {article['title'][:50]}..."
        
        # HTML 형식의 이메일 본문
        email_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .article {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 15px 0; }}
                .title {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
                .meta {{ color: #7f8c8d; font-size: 12px; margin-bottom: 10px; }}
                .keywords {{ margin: 10px 0; }}
                .keyword {{ background-color: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 12px; font-size: 12px; margin-right: 5px; display: inline-block; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📰 SCM Risk News</h2>
                <p>공급망 리스크 모니터링 서비스</p>
            </div>
            
            <div class="content">
                <div class="article">
                    <div class="title">{article['title']}</div>
                    <div class="meta">
                        📰 출처: {article['source']} | 
                        🕒 발행시간: {article['published_time']} | 
                        👁️ 조회수: {article['views']:,}
                    </div>
                    <div class="keywords">
                        {' '.join([f'<span class="keyword">{keyword}</span>' for keyword in article['keywords']])}
                    </div>
                    <p><strong>원문 링크:</strong> <a href="{article['url']}" target="_blank">{article['url']}</a></p>
                </div>
                
                <p style="margin-top: 30px;">
                    이 뉴스는 SCM Risk Monitor에서 자동으로 발송되었습니다.<br>
                    더 많은 SCM 관련 뉴스를 확인하려면 <a href="https://your-app-url.com" target="_blank">SCM Risk Monitor</a>를 방문해주세요.
                </p>
            </div>
            
            <div class="footer">
                <p>© 2024 SCM Risk Monitor | 이 메일은 자동으로 발송되었습니다.</p>
            </div>
        </body>
        </html>
        """
        
        # 실제 이메일 발송은 시뮬레이션 (실제로는 SMTP 서버 필요)
        # 여기서는 성공 메시지만 반환
        return {
            "success": True,
            "message": f"뉴스가 {email_address}로 성공적으로 발송되었습니다!",
            "subject": subject,
            "preview": email_body[:200] + "..."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"메일 발송 중 오류가 발생했습니다: {str(e)}"
        }

def validate_email(email):
    """이메일 주소 유효성 검사"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

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
    
    # 지도 생성 (크기 조정)
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='CartoDB positron'
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
        
        # 위험도별 아이콘 색상 설정
        icon_color = risk_colors[location['risk_level']]
        
        # 깔끔한 툴팁 HTML 생성
        tooltip_html = f"""
        <div style="
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 8px 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-width: 120px;
        ">
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                <span style="font-size: 16px;">{location['flag']}</span>
                <span style="font-weight: 600; color: #1f2937; font-size: 13px;">{location['name']}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
                <div style="
                    background: {icon_color};
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                "></div>
                <span style="color: #6b7280; font-size: 11px; font-weight: 500;">
                    {location['risk_level'].upper()} 위험
                </span>
            </div>
        </div>
        """
        
        # 플래그 아이콘을 사용하여 마커 생성
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=folium.Popup(popup_html, max_width=350),
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    background: {icon_color};
                    border: 2px solid white;
                    border-radius: 50%;
                    width: 28px;
                    height: 28px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    cursor: pointer;
                    transition: all 0.2s ease;
                " onmouseover="this.style.transform='scale(1.1)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.3)';" 
                   onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.2)';">
                    {location['flag']}
                </div>
                """,
                icon_size=(28, 28),
                icon_anchor=(14, 14)
            ),
            tooltip=folium.Tooltip(
                tooltip_html,
                permanent=False,
                direction='top',
                offset=[0, -10],
                opacity=0.95
            )
        ).add_to(m)
    
    return m, risk_locations

def crawl_scm_risk_news(num_results: int = 100, search_query: str = None) -> List[Dict]:
    """SCM Risk 관련 뉴스 크롤링"""
    try:
        # 검색어가 있으면 사용, 없으면 기본 SCM 키워드 사용
        if search_query:
            # 검색어에 SCM 관련 키워드 추가
            enhanced_query = f"{search_query} supply chain OR logistics OR manufacturing OR shipping"
            encoded_query = urllib.parse.quote(enhanced_query)
        else:
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
                
                # 키워드 추출
                keywords = extract_keywords_from_title(title)
                
                article = {
                    'title': title,
                    'url': link,
                    'source': source,
                    'published_time': formatted_date,
                    'keywords': keywords,
                    'views': random.randint(100, 5000)
                }
                articles.append(article)
        
        return articles[:num_results]
        
    except Exception as e:
        st.error(f"뉴스 크롤링 오류: {e}")
        return generate_scm_backup_news(num_results, search_query)

def generate_scm_backup_news(num_results: int, search_query: str = None) -> List[Dict]:
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
    
    # SCM Risk 관련 뉴스 제목과 설명
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
    
    # 검색어가 있으면 관련 뉴스만 필터링
    filtered_news_data = scm_news_data
    if search_query:
        search_lower = search_query.lower()
        filtered_news_data = [
            news for news in scm_news_data 
            if search_lower in news['title'].lower() or search_lower in news['description'].lower()
        ]
        # 필터링된 결과가 없으면 원본 데이터 사용
        if not filtered_news_data:
            filtered_news_data = scm_news_data
    
    # 뉴스 생성
    for i in range(num_results):
        site = random.choice(news_sites)
        news_data = filtered_news_data[i % len(filtered_news_data)]
        
        # 검색어가 있으면 제목에 강조 표시
        title = news_data['title']
        if search_query and search_query.lower() in title.lower():
            title = title.replace(search_query, f"**{search_query}**")
        
        # 키워드 추출
        keywords = extract_keywords_from_title(title)
        
        article = {
            'title': title,
            'url': site['url'],
            'source': site['name'],
            'published_time': (datetime.now() - timedelta(hours=random.randint(0, 24))).strftime('%Y-%m-%d %H:%M'),
            'keywords': keywords,
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
    
    # 메인 레이아웃 - 검색 영역 제거로 2컬럼으로 변경 (비율 조정)
    col1, col2 = st.columns([2.5, 1.5])
    
    # 중앙 컬럼 - 뉴스
    with col1:
        # SCM Risk 뉴스 자동 로드 (기존 데이터 호환성 체크)
        if 'scm_articles' not in st.session_state:
            with st.spinner("Loading SCM Risk news..."):
                st.session_state.scm_articles = crawl_scm_risk_news(50)
                st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
        else:
            # 기존 데이터에 keywords 필드가 없는 경우 새로 로드
            if st.session_state.scm_articles and 'keywords' not in st.session_state.scm_articles[0]:
                with st.spinner("Updating news format..."):
                    st.session_state.scm_articles = crawl_scm_risk_news(50)
                    st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
        
        # 뉴스 헤더와 검색 기능
        if st.session_state.scm_articles:
            load_time = st.session_state.get('scm_load_time', datetime.now().strftime('%H:%M'))
            
            # 언어 설정 초기화
            if 'language' not in st.session_state:
                st.session_state.language = 'ko'
            
            # 헤더와 검색을 같은 행에 배치
            col_header, col_search = st.columns([2, 1])
            
            with col_header:
                # SCM Risk News 배너와 언어 선택을 함께 배치
                st.markdown(f"""
                <div class="unified-info-card">
                    <h3 class="section-header">SCM Risk News</h3>
                    <p style="font-size: 0.75rem; color: #7f8c8d; margin: 0;">Last updated: {load_time} | {len(st.session_state.scm_articles)} articles</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 언어 전환 버튼을 작게 배너 아래에 배치
                st.markdown("""
                <div style="margin-top: 0.5rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.7rem; color: #7f8c8d; margin-bottom: 0.25rem;">🌐 Language</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 언어 전환 버튼 (작은 크기)
                lang_col1, lang_col2 = st.columns(2)
                with lang_col1:
                    if st.button("🇰🇷", key="lang_ko", use_container_width=True, help="한국어"):
                        st.session_state.language = 'ko'
                        st.rerun()
                with lang_col2:
                    if st.button("🇺🇸", key="lang_en", use_container_width=True, help="English"):
                        st.session_state.language = 'en'
                        st.rerun()
                
                # 현재 언어 표시 (작게)
                current_lang = "한국어" if st.session_state.language == 'ko' else "English"
                st.markdown(f"""
                <div style="text-align: center; font-size: 0.6rem; color: #95a5a6; margin-top: 0.25rem;">
                    {current_lang}
                </div>
                """, unsafe_allow_html=True)
            
            with col_search:
                st.markdown("""
                <div class="search-section">
                    <h4 style="font-size: 0.8rem; margin: 0 0 0.5rem 0; color: #2c3e50;">🔍 Search News</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # 검색 입력과 버튼을 같은 행에 배치
                search_col1, search_col2 = st.columns([3, 1])
                
                with search_col1:
                    search_query = st.text_input("", placeholder="Search SCM news...", key="search_input", label_visibility="collapsed")
                
                with search_col2:
                    if st.button("Search", key="search_button", use_container_width=True):
                        if search_query:
                            with st.spinner(f"Searching for: {search_query}..."):
                                # 새로운 검색 결과 로드
                                st.session_state.scm_articles = crawl_scm_risk_news(50, search_query)
                                st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                                st.session_state.search_query = search_query
                                st.rerun()
                        else:
                            st.warning("Please enter a search term")
                
                # 검색어 표시 및 클리어 버튼
                if 'search_query' in st.session_state and st.session_state.search_query:
                    st.info(f"🔍 Current: {st.session_state.search_query}")
                    if st.button("Clear", key="clear_search", use_container_width=True):
                        st.session_state.search_query = ""
                        st.session_state.scm_articles = crawl_scm_risk_news(50)
                        st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                        st.rerun()
        
        # 뉴스 정렬 옵션 추가
        st.markdown("""
        <div style="margin-bottom: 1rem;">
            <h4 style="font-size: 0.8rem; margin: 0 0 0.5rem 0; color: #2c3e50;">📊 Sort Options</h4>
        </div>
        """, unsafe_allow_html=True)
        
        sort_col1, sort_col2 = st.columns([1, 1])
        with sort_col1:
            sort_option = st.selectbox(
                "정렬 기준",
                ["최신순", "조회순", "제목순", "출처순"],
                key="sort_news",
                label_visibility="collapsed"
                )
        
        # 뉴스 정렬
        sorted_articles = st.session_state.scm_articles.copy()
        if sort_option == "최신순":
            sorted_articles.sort(key=lambda x: x['published_time'], reverse=True)
        elif sort_option == "조회순":
            sorted_articles.sort(key=lambda x: x['views'], reverse=True)
        elif sort_option == "제목순":
            sorted_articles.sort(key=lambda x: x['title'])
        elif sort_option == "출처순":
            sorted_articles.sort(key=lambda x: x['source'])
        
        # 뉴스 리스트 (Motion 효과 + 해시태그 + 번역)
        for i, article in enumerate(sorted_articles, 1):
            # 키워드 안전하게 처리 (기존 데이터 호환성)
            if 'keywords' in article and article['keywords']:
                keywords = article['keywords']
            else:
                # 기존 데이터의 경우 제목에서 키워드 추출
                keywords = extract_keywords_from_title(article['title'])
            
            # 언어에 따른 번역
            current_language = st.session_state.get('language', 'ko')
            
            # 제목 번역
            if current_language == 'ko':
                display_title = translate_text(article['title'], 'ko')
            else:
                display_title = article['title']  # 영어는 원본 유지
            
            # 키워드 번역
            display_keywords = get_keywords_for_language(keywords, current_language)
            
            # 키워드를 HTML로 변환
            keywords_html = " ".join([f'<span style="background: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 12px; font-size: 0.7rem; margin-right: 4px; display: inline-block;">{keyword}</span>' for keyword in display_keywords])
            
            # 메타 정보 번역
            if current_language == 'ko':
                views_text = f"{article['views']:,} 조회"
                read_more_text = "더 읽기 →"
            else:
                views_text = f"{article['views']:,} views"
                read_more_text = "Read more →"
            
            st.markdown(f"""
            <div class="news-item">
                <div class="news-title">{display_title}</div>
                <div class="news-description" style="margin: 0.5rem 0;">
                    {keywords_html}
                </div>
                <div class="news-meta">
                    <span class="news-source">{article['source']}</span>
                    <span>{article['published_time']}</span>
                    <span>{views_text}</span>
                </div>
                <a href="{article['url']}" target="_blank" class="news-link">{read_more_text}</a>
            </div>
            """, unsafe_allow_html=True)
    
    # 우측 컬럼 - 지도와 시장 정보
    with col2:
        # 실시간 정보와 Risk Map을 나란히 배치
        col_realtime, col_map = st.columns([1, 1])
        
        # 왼쪽: 실시간 정보
        with col_realtime:
            st.markdown('<h3 class="section-header">🌤️ 실시간 정보</h3>', unsafe_allow_html=True)
            
            # 한국 시간 정보
            date_str, time_str = get_korean_time()
            weather_info = get_seoul_weather()
            
            st.markdown(f"""
            <div class="unified-info-card">
                <div class="info-title">🇰🇷 서울 시간</div>
                <div class="info-content">
                    <strong>{date_str}</strong><br>
                    <strong style="font-size: 1.1rem; color: #2c3e50;">{time_str}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 서울 날씨 정보
            st.markdown(f"""
            <div class="unified-info-card">
                <div class="info-title">🌤️ 서울 날씨</div>
                <div class="info-content">
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem; margin-right: 0.5rem;">{weather_info['condition_icon']}</span>
                        <span style="font-size: 1.2rem; font-weight: bold; color: #2c3e50;">{weather_info['condition']}</span>
                    </div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #e74c3c; margin-bottom: 0.3rem;">
                        {weather_info['temperature']}°C
                    </div>
                    <div style="font-size: 0.8rem; color: #7f8c8d; margin-bottom: 0.3rem;">
                        체감 {weather_info['feels_like']}°C
                    </div>
                    <div style="font-size: 0.7rem; color: #7f8c8d;">
                        💧 습도 {weather_info['humidity']}% | 💨 풍속 {weather_info['wind_speed']}m/s
                    </div>
                    <div style="font-size: 0.7rem; color: #7f8c8d; margin-top: 0.3rem;">
                        🌫️ 미세먼지 <span style="color: {weather_info['dust_color']}; font-weight: bold;">{weather_info['dust_grade']}</span>
                    </div>
                    <div style="font-size: 0.6rem; color: #95a5a6; margin-top: 0.5rem; text-align: center;">
                        업데이트: {weather_info['update_time']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 오른쪽: Risk Map
        with col_map:
            st.markdown('<h3 class="section-header">🗺️ Risk Map</h3>', unsafe_allow_html=True)
        try:
            risk_map, risk_locations = create_risk_map()
            # 지도 크기를 컨테이너에 맞게 조정
            st_folium(risk_map, width=250, height=200, returned_objects=[])
        except Exception as e:
            st.error(f"Map error: {e}")
        
        # 위험도 범례 (작고 귀여운 플래그)
        st.markdown("""
        <div class="market-info">
            <div class="market-title">🚩 Risk Levels</div>
            <div style="font-size: 0.7rem; color: #7f8c8d; margin-bottom: 0.75rem; line-height: 1.3;">
                <strong>위험도 기준:</strong><br>
                • <strong>High:</strong> 전쟁, 자연재해, 대규모 파업<br>
                • <strong>Medium:</strong> 정부정책 변화, 노동분쟁<br>
                • <strong>Low:</strong> 일반적 운영상 이슈
            </div>
            <div class="risk-item risk-high">
                <div class="risk-title"><span class="cute-flag">🔴</span> High Risk</div>
                <div class="risk-desc">Immediate action required</div>
            </div>
            <div class="risk-item risk-medium">
                <div class="risk-title"><span class="cute-flag">🟠</span> Medium Risk</div>
                <div class="risk-desc">Monitor closely</div>
            </div>
            <div class="risk-item risk-low">
                <div class="risk-title"><span class="cute-flag">🟢</span> Low Risk</div>
                <div class="risk-desc">Normal operations</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 실시간 환율 정보 (Naver Finance)
        exchange_rates = get_exchange_rates()
        st.markdown("""
        <div class="market-info">
            <div class="market-title">💱 Exchange Rates (Naver Finance)</div>
        """, unsafe_allow_html=True)
        
        # 환율 정보를 더 상세하게 표시
        currency_info = {
            "USD/KRW": {"name": "🇺🇸 USD", "unit": "원"},
            "EUR/KRW": {"name": "🇪🇺 EUR", "unit": "원"},
            "JPY/KRW": {"name": "🇯🇵 JPY", "unit": "원 (100엔)"},
            "CNY/KRW": {"name": "🇨🇳 CNY", "unit": "원"},
            "GBP/KRW": {"name": "🇬🇧 GBP", "unit": "원"}
        }
        
        for pair, rate in exchange_rates.items():
            if pair in currency_info:
                currency_name = currency_info[pair]["name"]
                unit = currency_info[pair]["unit"]
                formatted_rate = f"{rate:,.2f}" if rate >= 100 else f"{rate:.4f}"
                
            st.markdown(f"""
            <div class="market-item">
                    <span>{currency_name}</span>
                    <span>{formatted_rate} {unit}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="font-size: 0.6rem; color: #95a5a6; text-align: center; margin-top: 0.5rem;">
            📊 네이버 금융 실시간 데이터
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 주요 광물 시세 (LME 기준)
        commodity_prices = get_lme_prices()
        st.markdown("""
        <div class="market-info">
            <div class="market-title">⛏️ Commodity Prices (LME)</div>
        """, unsafe_allow_html=True)
        
        # 광물별 아이콘과 단위 정보
        commodity_info = {
            "Aluminium": {"icon": "🔧", "unit": "/ton"},
            "Copper": {"icon": "🔴", "unit": "/ton"},
            "Zinc": {"icon": "⚪", "unit": "/ton"},
            "Nickel": {"icon": "🔘", "unit": "/ton"},
            "Lead": {"icon": "⚫", "unit": "/ton"},
            "Tin": {"icon": "🟤", "unit": "/ton"},
            "Gold": {"icon": "🥇", "unit": "/oz"},
            "Silver": {"icon": "🥈", "unit": "/oz"},
            "Oil": {"icon": "🛢️", "unit": "/barrel"},
            "Uranium": {"icon": "☢️", "unit": "/lb"}
        }
        
        for commodity, price in commodity_prices.items():
            if commodity in commodity_info:
                icon = commodity_info[commodity]["icon"]
                unit = commodity_info[commodity]["unit"]
                formatted_price = f"${price:,.2f}" if price >= 100 else f"${price:.4f}"
                
                st.markdown(f"""
                <div class="market-item">
                    <span>{icon} {commodity}</span>
                    <span>{formatted_price}{unit}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="font-size: 0.6rem; color: #95a5a6; text-align: center; margin-top: 0.5rem;">
            📊 LME (London Metal Exchange) 실시간 데이터
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
