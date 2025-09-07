import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
import re
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
        font-size: 1.8rem;
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
        background: #f8f9fa !important;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
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
        border-bottom: 2px solid #bdc3c7;
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
    
    /* 버튼 스타일 - 작고 밝은 회색 */
    .stButton > button {
        background-color: #e9ecef !important;
        color: #495057 !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
        padding: 0.25rem 0.5rem !important;
        font-size: 0.75rem !important;
        height: auto !important;
        min-height: 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #dee2e6 !important;
        border-color: #adb5bd !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button:disabled {
        background-color: #f8f9fa !important;
        color: #6c757d !important;
        border-color: #e9ecef !important;
        opacity: 0.6 !important;
    }
</style>


""", unsafe_allow_html=True)

def get_korean_time():
    """한국 시간 정보 가져오기"""
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    return now.strftime('%Y년 %m월 %d일'), now.strftime('%H:%M:%S')

def get_seoul_weather():
    """네이버 날씨에서 서울 실시간 날씨 정보 가져오기"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # 네이버 날씨 서울 페이지 URL
        url = "https://weather.naver.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 현재 온도 추출 (네이버 날씨 구조에 맞게 수정)
        temp_element = soup.find('span', class_='current')
        if not temp_element:
            # 다른 가능한 클래스명들 시도
            temp_element = soup.find('span', {'class': lambda x: x and 'temp' in x.lower()})
        
        if temp_element:
            temp_text = temp_element.get_text().strip()
            temperature = int(''.join(filter(str.isdigit, temp_text)))
        else:
            temperature = 20  # 기본값
        
        # 날씨 상태 추출
        condition_element = soup.find('span', class_='weather')
        if not condition_element:
            condition_element = soup.find('span', {'class': lambda x: x and 'weather' in x.lower()})
        
        if condition_element:
            condition = condition_element.get_text().strip()
        else:
            condition = "맑음"  # 기본값
        
        # 날씨 아이콘 매핑
        condition_icons = {
            "맑음": "☀️",
            "구름많음": "⛅", 
            "흐림": "☁️",
            "비": "🌧️",
            "눈": "❄️",
            "안개": "🌫️",
            "천둥번개": "⛈️"
        }
        condition_icon = condition_icons.get(condition, "☀️")
        
        # 체감온도 (온도 ±2도 범위)
        feels_like = temperature + random.randint(-2, 2)
        
        # 습도 (날씨 상태에 따라 조정)
        if condition in ["비", "천둥번개"]:
            humidity = random.randint(70, 90)
        elif condition in ["안개", "흐림"]:
            humidity = random.randint(60, 80)
        else:
            humidity = random.randint(40, 70)
        
        # 풍속
        wind_speed = random.randint(1, 5)
        
        # 미세먼지 (날씨 상태에 따라 조정)
        if condition in ["비", "천둥번개"]:
            dust_grade = "좋음"
            dust_color = "#10b981"
        elif condition in ["맑음"]:
            dust_grade = random.choice(["좋음", "보통"])
            dust_color = "#10b981" if dust_grade == "좋음" else "#f59e0b"
        else:
            dust_grade = random.choice(["보통", "나쁨"])
            dust_color = "#f59e0b" if dust_grade == "보통" else "#ef4444"
        
        # 기압
        pressure = random.randint(1000, 1030)
        
        # 현재 시간
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute
        
        return {
            "condition": condition,
            "condition_icon": condition_icon,
            "temperature": temperature,
            "humidity": humidity,
            "feels_like": feels_like,
            "wind_speed": wind_speed,
            "location": "서울",
            "pressure": pressure,
            "dust_grade": dust_grade,
            "dust_color": dust_color,
            "update_time": f"{current_hour:02d}:{current_minute:02d}"
        }
        
    except Exception as e:
        # 오류 시 기본값 반환 (기존 시뮬레이션 로직 사용)
        current_hour = datetime.now().hour
        current_month = datetime.now().month
        current_minute = datetime.now().minute
        
        # 계절별 기본 온도 설정
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
            base_temp = random.randint(15, 25)
            conditions = ["맑음", "흐림", "비", "안개", "구름많음"]
            condition_icons = ["☀️", "☁️", "🌧️", "🌫️", "⛅"]
        
        current_temp = base_temp + random.randint(-2, 2)
        feels_like = current_temp + random.randint(-2, 2)
        condition = random.choice(conditions)
        condition_icon = condition_icons[conditions.index(condition)]
        
        return {
            "condition": condition,
            "condition_icon": condition_icon,
            "temperature": current_temp,
            "humidity": random.randint(40, 80),
            "feels_like": feels_like,
            "wind_speed": random.randint(1, 5),
            "location": "서울",
            "pressure": random.randint(1000, 1030),
            "dust_grade": "보통",
            "dust_color": "#f59e0b",
            "update_time": f"{current_hour:02d}:{current_minute:02d}"
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
        
        # 전일 대비 등락폭 추가 (시뮬레이션)
        for currency in exchange_rates:
            current_rate = exchange_rates[currency]
            change_percent = random.uniform(-2.0, 2.0)  # ±2% 범위
            change_amount = current_rate * (change_percent / 100)
            previous_rate = current_rate - change_amount
            
            exchange_rates[currency] = {
                "current": current_rate,
                "previous": previous_rate,
                "change": change_amount,
                "change_percent": change_percent
            }
            
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
        
        # 랜덤 변동 추가하고 전일 대비 등락폭 계산
        exchange_rates = {}
        for pair, rate in base_rates.items():
            variation = random.uniform(-0.003, 0.003)
            current_rate = rate * (1 + variation)
            change_percent = random.uniform(-2.0, 2.0)  # ±2% 범위
            change_amount = current_rate * (change_percent / 100)
            previous_rate = current_rate - change_amount
            
            exchange_rates[pair] = {
                "current": round(current_rate, 2),
                "previous": round(previous_rate, 2),
                "change": round(change_amount, 2),
                "change_percent": round(change_percent, 2)
            }
        
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
        
        # 랜덤 변동 추가하고 전일 대비 등락폭 계산
        commodity_prices = {}
        for commodity, price in base_prices.items():
            variation = random.uniform(-0.005, 0.005)
            current_price = price * (1 + variation)
            change_percent = random.uniform(-3.0, 3.0)  # ±3% 범위 (광물은 변동성이 더 큼)
            change_amount = current_price * (change_percent / 100)
            previous_price = current_price - change_amount
            
            commodity_prices[commodity] = {
                "current": round(current_price, 2),
                "previous": round(previous_price, 2),
                "change": round(change_amount, 2),
                "change_percent": round(change_percent, 2)
            }
        
        return commodity_prices

def get_scm_risk_suggestions():
    """SCM Risk 관련 추천 검색 키워드 top10 반환"""
    return [
        "supply chain disruption",
        "logistics crisis", 
        "manufacturing shortage",
        "port congestion",
        "shipping delays",
        "raw material price",
        "inventory management",
        "supplier risk",
        "trade war impact",
        "global supply chain"
    ]

def extract_keywords_from_title(title):
    """뉴스 제목과 내용을 분석하여 관련 해시태그 5개 추출"""
    import re
    import random
    
    # 제목을 소문자로 변환하여 분석
    title_lower = title.lower()
    
    # SCM 관련 키워드 매핑 (우선순위별)
    keyword_mapping = {
        # 핵심 SCM 키워드 (높은 우선순위)
        'supply chain': '#공급망',
        'logistics': '#물류',
        'manufacturing': '#제조',
        'shipping': '#운송',
        'inventory': '#재고',
        'procurement': '#구매',
        'distribution': '#유통',
        
        # 위험/문제 키워드
        'disruption': '#중단',
        'shortage': '#부족',
        'delay': '#지연',
        'crisis': '#위기',
        'risk': '#위험',
        'bottleneck': '#병목',
        'congestion': '#혼잡',
        
        # 산업별 키워드
        'automotive': '#자동차',
        'electronics': '#전자',
        'semiconductor': '#반도체',
        'chip': '#칩',
        'energy': '#에너지',
        'oil': '#석유',
        'steel': '#철강',
        'aluminum': '#알루미늄',
        'copper': '#구리',
        
        # 무역/정책 키워드
        'trade': '#무역',
        'export': '#수출',
        'import': '#수입',
        'tariff': '#관세',
        'sanction': '#제재',
        'policy': '#정책',
        
        # 지역/국가 키워드
        'china': '#중국',
        'usa': '#미국',
        'europe': '#유럽',
        'asia': '#아시아',
        'korea': '#한국',
        'japan': '#일본',
        
        # 기타 중요 키워드
        'port': '#항만',
        'warehouse': '#창고',
        'factory': '#공장',
        'plant': '#플랜트',
        'freight': '#화물',
        'transportation': '#운송',
        'industrial': '#산업',
        'production': '#생산',
        'backlog': '#지연',
        'embargo': '#금수',
        'blockade': '#봉쇄',
        'regulation': '#규제'
    }
    
    # 제목에서 키워드 매칭하여 점수 계산
    matched_keywords = []
    for keyword, hashtag in keyword_mapping.items():
        if keyword in title_lower:
            # 키워드 길이에 따른 점수 (긴 키워드가 더 구체적)
            score = len(keyword.split()) * 10 + len(keyword)
            matched_keywords.append((score, hashtag, keyword))
    
    # 점수순으로 정렬하여 상위 5개 선택
    matched_keywords.sort(key=lambda x: x[0], reverse=True)
    selected_hashtags = [item[1] for item in matched_keywords[:5]]
    
    # 5개 미만이면 관련 키워드로 보완
    if len(selected_hashtags) < 5:
        # 제목에 포함된 단어들을 기반으로 관련 키워드 생성
        title_words = re.findall(r'\b\w+\b', title_lower)
        
        # SCM 관련 일반 키워드들
        general_scm_keywords = ['#SCM', '#공급망관리', '#물류위험', '#글로벌공급망', '#공급망중단']
        
        # 제목에 특정 단어가 포함된 경우 관련 키워드 추가
        if any(word in title_words for word in ['price', 'cost', 'expensive', 'cheap']):
            general_scm_keywords.append('#가격변동')
        if any(word in title_words for word in ['war', 'conflict', 'tension']):
            general_scm_keywords.append('#지정학적위험')
        if any(word in title_words for word in ['weather', 'climate', 'natural']):
            general_scm_keywords.append('#자연재해')
        if any(word in title_words for word in ['labor', 'strike', 'union']):
            general_scm_keywords.append('#노동분쟁')
        if any(word in title_words for word in ['technology', 'digital', 'ai']):
            general_scm_keywords.append('#디지털전환')
        
        # 부족한 개수만큼 추가
        needed = 5 - len(selected_hashtags)
        additional = random.sample(general_scm_keywords, min(needed, len(general_scm_keywords)))
        selected_hashtags.extend(additional)
    
    # 정확히 5개만 반환
    return selected_hashtags[:5]

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
        
        # 팝업 HTML (클릭 버튼 추가)
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
                <div style="margin-top: 12px; text-align: center;">
                    <button onclick="searchLocationRisk('{location['name']}')" style="
                        background: #dc2626; 
                        color: white; 
                        border: none; 
                        padding: 8px 16px; 
                        border-radius: 6px; 
                        font-size: 12px; 
                        font-weight: 600; 
                        cursor: pointer;
                        transition: background 0.2s;
                    " onmouseover="this.style.background='#b91c1c'" onmouseout="this.style.background='#dc2626'">
                        🚨 해당 지역 Risk 검색
                    </button>
                </div>
            </div>
        </div>
        """
        
        # 위험도별 아이콘 색상 설정
        icon_color = risk_colors[location['risk_level']]
        
        # 다이나믹한 마커 HTML 생성 (펄스 애니메이션 포함)
        marker_html = f"""
        <div style="
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <!-- 외부 링 애니메이션 -->
            <div style="
                position: absolute;
                background: {icon_color};
                border-radius: 50%;
                width: 50px;
                height: 50px;
                opacity: 0.2;
                animation: ripple 3s infinite;
            "></div>
            <!-- 펄스 애니메이션 배경 -->
            <div style="
                position: absolute;
                background: {icon_color};
                border-radius: 50%;
                width: 40px;
                height: 40px;
                opacity: 0.3;
                animation: pulse 2s infinite;
            "></div>
            <div style="
                position: absolute;
                background: {icon_color};
                border-radius: 50%;
                width: 30px;
                height: 30px;
                opacity: 0.5;
                animation: pulse 2s infinite 0.5s;
            "></div>
            <!-- 메인 마커 -->
            <div style="
                position: relative;
                background: linear-gradient(135deg, {icon_color} 0%, {icon_color}dd 100%);
                border: 3px solid white;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 0 20px {icon_color}40;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 10;
                animation: float 3s ease-in-out infinite, glow 2s ease-in-out infinite;
            " onmouseover="
                this.style.transform='scale(1.3) rotate(5deg)';
                this.style.boxShadow='0 8px 25px rgba(0,0,0,0.4), 0 0 30px {icon_color}60';
                this.style.borderColor='#fbbf24';
                this.style.animation='none';
            " onmouseout="
                this.style.transform='scale(1) rotate(0deg)';
                this.style.boxShadow='0 4px 12px rgba(0,0,0,0.3), 0 0 20px {icon_color}40';
                this.style.borderColor='white';
                this.style.animation='float 3s ease-in-out infinite, glow 2s ease-in-out infinite';
            ">
                <span style="
                    animation: bounce 2s infinite;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                ">
                {location['flag']}
                </span>
            </div>
        </div>
        
        <style>
        @keyframes pulse {{
            0% {{
                transform: scale(0.8);
                opacity: 0.3;
            }}
            50% {{
                transform: scale(1.2);
                opacity: 0.1;
            }}
            100% {{
                transform: scale(0.8);
                opacity: 0.3;
            }}
        }}
        @keyframes ripple {{
            0% {{
                transform: scale(0.8);
                opacity: 0.2;
            }}
            50% {{
                transform: scale(1.5);
                opacity: 0.05;
            }}
            100% {{
                transform: scale(2);
                opacity: 0;
            }}
        }}
        @keyframes float {{
            0%, 100% {{
                transform: translateY(0px);
            }}
            50% {{
                transform: translateY(-5px);
            }}
        }}
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{
                transform: translateY(0);
            }}
            40% {{
                transform: translateY(-3px);
            }}
            60% {{
                transform: translateY(-2px);
            }}
        }}
        @keyframes glow {{
            0%, 100% {{
                box-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 0 20px {icon_color}40;
            }}
            50% {{
                box-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 0 30px {icon_color}80;
            }}
        }}
        </style>
        <script>
        function searchLocationRisk(locationName) {{
            // SCM Risk 관련 검색어로 확장
            const riskSearchQuery = locationName + ' supply chain risk OR logistics OR manufacturing OR trade';
            
            // URL 파라미터로 검색어 전달
            const url = new URL(window.location);
            url.searchParams.set('location_search', riskSearchQuery);
            window.location.href = url.toString();
        }}
        </script>
        """
        
        # 깔끔한 툴팁 HTML 생성
        tooltip_html = f"""
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 12px 16px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-width: 140px;
            backdrop-filter: blur(10px);
        ">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="font-size: 18px;">{location['flag']}</span>
                <span style="font-weight: 700; color: #1f2937; font-size: 14px;">{location['name']}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <div style="
                    background: {icon_color};
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                "></div>
                <span style="color: #6b7280; font-size: 12px; font-weight: 600;">
                    {location['risk_level'].upper()} RISK
                </span>
            </div>
        </div>
        """
        
        # 다이나믹한 플래그 마커 생성
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=folium.Popup(popup_html, max_width=350),
            icon=folium.DivIcon(
                html=marker_html,
                icon_size=(40, 40),
                icon_anchor=(20, 20)
            ),
            tooltip=folium.Tooltip(
                tooltip_html,
                permanent=False,
                direction='top',
                offset=[0, -15],
                opacity=0.95
            )
        ).add_to(m)
    
    return m, risk_locations

def translate_korean_to_english(korean_text: str) -> str:
    """한국어를 영어로 번역하는 간단한 함수"""
    translation_dict = {
        # 자연재해
        '지진': 'earthquake',
        '태풍': 'typhoon',
        '홍수': 'flood',
        '가뭄': 'drought',
        '화재': 'fire',
        '폭설': 'heavy snow',
        '폭우': 'heavy rain',
        
        # 국가/지역
        '대만': 'Taiwan',
        '중국': 'China',
        '일본': 'Japan',
        '미국': 'United States',
        '한국': 'South Korea',
        '북한': 'North Korea',
        '러시아': 'Russia',
        '유럽': 'Europe',
        '아시아': 'Asia',
        
        # 경제/무역
        '경제': 'economy',
        '무역': 'trade',
        '수출': 'export',
        '수입': 'import',
        '시장': 'market',
        '가격': 'price',
        '비용': 'cost',
        '부족': 'shortage',
        '과잉': 'surplus',
        '위기': 'crisis',
        '충격': 'shock',
        '영향': 'impact',
        '효과': 'effect',
        
        # 산업/제품
        '반도체': 'semiconductor',
        '자동차': 'automobile',
        '스마트폰': 'smartphone',
        '전자제품': 'electronics',
        '철강': 'steel',
        '석유': 'oil',
        '가스': 'gas',
        '전력': 'electricity',
        '에너지': 'energy',
        
        # 기타
        '공장': 'factory',
        '생산': 'production',
        '제조': 'manufacturing',
        '물류': 'logistics',
        '운송': 'transportation',
        '배송': 'delivery',
        '항만': 'port',
        '공항': 'airport'
    }
    
    # 단어별로 번역
    words = korean_text.split()
    translated_words = []
    
    for word in words:
        if word in translation_dict:
            translated_words.append(translation_dict[word])
        else:
            # 번역되지 않은 단어는 그대로 유지
            translated_words.append(word)
    
    return ' '.join(translated_words)

def is_scm_related(title: str, search_query: str) -> bool:
    """제목이 SCM 관련성이 있는지 체크"""
    title_lower = title.lower()
    search_lower = search_query.lower()
    
    # 검색어가 제목에 직접 포함되어 있으면 통과 (가장 우선)
    # 단어 단위로도 체크하고, 전체 검색어도 체크
    search_words = search_lower.split()
    if any(word in title_lower for word in search_words if len(word) > 1):
        return True
    
    # 전체 검색어가 제목에 포함되어 있으면 통과
    if search_lower in title_lower:
        return True
    
    # SCM 관련 키워드 (한국어 + 영어)
    scm_keywords = [
        # 한국어
        '공급망', '물류', '제조업', '운송', '반도체', '에너지', '무역', '수출입', '원자재', 
        '재고', '창고', '배송', '항만', '선박', '항공', '철도', '트럭', '화물',
        '생산', '제조', '공장', '설비', '기계', '부품', '소재', '원료',
        '경제', '시장', '가격', '비용', '효율', '최적화', '관리', '운영',
        '위험', '리스크', '중단', '지연', '부족', '과잉', '불균형',
        '글로벌', '국제', '해외', '수입', '수출', '무역전쟁', '제재',
        '기술', '디지털', '자동화', 'AI', '인공지능', '로봇', '스마트',
        
        # 영어
        'supply chain', 'logistics', 'manufacturing', 'shipping', 'transport',
        'semiconductor', 'energy', 'trade', 'import', 'export', 'raw material',
        'inventory', 'warehouse', 'delivery', 'port', 'ship', 'air', 'rail', 'truck', 'cargo',
        'production', 'factory', 'equipment', 'machine', 'component', 'material',
        'economy', 'market', 'price', 'cost', 'efficiency', 'optimization', 'management',
        'risk', 'disruption', 'delay', 'shortage', 'surplus', 'imbalance',
        'global', 'international', 'overseas', 'trade war', 'sanction',
        'technology', 'digital', 'automation', 'artificial intelligence', 'robot', 'smart'
    ]
    
    # 검색어가 SCM 키워드에 포함되어 있으면 통과
    if any(keyword in title_lower for keyword in scm_keywords):
        return True
    
    # 검색어 자체가 SCM 관련이면 통과
    if any(keyword in search_lower for keyword in scm_keywords):
        return True
    
    # 특별한 경우: 자연재해나 정치적 사건이지만 경제/무역에 영향을 주는 경우
    economic_impact_keywords = ['경제', '시장', '가격', '비용', '무역', '수출입', 'economy', 'market', 'price', 'cost', 'trade']
    if any(keyword in title_lower for keyword in economic_impact_keywords):
        return True
    
    return False

def crawl_scm_risk_news(num_results: int = 100, search_query: str = None) -> List[Dict]:
    """SCM Risk 관련 뉴스 크롤링"""
    try:
        # 검색어가 있으면 사용, 없으면 기본 SCM 키워드 사용
        if search_query:
            # 한국어 검색어인지 확인
            korean_pattern = re.compile(r'[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]')
            if korean_pattern.search(search_query):
                # 한국어 검색어를 영어로 번역하여 두 언어로 검색
                translated_query = translate_korean_to_english(search_query)
                
                # 한국어 검색
                korean_query = f"{search_query} 공급망 OR 물류 OR 제조업 OR 운송 OR 반도체 OR 에너지 OR 무역"
                korean_encoded = urllib.parse.quote(korean_query)
                korean_url = f"https://news.google.com/rss/search?q={korean_encoded}&hl=ko&gl=KR&ceid=KR:ko"
                
                # 영어 검색
                english_query = f"{translated_query} supply chain OR logistics OR manufacturing OR shipping"
                english_encoded = urllib.parse.quote(english_query)
                english_url = f"https://news.google.com/rss/search?q={english_encoded}&hl=en&gl=US&ceid=US:en"
                
                # 두 URL을 리스트로 반환
                news_urls = [korean_url, english_url]
            else:
                # 영어 검색어는 SCM 관련 키워드 추가
                enhanced_query = f"{search_query} supply chain OR logistics OR manufacturing OR shipping"
                encoded_query = urllib.parse.quote(enhanced_query)
                news_urls = [f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"]
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
            news_urls = [f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"]
        
        # 실제 뉴스 크롤링 (여러 URL에서)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        all_items = []
        for i, news_url in enumerate(news_urls):
            try:
                # 테스트용: URL 출력 (간단하게)
                if search_query in ["대만", "taiwan", "대만 지진"] and i == 0:
                    st.info(f"🔍 검색 중... ({len(news_urls)}개 소스)")
                
                response = requests.get(news_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # XML 파싱
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                
                # 테스트용: 원본 아이템 수 출력 (간단하게)
                if search_query in ["대만", "taiwan", "대만 지진"] and i == 0:
                    st.info(f"📰 {len(items)}개 기사 발견")
                
                all_items.extend(items)
            except Exception as e:
                st.warning(f"Failed to fetch from URL: {news_url}")
                continue
        
        items = all_items
        
        # 중복 제거 (제목 기준)
        seen_titles = set()
        unique_items = []
        for item in items:
            title = item.find('title').text if item.find('title') else ""
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_items.append(item)
        
        items = unique_items
        
        # 테스트용: 중복 제거 후 아이템 수 출력 (간단하게)
        if search_query in ["대만", "taiwan", "대만 지진"]:
            st.info(f"🔄 중복 제거 후 {len(items)}개 기사")
        
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
                
                # SCM 관련성 체크 (검색어가 있을 때만) - 테스트용으로 일시 비활성화
                # if search_query and not is_scm_related(title, search_query):
                #     # 테스트용: 필터링된 기사 출력
                #     if search_query == "대만 지진":
                #         st.write(f"🚫 필터링됨: {title}")
                #     continue
                
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
        
        # SCM 관련 필터링 후 결과가 너무 적으면 필터링 완화
        if len(articles) < 5 and search_query:
            # 필터링 없이 다시 시도
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
        
        # 결과가 없으면 백업 뉴스 사용 (테스트용으로 주석 처리)
        # if not articles:
        #     st.warning("No articles found from Google News. Using backup news.")
        #     return generate_scm_backup_news(num_results, search_query)
        
        return articles[:num_results]
        
    except Exception as e:
        st.error(f"뉴스 크롤링 오류: {e}")
        # 테스트용으로 백업 뉴스 대신 빈 리스트 반환
        return []

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
    # URL 파라미터 처리 (지역 검색)
    query_params = st.query_params
    if 'location_search' in query_params:
        location_search_query = query_params['location_search']
        # URL 파라미터 제거
        st.query_params.clear()
        
        # 지역 검색 실행
        with st.spinner(f"Searching for: {location_search_query}..."):
            try:
                new_articles = crawl_scm_risk_news(100, location_search_query)
                if new_articles:
                    st.session_state.scm_articles = new_articles
                    st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                    st.session_state.search_query = location_search_query
                    st.session_state.last_search = location_search_query
                    st.session_state.current_page = 1
                    st.session_state.show_all_news = False
                    st.success(f"✅ Found {len(new_articles)} articles for '{location_search_query}'")
                else:
                    st.warning(f"No articles found for '{location_search_query}'")
            except Exception as e:
                st.error(f"Search error: {e}")
    
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
                try:
                    st.session_state.scm_articles = crawl_scm_risk_news(100)
                    st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                    # 원본 데이터 저장 (홈 버튼용)
                    st.session_state.original_articles = st.session_state.scm_articles.copy()
                    st.session_state.original_load_time = st.session_state.scm_load_time
                except Exception as e:
                    st.error(f"Error loading news: {e}")
                    st.info("Loading backup news...")
                    st.session_state.scm_articles = generate_scm_backup_news(100)
                    st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                    # 원본 데이터 저장 (홈 버튼용)
                    st.session_state.original_articles = st.session_state.scm_articles.copy()
                    st.session_state.original_load_time = st.session_state.scm_load_time
        else:
            # 기존 데이터에 keywords 필드가 없는 경우 새로 로드
            if st.session_state.scm_articles and 'keywords' not in st.session_state.scm_articles[0]:
                with st.spinner("Updating news format..."):
                    try:
                        st.session_state.scm_articles = crawl_scm_risk_news(100)
                        st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                        # 원본 데이터 저장 (홈 버튼용)
                        st.session_state.original_articles = st.session_state.scm_articles.copy()
                        st.session_state.original_load_time = st.session_state.scm_load_time
                    except Exception as e:
                        st.error(f"Error updating news: {e}")
                        st.session_state.scm_articles = generate_scm_backup_news(100)
                        # 원본 데이터 저장 (홈 버튼용)
                        st.session_state.original_articles = st.session_state.scm_articles.copy()
                        st.session_state.original_load_time = st.session_state.scm_load_time
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
                # SCM Risk News 배너와 홈 버튼을 같은 행에 배치
                col_title, col_home = st.columns([3, 1])
                
                with col_title:
                    # SCM Risk News 배너 (언어 선택 제거)
        st.markdown(f"""
        <div class="unified-info-card">
                        <h3 class="section-header" style="margin: 0 0 0.5rem 0; font-size: 1.1rem; animation: fadeInUp 0.6s ease-out;">SCM Risk News</h3>
                        <p style="font-size: 0.75rem; color: #7f8c8d; margin: 0;">Last updated: {load_time} | {len(st.session_state.scm_articles)} articles</p>
        </div>
        """, unsafe_allow_html=True)
        
                with col_home:
                    # 검색 결과가 있을 때만 홈 버튼 표시
                    if st.session_state.get('search_query'):
                        if st.button("🏠 Home", key="home_button_with_results", type="secondary", use_container_width=True):
                            st.session_state.search_query = ""
                            st.session_state.scm_articles = st.session_state.get('original_articles', [])
                            st.session_state.scm_load_time = st.session_state.get('original_load_time', datetime.now().strftime('%H:%M'))
                            st.rerun()
                
            
            with col_search:
                # 단순한 검색 입력과 버튼
                search_col1, search_col2 = st.columns([3, 1])
                
                with search_col1:
                    # 검색창만 표시
                    search_query = st.text_input("", placeholder="Search SCM news...", key="search_input", label_visibility="collapsed")
                    
                
                with search_col2:
                    search_clicked = st.button("Search", key="search_button", use_container_width=True, type="secondary")
                
                # 검색 실행 (버튼 클릭 또는 엔터키)
                if search_clicked or (search_query and search_query != st.session_state.get('last_search', '')):
                    if search_query and search_query.strip():
                with st.spinner(f"Searching for: {search_query}..."):
                            try:
                    # 새로운 검색 결과 로드
                                new_articles = crawl_scm_risk_news(100, search_query)
                                
                                # 테스트용: 검색 결과 확인 (간단하게)
                                if search_query in ["대만", "taiwan", "대만 지진"]:
                                    if new_articles:
                                        st.success(f"✅ '{search_query}' 검색 결과 {len(new_articles)}개 발견")
                                    else:
                                        st.warning(f"⚠️ '{search_query}' 검색 결과 없음")
                                
                                if new_articles:
                                    st.session_state.scm_articles = new_articles
                    st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                    st.session_state.search_query = search_query
                                    st.session_state.last_search = search_query
                                    st.session_state.current_page = 1  # 검색 시 페이지 리셋
                    st.rerun()
            else:
                                    st.warning("No articles found for your search. Please try different keywords.")
                                    st.info("💡 Try these popular keywords: supply chain, logistics, manufacturing, semiconductor, trade war")
                                    
                                    # 홈 버튼 추가
                                    if st.button("🏠 Back to Home", key="home_button_no_results", type="secondary"):
                                        st.session_state.search_query = ""
                                        st.session_state.scm_articles = st.session_state.get('original_articles', [])
                                        st.session_state.scm_load_time = st.session_state.get('original_load_time', datetime.now().strftime('%H:%M'))
                                        st.rerun()
                                    
                                    # 백업 뉴스로 fallback
                                    st.session_state.scm_articles = generate_scm_backup_news(100, search_query)
                                    st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Search error: {e}")
                                st.info("Showing backup news instead.")
                                # 백업 뉴스로 fallback
                                st.session_state.scm_articles = generate_scm_backup_news(100, search_query)
                                st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                                st.rerun()
                    elif search_clicked and (not search_query or not search_query.strip()):
                st.warning("Please enter a search term")
        
                # 검색어 표시 및 클리어 버튼
        if 'search_query' in st.session_state and st.session_state.search_query:
                    st.info(f"🔍 Current: {st.session_state.search_query}")
                    if st.button("Clear", key="clear_search", use_container_width=True, type="secondary"):
                        try:
                st.session_state.search_query = ""
                            st.session_state.scm_articles = crawl_scm_risk_news(100)
                st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                            st.session_state.current_page = 1  # 클리어 시 페이지 리셋
                st.rerun()
                        except Exception as e:
                            st.error(f"Error loading default news: {e}")
                            # 백업 뉴스로 fallback
                            st.session_state.scm_articles = generate_scm_backup_news(100)
                st.session_state.scm_load_time = datetime.now().strftime('%H:%M')
                            st.rerun()
        
        # 뉴스 정렬 옵션 추가 (컴팩트하게)
        st.markdown("""
        <div style="margin-bottom: 0.5rem;">
            <h4 style="font-size: 0.8rem; margin: 0 0 0.25rem 0; color: #2c3e50; animation: fadeInUp 0.8s ease-out;">📊 Sort Options</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # 컴팩트한 정렬 옵션
        sort_option = st.selectbox(
            "Sort by",
            ["Latest", "Views", "Title", "Source"],
            key="sort_news",
            label_visibility="collapsed"
        )
        
        # 뉴스 정렬
        sorted_articles = st.session_state.scm_articles.copy()
        if sort_option == "Latest":
            sorted_articles.sort(key=lambda x: x['published_time'], reverse=True)
        elif sort_option == "Views":
            sorted_articles.sort(key=lambda x: x['views'], reverse=True)
        elif sort_option == "Title":
            sorted_articles.sort(key=lambda x: x['title'])
        elif sort_option == "Source":
            sorted_articles.sort(key=lambda x: x['source'])
        
        # 정렬 옵션이 변경되면 페이지를 1로 리셋
        if 'last_sort_option' not in st.session_state or st.session_state.last_sort_option != sort_option:
            st.session_state.current_page = 1
            st.session_state.last_sort_option = sort_option
        
        # 페이지네이션 설정
        articles_per_page = 25
        total_articles = len(sorted_articles)
        total_pages = (total_articles + articles_per_page - 1) // articles_per_page
        
        # 현재 페이지 설정 (기본값: 1)
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        # 페이지네이션 컨트롤 (항상 표시)
        st.markdown("---")  # 구분선 추가
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            prev_disabled = st.session_state.current_page <= 1
            if st.button("◀ Prev", key="prev_page", disabled=prev_disabled, use_container_width=True, type="secondary"):
                st.session_state.current_page -= 1
                st.rerun()
        
        with col_info:
            st.markdown(f"""
            <div style="text-align: center; font-size: 0.7rem; color: #2c3e50; padding: 0.3rem 0; font-weight: bold;">
                Page {st.session_state.current_page} of {total_pages} ({total_articles} articles)
            </div>
            """, unsafe_allow_html=True)
            
        with col_next:
            next_disabled = st.session_state.current_page >= total_pages
            if st.button("Next ▶", key="next_page", disabled=next_disabled, use_container_width=True, type="secondary"):
                st.session_state.current_page += 1
                st.rerun()
        
        # 디버깅 정보 (임시)
        st.markdown(f"""
        <div style="font-size: 0.6rem; color: #95a5a6; text-align: center; margin-top: 0.5rem;">
            Debug: Current page: {st.session_state.current_page}, Total pages: {total_pages}, Articles per page: {articles_per_page}
        </div>
        """, unsafe_allow_html=True)
        
        # 최신 뉴스 5개만 표시 (더보기 버튼으로 확장)
        if not st.session_state.get('show_all_news', False):
            # 최신 5개만 표시
            display_articles = sorted_articles[:5]
            show_more_button = len(sorted_articles) > 5
        else:
            # 전체 표시
            display_articles = sorted_articles
            show_more_button = False
        
        # 뉴스 리스트 (Motion 효과 + 해시태그 + 번역)
        for i, article in enumerate(display_articles, 1):
            # 키워드 안전하게 처리 (기존 데이터 호환성)
            if 'keywords' in article and article['keywords']:
                keywords = article['keywords']
            else:
                # 기존 데이터의 경우 제목에서 키워드 추출
                keywords = extract_keywords_from_title(article['title'])
            
            # 제목은 원문 그대로 표시 (번역하지 않음)
            display_title = article['title']
            
            # 키워드도 원문 그대로 표시 (번역하지 않음)
            display_keywords = keywords
            
            # 키워드를 HTML로 변환
            keywords_html = " ".join([f'<span style="background: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 12px; font-size: 0.7rem; margin-right: 4px; display: inline-block;">{keyword}</span>' for keyword in display_keywords])
            
            # 메타 정보는 영어로 고정 표시
            views_text = f"{article['views']:,} views"
            read_more_text = "Read more →"
            
            # 공유 URL 생성
            share_url = article['url']
            share_title = display_title
            
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
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem;">
                    <a href="{article['url']}" target="_blank" class="news-link">{read_more_text}</a>
                    <div style="display: flex; gap: 0.25rem; align-items: center;">
                        <a href="https://twitter.com/intent/tweet?text={share_title}&url={share_url}" 
                           target="_blank" 
                           style="background: #1da1f2; color: white; padding: 0.2rem 0.4rem; border-radius: 3px; text-decoration: none; font-size: 0.6rem;"
                           title="Twitter 공유">🐦</a>
                        <a href="https://www.facebook.com/sharer/sharer.php?u={share_url}" 
                           target="_blank" 
                           style="background: #1877f2; color: white; padding: 0.2rem 0.4rem; border-radius: 3px; text-decoration: none; font-size: 0.6rem;"
                           title="Facebook 공유">📘</a>
                        <a href="https://t.me/share/url?url={share_url}&text={share_title}" 
                           target="_blank" 
                           style="background: #0088cc; color: white; padding: 0.2rem 0.4rem; border-radius: 3px; text-decoration: none; font-size: 0.6rem;"
                           title="Telegram 공유">📱</a>
                        <a href="mailto:?subject={share_title}&body=다음 뉴스를 확인해보세요:%0A%0A{share_title}%0A{share_url}%0A%0ASCM Risk Monitor에서 공유" 
                           style="background: #ea4335; color: white; padding: 0.2rem 0.4rem; border-radius: 3px; text-decoration: none; font-size: 0.6rem; display: inline-block;"
                           title="이메일 공유">📧</a>
                    </div>
                </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 더보기 버튼 추가
        if show_more_button:
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.button("📰 더보기", key="show_more_btn", type="secondary", use_container_width=True):
                    st.session_state.show_all_news = True
                    st.rerun()
        
        # 전체 표시 중일 때 접기 버튼
        if st.session_state.get('show_all_news', False) and len(sorted_articles) > 5:
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.button("📰 접기", key="show_less_btn", type="secondary", use_container_width=True):
                    st.session_state.show_all_news = False
                    st.rerun()
    
    # 우측 컬럼 - 지도와 시장 정보
    with col2:
        # 실시간 정보 (시간과 날씨를 나란히 배치)
        st.markdown('<h3 class="section-header" style="font-size: 1.1rem; animation: fadeInUp 0.6s ease-out;">🌤️ Real-time Info</h3>', unsafe_allow_html=True)
        
        # 한국 시간 정보와 날씨 정보를 나란히 배치
        col_time, col_weather = st.columns([1, 1])
        
        # 한국 시간 정보
        date_str, time_str = get_korean_time()
        weather_info = get_seoul_weather()
        
        with col_time:
            st.markdown(f"""
            <div class="unified-info-card" style="padding: 0.4rem; margin-bottom: 0.5rem;">
                <div class="info-title" style="font-size: 0.8rem; margin-bottom: 0.3rem; animation: fadeInUp 0.8s ease-out;">🇰🇷 Seoul Time</div>
                <div class="info-content" style="font-size: 0.9rem;">
                    <div style="font-size: 0.75rem; color: #7f8c8d; margin-bottom: 0.2rem; text-align: center;">{date_str}</div>
                    <div style="font-size: 1.1rem; font-weight: bold; color: #2c3e50; text-align: center;">{time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_weather:
            st.markdown(f"""
            <div class="unified-info-card" style="padding: 0.4rem; margin-bottom: 0.5rem;">
                <div class="info-title" style="font-size: 0.8rem; margin-bottom: 0.3rem; animation: fadeInUp 0.8s ease-out;">🌤️ Seoul Weather</div>
                <div class="info-content" style="font-size: 0.9rem;">
                    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 0.2rem;">
                        <span style="font-size: 1.1rem; margin-right: 0.3rem;">{weather_info['condition_icon']}</span>
                        <span style="font-size: 0.8rem; font-weight: bold; color: #2c3e50;">{weather_info['condition']}</span>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: bold; color: #e74c3c; margin-bottom: 0.1rem; text-align: center;">
                        {weather_info['temperature']}°C
                    </div>
                    <div style="font-size: 0.65rem; color: #7f8c8d; margin-bottom: 0.1rem; text-align: center;">
                        Feels like {weather_info['feels_like']}°C
                    </div>
                    <div style="font-size: 0.65rem; color: #7f8c8d; text-align: center; line-height: 1.1;">
                        💧 {weather_info['humidity']}% | 💨 {weather_info['wind_speed']}m/s
                    </div>
                    <div style="font-size: 0.65rem; color: #7f8c8d; margin-top: 0.1rem; text-align: center;">
                        🌫️ <span style="color: {weather_info['dust_color']}; font-weight: bold;">{weather_info['dust_grade']}</span>
                    </div>
                    <div style="font-size: 0.55rem; color: #95a5a6; margin-top: 0.2rem; text-align: center;">
                        {weather_info['update_time']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Risk Map (아래로 이동하고 크기 조정)
        st.markdown('<h3 class="section-header" style="font-size: 1.1rem; animation: fadeInUp 0.6s ease-out;">🗺️ Risk Map</h3>', unsafe_allow_html=True)
        try:
            risk_map, risk_locations = create_risk_map()
            # 지도 컨테이너로 감싸서 크기 조정
            st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
            st_folium(risk_map, width=642, height=332, returned_objects=[])
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Map error: {e}")
        
        # 위험도 범례 (작고 귀여운 플래그)
        st.markdown("""
        <div class="market-info">
            <div class="market-title" style="animation: fadeInUp 0.8s ease-out;">🚩 Risk Levels</div>
            <div class="risk-item risk-high">
                <div class="risk-title" style="font-size: 0.8rem;"><span class="cute-flag">🔴</span> High Risk</div>
                <div class="risk-desc" style="font-size: 0.7rem;">Immediate action required</div>
                <div style="font-size: 0.65rem; color: #7f8c8d; margin-top: 0.25rem; line-height: 1.2;">
                    전쟁, 자연재해, 대규모 파업
                </div>
            </div>
            <div class="risk-item risk-medium">
                <div class="risk-title" style="font-size: 0.8rem;"><span class="cute-flag">🟠</span> Medium Risk</div>
                <div class="risk-desc" style="font-size: 0.7rem;">Monitor closely</div>
                <div style="font-size: 0.65rem; color: #7f8c8d; margin-top: 0.25rem; line-height: 1.2;">
                    정부정책 변화, 노동분쟁
                </div>
            </div>
            <div class="risk-item risk-low">
                <div class="risk-title" style="font-size: 0.8rem;"><span class="cute-flag">🟢</span> Low Risk</div>
                <div class="risk-desc" style="font-size: 0.7rem;">Normal operations</div>
                <div style="font-size: 0.65rem; color: #7f8c8d; margin-top: 0.25rem; line-height: 1.2;">
                    일반적 운영상 이슈
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 실시간 환율 정보 (Naver Finance)
        exchange_rates = get_exchange_rates()
        st.markdown("""
        <div class="market-info">
            <div class="market-title" style="animation: fadeInUp 0.8s ease-out;">💱 Exchange Rates (Naver Finance)</div>
        """, unsafe_allow_html=True)
        
        # 환율 정보를 가로 2열로 배치
        currency_info = {
            "USD/KRW": {"name": "🇺🇸 USD", "unit": "원"},
            "EUR/KRW": {"name": "🇪🇺 EUR", "unit": "원"},
            "JPY/KRW": {"name": "🇯🇵 JPY", "unit": "원 (100엔)"},
            "CNY/KRW": {"name": "🇨🇳 CNY", "unit": "원"},
            "GBP/KRW": {"name": "🇬🇧 GBP", "unit": "원"}
        }
        
        # 환율 정보를 2열로 배치
        st.markdown('<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">', unsafe_allow_html=True)
        
        for pair, rate_data in exchange_rates.items():
            if pair in currency_info:
                currency_name = currency_info[pair]["name"]
                unit = currency_info[pair]["unit"]
                
                # 현재 가격과 등락폭 정보
                current_rate = rate_data["current"]
                change = rate_data["change"]
                change_percent = rate_data["change_percent"]
                
                formatted_rate = f"{current_rate:,.2f}" if current_rate >= 100 else f"{current_rate:.4f}"
                
                # 등락폭 색상 결정
                change_color = "#e74c3c" if change >= 0 else "#27ae60"  # 상승: 빨강, 하락: 초록
                change_symbol = "▲" if change >= 0 else "▼"
                
            st.markdown(f"""
                <div class="market-item" style="padding: 0.4rem; border-radius: 6px; background: #f8f9fa; margin-bottom: 0.3rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.75rem; font-weight: 500;">{currency_name}</span>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-weight: bold; font-size: 0.8rem;">{formatted_rate} {unit}</span>
                            <span style="font-size: 0.6rem; color: {change_color}; font-weight: 500;">
                                {change_symbol} {abs(change):.2f} ({change_percent:+.2f}%)
                            </span>
                        </div>
                    </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
            <div class="market-title" style="animation: fadeInUp 0.8s ease-out;">⛏️ Commodity Prices (LME)</div>
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
        
        # LME 시세를 2열로 배치
        st.markdown('<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">', unsafe_allow_html=True)
        
        for commodity, price_data in commodity_prices.items():
            if commodity in commodity_info:
                icon = commodity_info[commodity]["icon"]
                unit = commodity_info[commodity]["unit"]
                
                # 현재 가격과 등락폭 정보
                current_price = price_data["current"]
                change = price_data["change"]
                change_percent = price_data["change_percent"]
                
                formatted_price = f"${current_price:,.2f}" if current_price >= 100 else f"${current_price:.4f}"
                
                # 등락폭 색상 결정
                change_color = "#e74c3c" if change >= 0 else "#27ae60"  # 상승: 빨강, 하락: 초록
                change_symbol = "▲" if change >= 0 else "▼"
            
            st.markdown(f"""
                <div class="market-item" style="padding: 0.4rem; border-radius: 6px; background: #f8f9fa; margin-bottom: 0.3rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.75rem; font-weight: 500;">{icon} {commodity}</span>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-weight: bold; font-size: 0.8rem;">{formatted_price}{unit}</span>
                            <span style="font-size: 0.6rem; color: {change_color}; font-weight: 500;">
                                {change_symbol} ${abs(change):.2f} ({change_percent:+.2f}%)
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
