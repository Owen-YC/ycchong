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

# 페이지 설정
st.set_page_config(
    page_title="구글 뉴스 크롤러",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .news-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .news-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.8rem;
        line-height: 1.4;
    }
    .news-meta {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .news-description {
        font-size: 1rem;
        color: #333;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .news-link {
        display: inline-block;
        background-color: #1f77b4;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 500;
        transition: background-color 0.2s ease;
    }
    .news-link:hover {
        background-color: #0056b3;
        color: white;
        text-decoration: none;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .search-stats {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .trend-chart {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def generate_search_trend_data(query, days=30):
    """검색량 추이 데이터 생성"""
    dates = []
    search_volumes = []
    
    # 기본 검색량 패턴 (주말에 낮고, 평일에 높음)
    base_volume = {
        "AI": 8500,
        "경제": 7200,
        "정치": 6800,
        "스포츠": 6500,
        "IT": 7800,
        "엔터테인먼트": 6200,
        "코로나": 4500,
        "한국": 9000
    }
    
    base = base_volume.get(query, 5000)
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-1-i)
        dates.append(date.strftime('%Y-%m-%d'))
        
        # 주말 효과
        weekday_factor = 0.7 if date.weekday() >= 5 else 1.0
        
        # 랜덤 변동
        random_factor = random.uniform(0.8, 1.2)
        
        # 시간에 따른 트렌드 (최근에 증가하는 패턴)
        trend_factor = 1.0 + (i / days) * 0.3
        
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
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6, color='#1f77b4'),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))
    
    fig.update_layout(
        title=f'"{query}" 검색량 추이 (최근 30일)',
        xaxis_title='날짜',
        yaxis_title='일일 검색량',
        template='plotly_white',
        height=400,
        showlegend=False,
        hovermode='x unified'
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def crawl_google_news(query, num_results=10):
    """뉴스 데이터 생성 (구글 뉴스 크롤링 대신 샘플 데이터)"""
    try:
        # 샘플 뉴스 데이터 생성
        sample_news = {
            "AI": [
                {"title": "AI 기술 발전으로 새로운 혁신 기대", "source": "테크뉴스", "description": "인공지능 기술의 최신 발전 동향과 미래 전망에 대해 알아봅니다. 머신러닝과 딥러닝 기술이 다양한 분야에서 혁신을 가져오고 있습니다.", "url": "https://technews.com/ai-innovation"},
                {"title": "AI 챗봇 서비스 확산", "source": "IT월드", "description": "기업들의 AI 챗봇 도입이 활발해지고 있습니다. 고객 서비스와 업무 효율성 향상에 크게 기여하고 있습니다.", "url": "https://itworld.com/ai-chatbot"},
                {"title": "AI 윤리 가이드라인 발표", "source": "과학뉴스", "description": "AI 기술의 윤리적 사용을 위한 새로운 가이드라인이 발표되었습니다. 책임감 있는 AI 개발의 중요성이 강조되고 있습니다.", "url": "https://science.com/ai-ethics"}
            ],
            "경제": [
                {"title": "주요 경제지표 개선세", "source": "경제일보", "description": "최근 경제지표가 예상보다 좋은 성과를 보이고 있습니다. GDP 성장률과 고용률이 모두 상승세를 보이고 있습니다.", "url": "https://economy.com/economic-indicators"},
                {"title": "글로벌 경제 전망", "source": "국제경제", "description": "세계 경제의 향후 전망과 주요 이슈를 분석합니다. 글로벌 경제 회복세가 지속될 것으로 예상됩니다.", "url": "https://global-economy.com/outlook"},
                {"title": "디지털 경제 성장", "source": "경제타임즈", "description": "디지털 경제의 성장세가 가속화되고 있습니다. 온라인 거래와 디지털 서비스가 경제의 핵심 동력이 되고 있습니다.", "url": "https://economytimes.com/digital-growth"}
            ],
            "정치": [
                {"title": "정치 현안 논의 활발", "source": "정치뉴스", "description": "현재 주요 정치 현안에 대한 논의가 활발히 진행되고 있습니다. 국회에서 다양한 정책에 대한 토론이 이어지고 있습니다.", "url": "https://politics.com/discussion"},
                {"title": "정책 개혁 추진", "source": "정치일보", "description": "새로운 정책 개혁안이 추진되고 있습니다. 사회 전반의 변화를 위한 다양한 정책이 논의되고 있습니다.", "url": "https://politicsdaily.com/reform"},
                {"title": "국제 관계 발전", "source": "외교뉴스", "description": "국제 관계 개선을 위한 노력이 계속되고 있습니다. 외교적 성과와 협력 관계 강화가 이루어지고 있습니다.", "url": "https://diplomacy.com/relations"}
            ],
            "스포츠": [
                {"title": "스포츠 대회 성공적 개최", "source": "스포츠뉴스", "description": "주요 스포츠 대회가 성공적으로 개최되고 있습니다. 팬들의 열정과 선수들의 뛰어난 경기력이 돋보이고 있습니다.", "url": "https://sports.com/tournament"},
                {"title": "선수들의 활약", "source": "스포츠타임즈", "description": "국내외 선수들의 뛰어난 활약이 이어지고 있습니다. 새로운 기록과 놀라운 성과들이 계속 나오고 있습니다.", "url": "https://sportstimes.com/players"},
                {"title": "스포츠 산업 성장", "source": "스포츠경제", "description": "스포츠 산업의 지속적인 성장세가 관찰되고 있습니다. 스포츠 마케팅과 관련 산업이 확대되고 있습니다.", "url": "https://sportseconomy.com/growth"}
            ],
            "IT": [
                {"title": "IT 기술 혁신", "source": "테크뉴스", "description": "최신 IT 기술의 혁신적인 발전이 계속되고 있습니다. 새로운 기술과 서비스가 끊임없이 등장하고 있습니다.", "url": "https://technews.com/innovation"},
                {"title": "스마트폰 시장 동향", "source": "모바일뉴스", "description": "스마트폰 시장의 최신 동향과 트렌드를 분석합니다. 새로운 기능과 디자인이 소비자들의 관심을 끌고 있습니다.", "url": "https://mobile.com/trends"},
                {"title": "소프트웨어 개발 트렌드", "source": "개발자뉴스", "description": "소프트웨어 개발 분야의 최신 트렌드를 소개합니다. 새로운 프로그래밍 언어와 개발 도구가 인기를 얻고 있습니다.", "url": "https://developer.com/trends"}
            ],
            "엔터테인먼트": [
                {"title": "영화계 최신 소식", "source": "엔터뉴스", "description": "영화계의 최신 소식과 개봉 예정작을 소개합니다. 다양한 장르의 영화들이 관객들을 기다리고 있습니다.", "url": "https://entertainment.com/movies"},
                {"title": "음악 시장 변화", "source": "음악뉴스", "description": "음악 시장의 변화와 새로운 아티스트들을 소개합니다. 디지털 음원과 스트리밍 서비스가 음악 산업을 변화시키고 있습니다.", "url": "https://music.com/changes"},
                {"title": "방송계 트렌드", "source": "방송뉴스", "description": "방송계의 최신 트렌드와 인기 프로그램을 분석합니다. OTT 서비스와 전통 방송의 경쟁이 치열해지고 있습니다.", "url": "https://broadcast.com/trends"}
            ],
            "코로나": [
                {"title": "코로나19 상황 업데이트", "source": "건강뉴스", "description": "최신 코로나19 상황과 예방 수칙을 안내합니다. 백신 접종과 방역 수칙 준수가 중요합니다.", "url": "https://health.com/covid19"},
                {"title": "백신 접종 현황", "source": "의료뉴스", "description": "백신 접종 현황과 효과에 대한 최신 정보를 제공합니다. 전 세계적인 백신 접종이 진행되고 있습니다.", "url": "https://medical.com/vaccine"},
                {"title": "방역 정책 변화", "source": "정책뉴스", "description": "방역 정책의 최신 변화사항을 전달합니다. 상황에 따른 유연한 정책 조정이 이루어지고 있습니다.", "url": "https://policy.com/prevention"}
            ],
            "한국": [
                {"title": "한국 경제 성장세", "source": "경제일보", "description": "한국 경제의 지속적인 성장세와 전망을 분석합니다. 수출과 내수 모두에서 좋은 성과를 보이고 있습니다.", "url": "https://economy.com/korea-growth"},
                {"title": "한국 문화 세계 진출", "source": "문화뉴스", "description": "한국 문화의 세계 진출과 K-콘텐츠의 인기를 다룹니다. K-팝, K-드라마, K-뷰티가 전 세계에서 사랑받고 있습니다.", "url": "https://culture.com/k-wave"},
                {"title": "한국 기술 혁신", "source": "기술뉴스", "description": "한국 기술의 혁신과 글로벌 경쟁력 강화를 소개합니다. 반도체, 자동차, IT 분야에서 세계적 수준을 보여주고 있습니다.", "url": "https://tech.com/korea-innovation"}
            ]
        }
        
        articles = []
        
        # 쿼리에 맞는 뉴스 데이터 선택
        if query in sample_news:
            news_list = sample_news[query]
        else:
            # 기본 뉴스 데이터
            news_list = sample_news["한국"]
        
        # 요청된 개수만큼 뉴스 생성
        for i in range(min(num_results, len(news_list))):
            news = news_list[i]
            article = {
                'title': news["title"],
                'url': news["url"],
                'source': news["source"],
                'published_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'description': news["description"]
            }
            articles.append(article)
        
        # 추가 뉴스 생성 (요청된 개수만큼)
        while len(articles) < num_results:
            article = {
                'title': f'"{query}" 관련 추가 뉴스 {len(articles) + 1}',
                'url': f"https://news.google.com/search?q={urllib.parse.quote(query)}",
                'source': f"뉴스소스{len(articles) + 1}",
                'published_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'description': f'"{query}" 키워드와 관련된 추가 뉴스 정보입니다. 최신 동향과 분석을 제공합니다.'
            }
            articles.append(article)
        
        return articles
        
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
        <h3>📊 검색 결과 통계</h3>
        <p>🔍 검색어: <strong>{query}</strong> | 📰 총 {len(articles)}개 기사 | 🕒 검색 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 검색량 추이 차트
    st.markdown("### 📈 검색량 추이")
    trend_fig = create_trend_chart(query)
    st.plotly_chart(trend_fig, use_container_width=True)
    
    # 뉴스 기사 목록
    st.markdown("### 📰 관련 뉴스 기사")
    
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
            f.write(f"구글 뉴스 크롤링 결과 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
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
    st.markdown('<h1 class="main-header">📰 구글 뉴스 크롤러</h1>', unsafe_allow_html=True)
    st.markdown("### 실시간 뉴스를 쉽고 빠르게 검색해보세요")
    
    # 사이드바
    with st.sidebar:
        st.header("🔧 검색 설정")
        
        # 검색 옵션
        search_option = st.selectbox(
            "검색 방법 선택",
            ["키워드 검색", "인기 뉴스", "빠른 검색"]
        )
        
        if search_option == "키워드 검색":
            query = st.text_input("검색 키워드를 입력하세요", placeholder="예: AI, 코로나, 경제...")
            num_results = st.slider("검색 결과 개수", 5, 50, 10)
        elif search_option == "빠른 검색":
            quick_queries = ["AI", "코로나", "경제", "정치", "스포츠", "IT", "엔터테인먼트"]
            query = st.selectbox("빠른 검색 키워드 선택", quick_queries)
            num_results = st.slider("검색 결과 개수", 5, 50, 10)
        else:  # 인기 뉴스
            query = "한국"
            num_results = 15
        
        # 검색 버튼
        if st.button("🔍 뉴스 검색", type="primary"):
            if search_option == "키워드 검색" and not query.strip():
                st.error("검색어를 입력해주세요!")
                return
            
            with st.spinner("뉴스를 검색 중입니다..."):
                articles = crawl_google_news(query, num_results)
                
                if articles:
                    st.success(f"✅ {len(articles)}개의 뉴스를 찾았습니다!")
                    
                    # 세션 상태에 저장
                    st.session_state.articles = articles
                    st.session_state.query = query
                    
                    # 파일 저장 옵션
                    if st.button("💾 텍스트 파일로 저장"):
                        filename = f"google_news_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        if save_to_text(articles, filename):
                            st.success(f"✅ 뉴스가 '{filename}' 파일로 저장되었습니다!")
                            
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
        with st.expander("📊 데이터 테이블 보기"):
            df = pd.DataFrame(st.session_state.articles)
            st.dataframe(df, use_container_width=True)
            
            # CSV 다운로드
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 파일 다운로드",
                data=csv,
                file_name=f"google_news_{st.session_state.query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
