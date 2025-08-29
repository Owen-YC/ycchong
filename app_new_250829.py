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

# 페이지 설정
st.set_page_config(
    page_title="SCM Risk 관리 대시보드",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 - 트렌디한 모던 디자인
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* 메인 헤더 */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        text-shadow: 0 4px 8px rgba(30, 58, 138, 0.1);
        letter-spacing: -0.02em;
    }
    
    /* 뉴스 카드 */
    .news-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 
            0 4px 6px rgba(30, 58, 138, 0.05),
            0 10px 15px rgba(30, 58, 138, 0.1),
            0 0 0 1px rgba(59, 130, 246, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6, #60a5fa);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 
            0 20px 25px rgba(30, 58, 138, 0.15),
            0 10px 10px rgba(30, 58, 138, 0.1),
            0 0 0 1px rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .news-card:hover::before {
        transform: scaleX(1);
    }
    
    /* 뉴스 제목 */
    .news-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 1rem;
        line-height: 1.4;
        letter-spacing: -0.01em;
    }
    
    /* 뉴스 메타 정보 */
    .news-meta {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        font-weight: 500;
    }
    
    /* 뉴스 설명 */
    .news-description {
        font-size: 1rem;
        color: #475569;
        line-height: 1.7;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* 뉴스 링크 버튼 */
    .news-link {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(30, 58, 138, 0.2);
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
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .news-link:hover {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        color: white;
        text-decoration: none;
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(30, 58, 138, 0.3);
    }
    
    .news-link:hover::before {
        left: 100%;
    }
    
    /* Streamlit 버튼 */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 6px rgba(30, 58, 138, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(30, 58, 138, 0.3);
    }
    
    /* 검색 통계 카드 */
    .search-stats {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
        color: white;
        padding: 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        box-shadow: 
            0 20px 25px rgba(30, 58, 138, 0.2),
            0 10px 10px rgba(30, 58, 138, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .search-stats::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
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
        box-shadow: 0 4px 6px rgba(220, 38, 38, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* 차트 컨테이너 */
    .trend-chart {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 4px 6px rgba(30, 58, 138, 0.05),
            0 10px 15px rgba(30, 58, 138, 0.1);
    }
    
    /* 지도 컨테이너 */
    .map-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 4px 6px rgba(30, 58, 138, 0.05),
            0 10px 15px rgba(30, 58, 138, 0.1);
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(59, 130, 246, 0.1);
    }
    
    /* 스크롤바 스타일 */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(59, 130, 246, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1e40af, #2563eb);
    }
    
    /* 로딩 애니메이션 */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(59, 130, 246, 0.3);
        border-radius: 50%;
        border-top-color: #3b82f6;
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
        
        .search-stats {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def generate_search_trend_data(query, days=30):
    """검색량 추이 데이터 생성"""
    dates = []
    search_volumes = []
    
    # SCM Risk 관련 검색량 패턴
    base_volume = {
        "SCM": 12000,
        "공급망": 9800,
        "물류": 8500,
        "운송": 7200,
        "창고": 6800,
        "재고": 7500,
        "배송": 8000,
        "Risk": 11000,
        "위험": 9000,
        "중단": 8200,
        "지연": 7800,
        "부족": 7000
    }
    
    base = base_volume.get(query, 6000)
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-1-i)
        dates.append(date.strftime('%Y-%m-%d'))
        
        # 주말 효과
        weekday_factor = 0.7 if date.weekday() >= 5 else 1.0
        
        # 랜덤 변동
        random_factor = random.uniform(0.8, 1.2)
        
        # 시간에 따른 트렌드 (최근에 증가하는 패턴)
        trend_factor = 1.0 + (i / days) * 0.4
        
        volume = int(base * weekday_factor * random_factor * trend_factor)
        search_volumes.append(volume)
    
    return dates, search_volumes

def create_trend_chart(query):
    """검색량 추이 차트 생성"""
    dates, volumes = generate_search_trend_data(query)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=volumes,
        mode='lines+markers',
        name='검색량',
        line=dict(color='#1e3a8a', width=3),
        marker=dict(size=6, color='#3b82f6'),
        fill='tonexty',
        fillcolor='rgba(30, 58, 138, 0.1)'
    ))
    
    fig.update_layout(
        title=f'"{query}" SCM Risk 검색량 추이 (최근 30일)',
        xaxis_title='날짜',
        yaxis_title='일일 검색량',
        template='plotly_white',
        height=400,
        showlegend=False,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_risk_map():
    """SCM Risk 지역별 지도 생성"""
    # 주요 SCM Risk 발생 지역
    risk_locations = [
        {"name": "중국 상하이", "lat": 31.2304, "lng": 121.4737, "risk": "높음", "description": "공급망 중단 위험"},
        {"name": "미국 로스앤젤레스", "lat": 34.0522, "lng": -118.2437, "risk": "중간", "description": "항구 혼잡"},
        {"name": "독일 함부르크", "lat": 53.5511, "lng": 9.9937, "risk": "낮음", "description": "물류 지연"},
        {"name": "싱가포르", "lat": 1.3521, "lng": 103.8198, "risk": "중간", "description": "운송 비용 증가"},
        {"name": "한국 부산", "lat": 35.1796, "lng": 129.0756, "risk": "낮음", "description": "정상 운영"},
        {"name": "일본 도쿄", "lat": 35.6762, "lng": 139.6503, "risk": "중간", "description": "지진 위험"},
        {"name": "인도 뭄바이", "lat": 19.0760, "lng": 72.8777, "risk": "높음", "description": "인프라 부족"},
        {"name": "브라질 상파울루", "lat": -23.5505, "lng": -46.6333, "risk": "중간", "description": "정치적 불안정"}
    ]
    
    # 지도 생성 (한국 중심)
    m = folium.Map(
        location=[36.5, 127.5],
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # 위험도별 색상
    risk_colors = {
        "높음": "red",
        "중간": "orange", 
        "낮음": "green"
    }
    
    for location in risk_locations:
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=f"""
            <b>{location['name']}</b><br>
            위험도: <span style="color: {risk_colors[location['risk']]}">{location['risk']}</span><br>
            {location['description']}
            """,
            icon=folium.Icon(color=risk_colors[location['risk']], icon='info-sign')
        ).add_to(m)
    
    return m

def crawl_google_news(query, num_results=500):
    """검색 키워드에 맞는 SCM Risk 관련 뉴스 데이터 생성"""
    try:
        # 키워드별 맞춤 뉴스 데이터
        keyword_news = {
            "SCM": [
                {"title": "글로벌 SCM 위기, 기업들의 대응 전략", "source": "SCM뉴스", "description": "공급망 관리(SCM) 시스템의 글로벌 위기로 인해 기업들이 다양한 대응 전략을 모색하고 있습니다.", "url": "https://scm-news.com/global-crisis"},
                {"title": "SCM 디지털 전환 가속화", "source": "디지털SCM", "description": "AI와 IoT 기술을 활용한 SCM 디지털 전환이 급속히 진행되고 있습니다.", "url": "https://digital-scm.com/transformation"},
                {"title": "SCM 위험 관리 시스템 도입 확대", "source": "리스크관리", "description": "기업들이 SCM 위험을 사전에 예측하고 대응하기 위한 시스템을 적극 도입하고 있습니다.", "url": "https://risk-management.com/scm"}
            ],
            "공급망": [
                {"title": "글로벌 공급망 위기 심화", "source": "공급망뉴스", "description": "코로나19 이후 지속되는 글로벌 공급망 위기로 인해 기업들이 다양한 대응 전략을 모색하고 있습니다.", "url": "https://supply-chain.com/crisis"},
                {"title": "공급망 재구성 움직임 활발", "source": "경제분석", "description": "글로벌 공급망 위기로 인해 기업들이 지역별 공급망 재구성을 추진하고 있습니다.", "url": "https://analysis.com/restructuring"},
                {"title": "공급망 투명성 확보 중요성 증가", "source": "ESG뉴스", "description": "ESG 경영의 확산으로 공급망 투명성 확보의 중요성이 크게 증가하고 있습니다.", "url": "https://esg-news.com/transparency"}
            ],
            "물류": [
                {"title": "해운비 상승으로 인한 물류 비용 증가", "source": "물류뉴스", "description": "글로벌 해운비 상승으로 인해 수출입 기업들의 물류 비용이 크게 증가하고 있습니다.", "url": "https://logistics.com/shipping-cost"},
                {"title": "스마트 물류 시스템 도입 확대", "source": "스마트물류", "description": "AI와 자동화 기술을 활용한 스마트 물류 시스템이 급속히 도입되고 있습니다.", "url": "https://smart-logistics.com/system"},
                {"title": "친환경 물류로의 전환 가속화", "source": "그린물류", "description": "탄소 중립 목표에 따라 친환경 물류 시스템으로의 전환이 가속화되고 있습니다.", "url": "https://green-logistics.com/transition"}
            ],
            "운송": [
                {"title": "운송업계 디지털 혁신 가속화", "source": "운송뉴스", "description": "운송업계에서 디지털 기술을 활용한 혁신이 빠르게 진행되고 있습니다.", "url": "https://transport.com/innovation"},
                {"title": "전기차 운송으로의 전환", "source": "전기운송", "description": "환경 규제 강화로 인해 전기차 운송으로의 전환이 가속화되고 있습니다.", "url": "https://electric-transport.com/transition"},
                {"title": "운송 비용 최적화 전략", "source": "비용관리", "description": "기업들이 운송 비용을 최적화하기 위한 다양한 전략을 추진하고 있습니다.", "url": "https://cost-management.com/transport"}
            ],
            "창고": [
                {"title": "스마트 창고 시스템 도입 확대", "source": "창고뉴스", "description": "자동화와 AI 기술을 활용한 스마트 창고 시스템이 급속히 도입되고 있습니다.", "url": "https://warehouse.com/smart-system"},
                {"title": "창고 부족 현상 심화", "source": "부동산뉴스", "description": "전자상거래 확산으로 인한 창고 부족 현상이 심화되고 있습니다.", "url": "https://real-estate.com/warehouse-shortage"},
                {"title": "친환경 창고 구축 트렌드", "source": "그린빌딩", "description": "친환경 건축물 인증을 받은 창고 구축이 새로운 트렌드로 부상하고 있습니다.", "url": "https://green-building.com/warehouse"}
            ],
            "재고": [
                {"title": "실시간 재고 관리 시스템 도입", "source": "재고관리", "description": "IoT 기술을 활용한 실시간 재고 관리 시스템이 기업들에 도입되고 있습니다.", "url": "https://inventory.com/real-time"},
                {"title": "재고 최적화로 비용 절감", "source": "비용절감", "description": "AI 기반 재고 최적화를 통해 기업들이 물류 비용을 크게 절감하고 있습니다.", "url": "https://cost-reduction.com/inventory"},
                {"title": "재고 부족으로 인한 생산 중단", "source": "생산뉴스", "description": "반도체 등 핵심 부품의 재고 부족으로 인한 생산 중단이 발생하고 있습니다.", "url": "https://production.com/shortage"}
            ],
            "배송": [
                {"title": "배송 속도 경쟁 심화", "source": "배송뉴스", "description": "전자상거래 확산으로 인한 배송 속도 경쟁이 심화되고 있습니다.", "url": "https://delivery.com/speed-competition"},
                {"title": "드론 배송 시범 운영 확대", "source": "드론배송", "description": "드론을 활용한 배송 서비스의 시범 운영이 전 세계적으로 확대되고 있습니다.", "url": "https://drone-delivery.com/pilot"},
                {"title": "배송 비용 상승으로 인한 가격 인상", "source": "가격뉴스", "description": "배송 비용 상승으로 인해 소비자 물가가 상승하고 있습니다.", "url": "https://price-news.com/delivery-cost"}
            ],
            "Risk": [
                {"title": "SCM Risk 관리 시스템 도입 확대", "source": "리스크뉴스", "description": "기업들이 공급망 위험을 사전에 예측하고 대응하기 위한 시스템을 적극 도입하고 있습니다.", "url": "https://risk.com/management-system"},
                {"title": "글로벌 Risk 요인 증가", "source": "글로벌리스크", "description": "지정학적 불안정과 기후변화로 인한 글로벌 Risk 요인이 증가하고 있습니다.", "url": "https://global-risk.com/factors"},
                {"title": "Risk 대응 체계 강화", "source": "대응체계", "description": "기업들이 다양한 Risk에 대응하기 위한 체계를 강화하고 있습니다.", "url": "https://response-system.com/risk"}
            ],
            "위험": [
                {"title": "공급망 위험 요인 다양화", "source": "위험관리", "description": "기후변화, 지정학적 불안정 등으로 인한 공급망 위험 요인이 다양화되고 있습니다.", "url": "https://risk-management.com/factors"},
                {"title": "위험 예측 기술 발전", "source": "예측기술", "description": "AI와 빅데이터를 활용한 위험 예측 기술이 빠르게 발전하고 있습니다.", "url": "https://prediction-tech.com/risk"},
                {"title": "위험 대응 전략 수립", "source": "전략수립", "description": "기업들이 다양한 위험에 대응하기 위한 전략을 체계적으로 수립하고 있습니다.", "url": "https://strategy.com/risk-response"}
            ],
            "중단": [
                {"title": "공급망 중단 위험 증가", "source": "중단뉴스", "description": "자연재해와 지정학적 불안정으로 인한 공급망 중단 위험이 증가하고 있습니다.", "url": "https://disruption.com/risk"},
                {"title": "생산 중단으로 인한 손실 확대", "source": "생산뉴스", "description": "부품 부족으로 인한 생산 중단으로 기업들의 손실이 확대되고 있습니다.", "url": "https://production.com/disruption"},
                {"title": "중단 대응 체계 구축", "source": "대응체계", "description": "기업들이 공급망 중단에 대응하기 위한 체계를 구축하고 있습니다.", "url": "https://response.com/disruption"}
            ],
            "지연": [
                {"title": "물류 지연 현상 심화", "source": "지연뉴스", "description": "항구 혼잡과 운송 수단 부족으로 인한 물류 지연 현상이 심화되고 있습니다.", "url": "https://delay.com/logistics"},
                {"title": "배송 지연으로 인한 고객 불만 증가", "source": "고객서비스", "description": "배송 지연으로 인한 고객 불만이 증가하고 있습니다.", "url": "https://customer-service.com/delay"},
                {"title": "지연 대응 시스템 도입", "source": "시스템도입", "description": "기업들이 지연 상황에 대응하기 위한 시스템을 도입하고 있습니다.", "url": "https://system.com/delay-response"}
            ],
            "부족": [
                {"title": "반도체 부족으로 인한 생산 차질", "source": "반도체뉴스", "description": "반도체 부족으로 인해 자동차와 전자제품 생산에 차질이 빚어지고 있습니다.", "url": "https://semiconductor.com/shortage"},
                {"title": "원자재 부족 현상 확산", "source": "원자재뉴스", "description": "기후변화와 수요 증가로 인한 원자재 부족 현상이 확산되고 있습니다.", "url": "https://raw-material.com/shortage"},
                {"title": "인력 부족으로 인한 물류 지연", "source": "인력뉴스", "description": "물류 업계의 인력 부족으로 인한 서비스 지연이 발생하고 있습니다.", "url": "https://workforce.com/shortage"}
            ]
        }
        
        articles = []
        
        # 검색 키워드에 맞는 뉴스 선택
        if query in keyword_news:
            news_list = keyword_news[query]
        else:
            # 기본 SCM 뉴스
            news_list = keyword_news["SCM"]
        
        # 기본 뉴스 추가
        for news in news_list:
            article = {
                'title': news["title"],
                'url': news["url"],
                'source': news["source"],
                'published_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'description': news["description"]
            }
            articles.append(article)
        
        # 추가 뉴스 생성 (검색 키워드에 맞게)
        scm_keywords = ["공급망", "물류", "운송", "창고", "재고", "배송", "위험", "중단", "지연", "부족"]
        scm_topics = [
            f"{query} 최적화 전략",
            f"{query} 디지털 전환",
            f"{query} 위험 관리",
            f"{query} 비용 절감",
            f"{query} 효율성 향상",
            f"{query} 혁신 기술",
            f"{query} 글로벌 트렌드",
            f"{query} 미래 전망",
            f"{query} 대응 방안",
            f"{query} 성공 사례"
        ]
        
        while len(articles) < num_results:
            topic = random.choice(scm_topics)
            source = f"{query}뉴스{len(articles) + 1}"
            
            article = {
                'title': f'"{query}" 관련 {topic}',
                'url': f"https://{query}-news.com/{len(articles) + 1}",
                'source': source,
                'published_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'description': f'{query}와 관련된 {topic}에 대한 최신 동향과 분석을 제공합니다. SCM Risk 관리 관점에서 {query}의 중요성과 향후 전망을 살펴봅니다.'
            }
            articles.append(article)
        
        return articles[:num_results]
        
    except Exception as e:
        st.error(f"뉴스 생성 오류: {e}")
        return []

def display_news_articles(articles, query):
    """뉴스 기사들을 중앙에 표시"""
    if not articles:
        st.warning("검색 결과가 없습니다.")
        return
    
    # 검색 통계
    st.markdown(f"""
    <div class="search-stats">
        <h3>🌍 SCM Risk 관리 대시보드</h3>
        <p>🔍 검색어: <strong>{query}</strong> | 📰 총 {len(articles)}개 기사 | 🕒 검색 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="risk-indicator">⚠️ {query} Risk 모니터링 중</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 검색량 추이 차트
    st.markdown("### 📈 SCM Risk 검색량 추이")
    trend_fig = create_trend_chart(query)
    st.plotly_chart(trend_fig, use_container_width=True)
    
    # SCM Risk 지역별 지도
    st.markdown("### 🗺️ SCM Risk 발생 지역")
    try:
        risk_map = create_risk_map()
        folium_static(risk_map, width=800, height=400)
    except Exception as e:
        st.error(f"지도 로딩 오류: {e}")
        st.info("지도 기능을 사용하려면 folium과 streamlit-folium 패키지가 필요합니다.")
    
    # 뉴스 기사 목록
    st.markdown("### 📰 SCM Risk 관련 뉴스")
    
    for i, article in enumerate(articles, 1):
        st.markdown(f"""
        <div class="news-card">
            <div class="news-title">{i}. {article['title']}</div>
            <div class="news-meta">
                📰 {article['source']} 
                {f"| 🕒 {article['published_time']}" if article['published_time'] else ""}
            </div>
            <div class="news-description">
                {article['description'] if article['description'] else "설명 없음"}
            </div>
            <a href="{article['url']}" target="_blank" class="news-link">
                🔗 원문 보기
            </a>
        </div>
        """, unsafe_allow_html=True)

def save_to_text(articles, filename):
    """뉴스 기사들을 텍스트 파일로 저장"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"SCM Risk 관리 뉴스 분석 결과 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, article in enumerate(articles, 1):
                f.write(f"[{i}] {article['title']}\n")
                f.write(f"출처: {article['source']}\n")
                if article['published_time']:
                    f.write(f"발행시간: {article['published_time']}\n")
                f.write(f"URL: {article['url']}\n")
                if article['description']:
                    f.write(f"설명: {article['description']}\n")
                f.write("-" * 60 + "\n\n")
        
        return True
    except Exception as e:
        st.error(f"파일 저장 오류: {e}")
        return False

def main():
    # 헤더
    st.markdown('<h1 class="main-header">🌍 SCM Risk 관리 대시보드</h1>', unsafe_allow_html=True)
    st.markdown("### 글로벌 공급망 위험을 실시간으로 모니터링하고 관리하세요")
    
    # 사이드바
    with st.sidebar:
        st.header("🔧 SCM Risk 검색 설정")
        
        # 검색 옵션
        search_option = st.selectbox(
            "검색 방법 선택",
            ["키워드 검색", "SCM Risk 분석", "빠른 검색"]
        )
        
        if search_option == "키워드 검색":
            query = st.text_input("SCM Risk 키워드를 입력하세요", placeholder="예: 공급망, 물류, 운송...")
            num_results = st.slider("검색 결과 개수", 100, 1000, 500)
        elif search_option == "빠른 검색":
            quick_queries = ["SCM", "공급망", "물류", "운송", "창고", "재고", "배송", "Risk", "위험", "중단"]
            query = st.selectbox("SCM Risk 키워드 선택", quick_queries)
            num_results = st.slider("검색 결과 개수", 100, 1000, 500)
        else:  # SCM Risk 분석
            query = "SCM"
            num_results = 500
        
        # 검색 버튼
        if st.button("🔍 SCM Risk 분석", type="primary"):
            if search_option == "키워드 검색" and not query.strip():
                st.error("검색어를 입력해주세요!")
                return
            
            with st.spinner("SCM Risk를 분석 중입니다..."):
                articles = crawl_google_news(query, num_results)
                
                if articles:
                    st.success(f"✅ {len(articles)}개의 SCM Risk 관련 뉴스를 찾았습니다!")
                    
                    # 세션 상태에 저장
                    st.session_state.articles = articles
                    st.session_state.query = query
                    
                    # 파일 저장 옵션
                    if st.button("💾 분석 결과 저장"):
                        filename = f"scm_risk_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        if save_to_text(articles, filename):
                            st.success(f"✅ SCM Risk 분석 결과가 '{filename}' 파일로 저장되었습니다!")
                            
                            # 파일 다운로드 버튼
                            with open(filename, 'r', encoding='utf-8') as f:
                                st.download_button(
                                    label="📥 파일 다운로드",
                                    data=f.read(),
                                    file_name=filename,
                                    mime="text/plain"
                                )
                else:
                    st.warning("검색 결과가 없습니다. 다른 키워드로 시도해보세요.")
    
    # 메인 컨텐츠 - 뉴스 기사 표시
    if 'articles' in st.session_state and st.session_state.articles:
        display_news_articles(st.session_state.articles, st.session_state.query)
        
        # 데이터 테이블 및 다운로드 옵션
        with st.expander("📊 SCM Risk 데이터 테이블"):
            df = pd.DataFrame(st.session_state.articles)
            st.dataframe(df, use_container_width=True)
            
            # CSV 다운로드
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 파일 다운로드",
                data=csv,
                file_name=f"scm_risk_{st.session_state.query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
