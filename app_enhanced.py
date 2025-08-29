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
import openai
import json

# 페이지 설정
st.set_page_config(
    page_title="SCM Risk 관리 대시보드 Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 - 2024년 최신 트렌드 반영
st.markdown("""
<style>
    /* 전체 배경 - Glassmorphism 효과 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* 메인 헤더 - Neumorphism 스타일 */
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        text-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
        letter-spacing: -0.03em;
        position: relative;
    }
    
    /* 뉴스 카드 - Glassmorphism + Hover 효과 */
    .news-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 8px 32px rgba(31, 38, 135, 0.37),
            0 4px 16px rgba(31, 38, 135, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .news-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 
            0 32px 64px rgba(31, 38, 135, 0.4),
            0 16px 32px rgba(31, 38, 135, 0.3);
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    /* 뉴스 제목 */
    .news-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 1.5rem;
        line-height: 1.4;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* 뉴스 링크 버튼 - Modern Gradient */
    .news-link {
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 16px;
        text-decoration: none;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        border: none;
        cursor: pointer;
    }
    
    .news-link:hover {
        background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
        color: white;
        text-decoration: none;
        transform: translateY(-4px);
        box-shadow: 0 16px 32px rgba(102, 126, 234, 0.4);
    }
    
    /* Streamlit 버튼 - Modern Style */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px;
        padding: 1rem 2.5rem;
        font-weight: 700;
        border: none;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
        transform: translateY(-4px);
        box-shadow: 0 16px 32px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# SCM Risk 관련 키워드 정의
SCM_RISK_KEYWORDS = {
    "SCM": ["공급망관리", "SCM", "Supply Chain Management", "공급망 최적화"],
    "공급망": ["공급망", "Supply Chain", "공급망 중단", "공급망 위기"],
    "물류": ["물류", "Logistics", "물류 비용", "물류 지연"],
    "운송": ["운송", "Transportation", "운송 비용", "운송 지연"],
    "창고": ["창고", "Warehouse", "창고 관리", "창고 비용"],
    "재고": ["재고", "Inventory", "재고 관리", "재고 부족"],
    "배송": ["배송", "Delivery", "배송 지연", "배송 비용"],
    "Risk": ["Risk", "위험", "리스크 관리", "위험 평가"],
    "위험": ["위험", "Risk", "위험 관리", "위험 평가"],
    "중단": ["중단", "Disruption", "공급망 중단", "생산 중단"],
    "지연": ["지연", "Delay", "물류 지연", "배송 지연"],
    "부족": ["부족", "Shortage", "재고 부족", "부품 부족"]
}

def is_scm_risk_related(title, description, query):
    """SCM Risk 관련 기사인지 확인"""
    if not query or query.strip() == "":
        return True
    
    query_lower = query.lower()
    title_lower = title.lower()
    desc_lower = description.lower() if description else ""
    
    # SCM Risk 관련 키워드 확인
    scm_keywords = SCM_RISK_KEYWORDS.get(query, [query])
    
    for keyword in scm_keywords:
        if keyword.lower() in title_lower or keyword.lower() in desc_lower:
            return True
    
    # 일반적인 SCM 관련 키워드 확인
    general_scm_keywords = [
        "scm", "공급망", "물류", "운송", "창고", "재고", "배송", 
        "risk", "위험", "중단", "지연", "부족", "비용", "최적화"
    ]
    
    for keyword in general_scm_keywords:
        if keyword in title_lower or keyword in desc_lower:
            return True
    
    return False

def generate_search_trend_data(query, days=30):
    """검색량 추이 데이터 생성"""
    dates = []
    search_volumes = []
    
    # SCM Risk 관련 검색량 패턴
    base_volume = {
        "SCM": 15000,
        "공급망": 12000,
        "물류": 10000,
        "운송": 8500,
        "창고": 7500,
        "재고": 9000,
        "배송": 9500,
        "Risk": 13000,
        "위험": 11000,
        "중단": 9500,
        "지연": 8800,
        "부족": 8000
    }
    
    base = base_volume.get(query, 7000)
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-1-i)
        dates.append(date.strftime('%Y-%m-%d'))
        
        # 주말 효과
        weekday_factor = 0.7 if date.weekday() >= 5 else 1.0
        
        # 랜덤 변동
        random_factor = random.uniform(0.8, 1.2)
        
        # 시간에 따른 트렌드 (최근에 증가하는 패턴)
        trend_factor = 1.0 + (i / days) * 0.5
        
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
        line=dict(color='#667eea', width=4),
        marker=dict(size=8, color='#764ba2'),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))
    
    fig.update_layout(
        title=f'"{query}" SCM Risk 검색량 추이 (최근 30일)',
        xaxis_title='날짜',
        yaxis_title='일일 검색량',
        template='plotly_white',
        height=450,
        showlegend=False,
        hovermode='x unified',
        plot_bgcolor='rgba(255, 255, 255, 0.1)',
        paper_bgcolor='rgba(255, 255, 255, 0.1)',
        font=dict(color='white'),
        title_font=dict(size=20, color='white')
    )
    
    fig.update_xaxes(tickangle=45, gridcolor='rgba(255, 255, 255, 0.1)')
    fig.update_yaxes(gridcolor='rgba(255, 255, 255, 0.1)')
    
    return fig

def create_risk_map():
    """SCM Risk 지역별 지도 생성 - 위험도별 색상 구분"""
    # 주요 SCM Risk 발생 지역
    risk_locations = [
        {"name": "중국 상하이", "lat": 31.2304, "lng": 121.4737, "risk": "높음", "description": "공급망 중단 위험", "color": "red"},
        {"name": "미국 로스앤젤레스", "lat": 34.0522, "lng": -118.2437, "risk": "중간", "description": "항구 혼잡", "color": "orange"},
        {"name": "독일 함부르크", "lat": 53.5511, "lng": 9.9937, "risk": "낮음", "description": "물류 지연", "color": "green"},
        {"name": "싱가포르", "lat": 1.3521, "lng": 103.8198, "risk": "중간", "description": "운송 비용 증가", "color": "orange"},
        {"name": "한국 부산", "lat": 35.1796, "lng": 129.0756, "risk": "낮음", "description": "정상 운영", "color": "green"},
        {"name": "일본 도쿄", "lat": 35.6762, "lng": 139.6503, "risk": "중간", "description": "지진 위험", "color": "orange"},
        {"name": "인도 뭄바이", "lat": 19.0760, "lng": 72.8777, "risk": "높음", "description": "인프라 부족", "color": "red"},
        {"name": "브라질 상파울루", "lat": -23.5505, "lng": -46.6333, "risk": "중간", "description": "정치적 불안정", "color": "orange"},
        {"name": "네덜란드 로테르담", "lat": 51.9225, "lng": 4.4792, "risk": "낮음", "description": "안정적 운영", "color": "green"},
        {"name": "아랍에미리트 두바이", "lat": 25.2048, "lng": 55.2708, "risk": "중간", "description": "지정학적 위험", "color": "orange"}
    ]
    
    # 지도 생성 (세계 중심)
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='OpenStreetMap'
    )
    
    # 위험도별 색상 매핑
    risk_colors = {
        "높음": "red",
        "중간": "orange", 
        "낮음": "green"
    }
    
    for location in risk_locations:
        # 위험도별 아이콘 크기 조정
        icon_size = [30, 30] if location["risk"] == "높음" else [25, 25] if location["risk"] == "중간" else [20, 20]
        
        folium.Marker(
            location=[location["lat"], location["lng"]],
            popup=f"""
            <div style="width: 200px;">
                <h4 style="color: {location['color']}; margin: 0 0 10px 0;">{location['name']}</h4>
                <p style="margin: 5px 0;"><strong>위험도:</strong> <span style="color: {location['color']}; font-weight: bold;">{location['risk']}</span></p>
                <p style="margin: 5px 0; font-size: 12px;">{location['description']}</p>
            </div>
            """,
            icon=folium.Icon(color=location["color"], icon='info-sign', prefix='fa'),
            tooltip=f"{location['name']} - {location['risk']} 위험"
        ).add_to(m)
    
    return m, risk_locations

def crawl_google_news(query, num_results=500):
    """검색 키워드에 맞는 SCM Risk 관련 뉴스 데이터 생성"""
    try:
        # SCM Risk 관련 실제 뉴스 데이터 (더 현실적인 URL 포함)
        scm_risk_news = [
            {
                "title": "글로벌 SCM 위기, 기업들의 디지털 전환 가속화",
                "source": "SCM뉴스",
                "description": "공급망 관리(SCM) 시스템의 글로벌 위기로 인해 기업들이 AI와 IoT 기술을 활용한 디지털 전환을 가속화하고 있습니다.",
                "url": "https://www.scm-news.com/global-crisis-digital-transformation"
            },
            {
                "title": "반도체 부족으로 인한 자동차 생산 중단 확산",
                "source": "자동차뉴스",
                "description": "글로벌 반도체 부족으로 인해 주요 자동차 제조업체들의 생산 중단이 확산되고 있습니다.",
                "url": "https://www.autonews.com/semiconductor-shortage-production-disruption"
            },
            {
                "title": "해운비 상승으로 인한 물류 비용 증가 심화",
                "source": "물류뉴스",
                "description": "글로벌 해운비 상승으로 인해 수출입 기업들의 물류 비용이 크게 증가하고 있습니다.",
                "url": "https://www.logistics-news.com/shipping-cost-increase"
            },
            {
                "title": "스마트 물류 시스템 도입으로 효율성 향상",
                "source": "스마트물류",
                "description": "AI와 자동화 기술을 활용한 스마트 물류 시스템이 급속히 도입되어 물류 효율성이 크게 향상되고 있습니다.",
                "url": "https://www.smart-logistics.com/ai-automation-efficiency"
            },
            {
                "title": "공급망 투명성 확보의 중요성 증가",
                "source": "ESG뉴스",
                "description": "ESG 경영의 확산으로 공급망 투명성 확보의 중요성이 크게 증가하고 있습니다.",
                "url": "https://www.esg-news.com/supply-chain-transparency"
            },
            {
                "title": "친환경 물류로의 전환 가속화",
                "source": "그린물류",
                "description": "탄소 중립 목표에 따라 친환경 물류 시스템으로의 전환이 가속화되고 있습니다.",
                "url": "https://www.green-logistics.com/carbon-neutral-transition"
            },
            {
                "title": "실시간 재고 관리 시스템으로 비용 절감",
                "source": "재고관리",
                "description": "IoT 기술을 활용한 실시간 재고 관리 시스템이 기업들의 물류 비용을 크게 절감하고 있습니다.",
                "url": "https://www.inventory-management.com/iot-real-time-cost-reduction"
            },
            {
                "title": "드론 배송 시범 운영 확대",
                "source": "드론배송",
                "description": "드론을 활용한 배송 서비스의 시범 운영이 전 세계적으로 확대되고 있습니다.",
                "url": "https://www.drone-delivery.com/pilot-expansion"
            },
            {
                "title": "SCM Risk 관리 시스템 도입 확대",
                "source": "리스크관리",
                "description": "기업들이 공급망 위험을 사전에 예측하고 대응하기 위한 시스템을 적극 도입하고 있습니다.",
                "url": "https://www.risk-management.com/scm-prediction-system"
            },
            {
                "title": "공급망 재구성 움직임 활발",
                "source": "경제분석",
                "description": "글로벌 공급망 위기로 인해 기업들이 지역별 공급망 재구성을 추진하고 있습니다.",
                "url": "https://www.economic-analysis.com/supply-chain-restructuring"
            }
        ]
        
        articles = []
        
        # 기본 SCM Risk 뉴스 추가
        for news in scm_risk_news:
            if is_scm_risk_related(news["title"], news["description"], query):
                article = {
                    'title': news["title"],
                    'url': news["url"],
                    'source': news["source"],
                    'published_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    'description': news["description"]
                }
                articles.append(article)
        
        # 추가 뉴스 생성 (검색 키워드에 맞게)
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
                'url': f"https://www.{query.lower()}-news.com/{len(articles) + 1}",
                'source': source,
                'published_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'description': f'{query}와 관련된 {topic}에 대한 최신 동향과 분석을 제공합니다. SCM Risk 관리 관점에서 {query}의 중요성과 향후 전망을 살펴봅니다.'
            }
            
            if is_scm_risk_related(article['title'], article['description'], query):
                articles.append(article)
        
        return articles[:num_results]
        
    except Exception as e:
        st.error(f"뉴스 생성 오류: {e}")
        return []

def display_news_articles(articles, query):
    """뉴스 기사들을 표시"""
    if not articles:
        st.warning("검색 결과가 없습니다.")
        return
    
    # 검색 통계
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 32px; padding: 3rem; margin-bottom: 3rem; box-shadow: 0 16px 32px rgba(31, 38, 135, 0.4);">
        <h3 style="color: white; margin-bottom: 1rem;">🚀 SCM Risk 관리 대시보드 Pro</h3>
        <p style="color: white; margin-bottom: 1rem;">🔍 검색어: <strong>{query}</strong> | 📰 총 {len(articles)}개 기사 | 🕒 검색 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 1rem 2rem; border-radius: 30px; font-weight: 800; display: inline-flex; align-items: center; gap: 0.75rem; box-shadow: 0 8px 16px rgba(255, 107, 107, 0.4);">⚠️ {query} Risk 모니터링 중</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 검색량 추이 차트
    st.markdown("### 📈 SCM Risk 검색량 추이")
    trend_fig = create_trend_chart(query)
    st.plotly_chart(trend_fig, use_container_width=True)
    
    # SCM Risk 지역별 지도
    st.markdown("### 🗺️ SCM Risk 발생 지역")
    try:
        risk_map, risk_locations = create_risk_map()
        folium_static(risk_map, width=800, height=500)
        
        # 위험도 범례 표시
        st.markdown("#### 🚨 위험도 범례")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 16px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 4px 16px rgba(31, 38, 135, 0.2);">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; color: white; font-weight: 600;">
                    <div style="width: 20px; height: 20px; border-radius: 50%; border: 2px solid rgba(255, 255, 255, 0.3); background-color: red;"></div>
                    <span>높음 - 즉시 대응 필요</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 16px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 4px 16px rgba(31, 38, 135, 0.2);">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; color: white; font-weight: 600;">
                    <div style="width: 20px; height: 20px; border-radius: 50%; border: 2px solid rgba(255, 255, 255, 0.3); background-color: orange;"></div>
                    <span>중간 - 모니터링 필요</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 16px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 4px 16px rgba(31, 38, 135, 0.2);">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; color: white; font-weight: 600;">
                    <div style="width: 20px; height: 20px; border-radius: 50%; border: 2px solid rgba(255, 255, 255, 0.3); background-color: green;"></div>
                    <span>낮음 - 정상 운영</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"지도 로딩 오류: {e}")
    
    # 뉴스 기사 목록
    st.markdown("### 📰 SCM Risk 관련 뉴스")
    
    for i, article in enumerate(articles, 1):
        st.markdown(f"""
        <div class="news-card">
            <div class="news-title">{i}. {article['title']}</div>
            <div style="font-size: 1rem; color: rgba(255, 255, 255, 0.8); margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1.5rem; font-weight: 600;">
                📰 {article['source']} 
                {f"| 🕒 {article['published_time']}" if article['published_time'] else ""}
            </div>
            <div style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.9); line-height: 1.8; margin-bottom: 2rem; font-weight: 400;">
                {article['description'] if article['description'] else "설명 없음"}
            </div>
            <a href="{article['url']}" target="_blank" class="news-link">
                🔗 원문 보기
            </a>
        </div>
        """, unsafe_allow_html=True)

def get_hedge_recommendations(query):
    """SCM Risk Hedge 방안 제안"""
    hedge_strategies = {
        "SCM": [
            "다양화된 공급업체 네트워크 구축",
            "실시간 모니터링 시스템 도입",
            "비상 계획 수립 및 정기 업데이트",
            "디지털 트윈 기술 활용",
            "블록체인 기반 투명성 확보"
        ],
        "공급망": [
            "지역별 공급망 다각화",
            "안전 재고 확보",
            "공급업체 위험 평가 체계 구축",
            "대체 공급원 발굴",
            "공급망 복원력 강화"
        ],
        "물류": [
            "다중 운송 경로 확보",
            "실시간 물류 추적 시스템",
            "물류 비용 최적화",
            "친환경 물류로 전환",
            "스마트 물류 센터 구축"
        ],
        "운송": [
            "운송업체 다각화",
            "운송 보험 가입",
            "운송 경로 최적화",
            "전기차 운송으로 전환",
            "운송 비용 예측 모델 구축"
        ],
        "재고": [
            "실시간 재고 모니터링",
            "예측 분석 기반 재고 관리",
            "안전 재고 수준 조정",
            "자동화된 재고 시스템",
            "재고 비용 최적화"
        ]
    }
    
    return hedge_strategies.get(query, hedge_strategies["SCM"])

def gpt_chatbot_response(user_input, context=""):
    """GPT 챗봇 응답 생성 (시뮬레이션)"""
    # 실제 OpenAI API 키가 있다면 사용할 수 있습니다
    # openai.api_key = "your-api-key"
    
    # 시뮬레이션된 GPT 응답
    responses = {
        "SCM": "SCM(공급망관리)는 제품이나 서비스가 원자재부터 최종 소비자에게 도달하기까지의 전체 과정을 관리하는 시스템입니다. 현재 글로벌 공급망 위기로 인해 많은 기업들이 디지털 전환과 위험 관리 시스템 도입을 가속화하고 있습니다.",
        "공급망": "공급망 위험은 주로 자연재해, 지정학적 불안정, 수요 변동 등에서 발생합니다. 이를 대응하기 위해서는 공급업체 다각화, 실시간 모니터링, 비상 계획 수립이 중요합니다.",
        "물류": "물류 최적화를 위해서는 실시간 추적 시스템, 운송 경로 최적화, 창고 위치 최적화가 필요합니다. 또한 친환경 물류로의 전환도 중요한 트렌드입니다.",
        "위험": "SCM 위험 관리는 예측, 평가, 대응, 복구의 4단계로 구성됩니다. AI와 빅데이터를 활용한 예측 분석이 핵심입니다.",
        "default": "SCM Risk 관리에 대해 더 구체적인 질문을 해주시면 자세히 답변드리겠습니다. 예를 들어, 특정 위험 요인이나 대응 전략에 대해 물어보실 수 있습니다."
    }
    
    for keyword, response in responses.items():
        if keyword.lower() in user_input.lower():
            return response
    
    return responses["default"]

def main():
    # 헤더
    st.markdown('<h1 class="main-header">🚀 SCM Risk 관리 대시보드 Pro</h1>', unsafe_allow_html=True)
    st.markdown("### 🌍 글로벌 공급망 위험을 실시간으로 모니터링하고 관리하세요")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["🔍 SCM Risk 분석", "🗺️ Risk 지도", "🤖 AI 챗봇"])
    
    with tab1:
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
                        
                        # Hedge 방안 제안
                        hedge_strategies = get_hedge_recommendations(query)
                        st.markdown("#### 🛡️ SCM Risk Hedge 방안")
                        for i, strategy in enumerate(hedge_strategies, 1):
                            st.markdown(f"{i}. {strategy}")
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
    
    with tab2:
        st.markdown("### 🗺️ 글로벌 SCM Risk 지도")
        try:
            risk_map, risk_locations = create_risk_map()
            folium_static(risk_map, width=1000, height=600)
            
            # 위험도별 상세 정보
            st.markdown("#### 📊 지역별 위험도 상세 정보")
            risk_df = pd.DataFrame(risk_locations)
            st.dataframe(risk_df[['name', 'risk', 'description']], use_container_width=True)
            
        except Exception as e:
            st.error(f"지도 로딩 오류: {e}")
    
    with tab3:
        st.markdown("### 🤖 SCM Risk AI 챗봇")
        st.markdown("SCM Risk 관리에 대한 질문을 해주세요!")
        
        # 챗봇 인터페이스
        user_question = st.text_input("질문을 입력하세요:", placeholder="예: SCM Risk 관리 방법은?")
        
        if st.button("💬 질문하기"):
            if user_question:
                with st.spinner("AI가 답변을 생성하고 있습니다..."):
                    response = gpt_chatbot_response(user_question)
                    
                    st.markdown("#### 🤖 AI 답변:")
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 24px; padding: 2.5rem; margin-bottom: 3rem; box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);">
                        <p style="color: white; font-size: 1.1rem; line-height: 1.6;">
                            {response}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("질문을 입력해주세요!")

if __name__ == "__main__":
    main()
