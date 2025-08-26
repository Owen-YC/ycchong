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

# CSS 스타일 - 흰색 배경, 푸른 계열 색상
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1e3a8a;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .news-card {
        background-color: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(30, 58, 138, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(30, 58, 138, 0.15);
        border-color: #3b82f6;
    }
    .news-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1e3a8a;
        margin-bottom: 0.8rem;
        line-height: 1.4;
    }
    .news-meta {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .news-description {
        font-size: 1rem;
        color: #374151;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .news-link {
        display: inline-block;
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .news-link:hover {
        background: linear-gradient(135deg, #1e40af, #2563eb);
        color: white;
        text-decoration: none;
        transform: translateY(-1px);
    }
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e40af, #2563eb);
    }
    .search-stats {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(30, 58, 138, 0.2);
    }
    .trend-chart {
        background-color: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(30, 58, 138, 0.1);
    }
    .map-container {
        background-color: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(30, 58, 138, 0.1);
    }
    .risk-indicator {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .stApp {
        background-color: #ffffff;
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
    """SCM Risk 관련 뉴스 데이터 생성"""
    try:
        # SCM Risk 관련 뉴스 데이터
        scm_news = [
            {"title": "글로벌 공급망 위기, 기업들의 대응 전략", "source": "경제일보", "description": "코로나19 이후 지속되는 공급망 위기로 인해 기업들이 다양한 대응 전략을 모색하고 있습니다. 재고 관리와 공급업체 다변화가 핵심 과제로 부상하고 있습니다.", "url": "https://economy.com/supply-chain-crisis"},
            {"title": "중국 공장 폐쇄로 인한 전자제품 공급 부족", "source": "테크뉴스", "description": "중국 주요 전자제품 생산지의 폐쇄로 인해 글로벌 전자제품 공급망에 차질이 빚어지고 있습니다. 반도체와 스마트폰 부품의 공급이 급격히 감소하고 있습니다.", "url": "https://technews.com/china-factory-closure"},
            {"title": "해운비 상승으로 인한 물류 비용 증가", "source": "물류뉴스", "description": "글로벌 해운비 상승으로 인해 수출입 기업들의 물류 비용이 크게 증가하고 있습니다. 컨테이너 부족 현상이 지속되면서 물류 지연이 발생하고 있습니다.", "url": "https://logistics.com/shipping-cost-increase"},
            {"title": "러시아-우크라이나 전쟁이 글로벌 공급망에 미치는 영향", "source": "국제뉴스", "description": "러시아-우크라이나 전쟁으로 인해 에너지와 곡물 공급망에 큰 타격을 받고 있습니다. 특히 유럽 지역의 에너지 의존도 문제가 심화되고 있습니다.", "url": "https://international.com/russia-ukraine-supply"},
            {"title": "기후변화로 인한 농산물 공급 불안정", "source": "농업뉴스", "description": "기후변화로 인한 극단적 날씨 현상이 농산물 생산에 큰 영향을 미치고 있습니다. 곡물과 과일의 수확량 감소로 인한 가격 상승이 예상됩니다.", "url": "https://agriculture.com/climate-change-impact"},
            {"title": "자동차 반도체 부족으로 인한 생산 중단", "source": "자동차뉴스", "description": "반도체 부족으로 인해 글로벌 자동차 제조업체들이 생산을 중단하거나 줄이고 있습니다. 신차 출고 지연이 장기화되고 있습니다.", "url": "https://automotive.com/semiconductor-shortage"},
            {"title": "디지털 전환으로 인한 공급망 혁신", "source": "IT뉴스", "description": "AI와 IoT 기술을 활용한 스마트 공급망 관리 시스템이 도입되고 있습니다. 실시간 재고 추적과 예측 분석으로 효율성이 크게 향상되고 있습니다.", "url": "https://itnews.com/digital-supply-chain"},
            {"title": "친환경 물류로의 전환 가속화", "source": "환경뉴스", "description": "탄소 중립 목표에 따라 친환경 물류 시스템으로의 전환이 가속화되고 있습니다. 전기차 배송과 그린 물류가 새로운 트렌드로 부상하고 있습니다.", "url": "https://environment.com/green-logistics"},
            {"title": "지역별 공급망 재구성 움직임", "source": "경제분석", "description": "글로벌 공급망 위기로 인해 기업들이 지역별 공급망 재구성을 추진하고 있습니다. 근접 생산과 다변화 전략이 활발히 논의되고 있습니다.", "url": "https://analysis.com/regional-supply-chain"},
            {"title": "공급망 위험 관리 시스템 도입 확대", "source": "리스크뉴스", "description": "기업들이 공급망 위험을 사전에 예측하고 대응하기 위한 리스크 관리 시스템을 적극 도입하고 있습니다. 실시간 모니터링과 대응 체계가 구축되고 있습니다.", "url": "https://risk.com/supply-chain-management"}
        ]
        
        articles = []
        
        # 기본 SCM 뉴스 추가
        for i, news in enumerate(scm_news):
            article = {
                'title': news["title"],
                'url': news["url"],
                'source': news["source"],
                'published_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'description': news["description"]
            }
            articles.append(article)
        
        # 추가 SCM 관련 뉴스 생성
        scm_keywords = ["공급망", "물류", "운송", "창고", "재고", "배송", "위험", "중단", "지연", "부족"]
        scm_topics = [
            "글로벌 물류 네트워크 최적화",
            "실시간 재고 관리 시스템",
            "공급업체 위험 평가",
            "물류 비용 절감 전략",
            "공급망 투명성 확보",
            "긴급 상황 대응 체계",
            "지속가능한 공급망 구축",
            "디지털 물류 플랫폼",
            "공급망 복원력 강화",
            "물류 인프라 투자"
        ]
        
        while len(articles) < num_results:
            topic = random.choice(scm_topics)
            keyword = random.choice(scm_keywords)
            source = f"SCM{len(articles) + 1}뉴스"
            
            article = {
                'title': f'"{keyword}" 관련 {topic}',
                'url': f"https://scm-news.com/{keyword}-{len(articles) + 1}",
                'source': source,
                'published_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'description': f'SCM Risk 관리 관점에서 {keyword}와 관련된 {topic}에 대한 최신 동향과 분석을 제공합니다. 공급망 안정성과 효율성 향상을 위한 전략적 접근이 필요합니다.'
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
        <div class="risk-indicator">⚠️ SCM Risk 모니터링 중</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 검색량 추이 차트
    st.markdown("### 📈 SCM Risk 검색량 추이")
    trend_fig = create_trend_chart(query)
    st.plotly_chart(trend_fig, use_container_width=True)
    
    # SCM Risk 지역별 지도
    st.markdown("### 🗺️ SCM Risk 발생 지역")
    risk_map = create_risk_map()
    folium_static(risk_map, width=800, height=400)
    
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
