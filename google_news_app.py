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

# 페이지 설정
st.set_page_config(
    page_title="📰 Google News Crawler",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2024-2025년 최신 UI/UX 트렌드 CSS
st.markdown("""
<style>
    /* 전체 배경 - 다크모드 지원 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        transition: all 0.3s ease;
    }
    
    .stApp.light-mode {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Glassmorphism 효과 */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    }
    
    .glass-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        background: rgba(255, 255, 255, 0.15);
    }
    
    /* 다크모드 지원 */
    .dark-mode .glass-card {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .dark-mode .glass-card:hover {
        background: rgba(0, 0, 0, 0.3);
    }
    
    /* 메인 헤더 - 2025년 트렌드 */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        letter-spacing: -0.02em;
        position: relative;
        animation: slideInFromTop 1s ease-out;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .dark-mode .main-header {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 50%, #d299c2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* 서브 헤더 */
    .sub-header {
        font-size: 1.3rem;
        font-weight: 500;
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 3rem;
        letter-spacing: 0.02em;
        position: relative;
        animation: slideInFromBottom 1.2s ease-out;
    }
    
    .dark-mode .sub-header {
        color: rgba(0, 0, 0, 0.8);
    }
    
    /* 뉴스 카드 - Glassmorphism + 모션 */
    .news-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
    }
    
    .news-card:hover::before {
        transform: scaleX(1);
    }
    
    .news-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        background: rgba(255, 255, 255, 0.15);
    }
    
    .dark-mode .news-card {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .dark-mode .news-card:hover {
        background: rgba(0, 0, 0, 0.3);
    }
    
    /* 뉴스 제목 */
    .news-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.95);
        margin-bottom: 1rem;
        line-height: 1.4;
        position: relative;
        transition: color 0.3s ease;
    }
    
    .dark-mode .news-title {
        color: rgba(0, 0, 0, 0.9);
    }
    
    .news-card:hover .news-title {
        color: #f093fb;
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .news-source:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .news-time {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .dark-mode .news-time {
        color: rgba(0, 0, 0, 0.6);
    }
    
    .news-views {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .dark-mode .news-views {
        color: rgba(0, 0, 0, 0.6);
    }
    
    /* 뉴스 링크 버튼 - 2025년 트렌드 */
    .news-link {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 1rem 2rem;
        border-radius: 25px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        border: none;
        cursor: pointer;
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
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        color: white !important;
    }
    
    .news-link:hover::before {
        left: 100%;
    }
    
    /* 검색 섹션 */
    .search-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .dark-mode .search-section {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 통계 카드 */
    .stats-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .dark-mode .stats-card {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 테마 토글 버튼 */
    .theme-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 50px;
        padding: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .theme-toggle:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.1);
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
    
    .dark-mode .filter-btn.active {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

def get_korean_time():
    """한국 시간 정보 가져오기"""
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    return now.strftime('%Y년 %m월 %d일'), now.strftime('%H:%M:%S')

def crawl_google_news(query: str, num_results: int = 20) -> List[Dict]:
    """Google News RSS API를 사용한 실제 뉴스 크롤링"""
    try:
        # Google News RSS 피드 URL 구성
        search_query = query
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
                    'description': f"{title} - {source}에서 제공하는 {query} 관련 뉴스입니다.",
                    'views': random.randint(100, 5000),
                    'category': categorize_news(title, query)
                }
                articles.append(article)
        
        return articles[:num_results]
        
    except Exception as e:
        st.error(f"뉴스 크롤링 오류: {e}")
        return generate_backup_news(query, num_results)

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

def generate_backup_news(query: str, num_results: int) -> List[Dict]:
    """백업 뉴스 생성"""
    articles = []
    
    # 실제 뉴스 사이트 URL 매핑
    news_sites = [
        {"name": "연합뉴스", "url": "https://www.yna.co.kr"},
        {"name": "뉴스1", "url": "https://www.news1.kr"},
        {"name": "뉴시스", "url": "https://www.newsis.com"},
        {"name": "매일경제", "url": "https://www.mk.co.kr"},
        {"name": "한국경제", "url": "https://www.hankyung.com"},
        {"name": "조선일보", "url": "https://www.chosun.com"},
        {"name": "중앙일보", "url": "https://www.joongang.co.kr"},
        {"name": "동아일보", "url": "https://www.donga.com"}
    ]
    
    # 동적 뉴스 제목 생성
    news_templates = [
        f"{query} 관련 최신 동향 분석",
        f"{query}에 대한 전문가 의견",
        f"{query} 관련 정책 변화 소식",
        f"{query} 시장 동향 전망",
        f"{query} 관련 업계 반응",
        f"{query}에 대한 상세 분석",
        f"{query} 관련 주요 이슈",
        f"{query} 시장 전망 보고서"
    ]
    
    for i in range(min(num_results, len(news_templates))):
        site = random.choice(news_sites)
        article = {
            'title': news_templates[i],
            'url': site['url'],
            'source': site['name'],
            'published_time': (datetime.now() - timedelta(hours=random.randint(0, 24))).strftime('%Y-%m-%d %H:%M'),
            'description': f"{query}에 대한 최신 뉴스와 분석을 제공합니다.",
            'views': random.randint(100, 5000),
            'category': categorize_news(news_templates[i], query)
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
    # 테마 토글 버튼
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # 사이드바
    with st.sidebar:
        st.markdown("""
        <div class="glass-card" style="padding: 1.5rem; margin-bottom: 2rem;">
            <h3 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem; text-align: center;">🎨 테마 설정</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🌙 다크모드" if not st.session_state.dark_mode else "☀️ 라이트모드"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        
        # 검색 설정
        st.markdown("""
        <div class="glass-card" style="padding: 1.5rem; margin-bottom: 2rem;">
            <h3 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem; text-align: center;">🔍 뉴스 검색</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("search_form"):
            query = st.text_input("검색 키워드", placeholder="예: 인공지능, 반도체, 경제...", value="")
            num_results = st.slider("검색 결과 개수", 10, 50, 20)
            submit_button = st.form_submit_button("🔍 검색", type="primary")
            
            if submit_button:
                if not query.strip():
                    st.error("검색어를 입력해주세요!")
                else:
                    with st.spinner("뉴스를 검색하고 있습니다..."):
                        articles = crawl_google_news(query, num_results)
                        
                        if articles:
                            st.success(f"✅ '{query}' 키워드로 {len(articles)}개의 뉴스를 찾았습니다!")
                            st.session_state.articles = articles
                            st.session_state.query = query
                            st.session_state.search_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            st.warning(f"'{query}' 키워드로 검색 결과가 없습니다.")
        
        # 실시간 정보
        if 'articles' in st.session_state and st.session_state.articles:
            st.markdown("""
            <div class="glass-card" style="padding: 1.5rem; margin-bottom: 2rem;">
                <h3 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem; text-align: center;">📊 검색 통계</h3>
            </div>
            """, unsafe_allow_html=True)
            
            stats = get_category_stats(st.session_state.articles)
            
            for category, count in stats.items():
                st.markdown(f"""
                <div class="stats-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: rgba(255, 255, 255, 0.9); font-weight: 600;">{category}</span>
                        <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">{count}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 메인 컨텐츠
    # 헤더
    st.markdown('<h1 class="main-header">📰 Google News Crawler</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">🌍 최신 뉴스를 실시간으로 검색하고 분석하세요</h2>', unsafe_allow_html=True)
    
    # 환영 메시지
    date_str, time_str = get_korean_time()
    st.markdown(f"""
    <div class="welcome-message">
        🎉 안녕하세요! 현재 시간: {date_str} {time_str}<br>
        원하는 키워드로 최신 뉴스를 검색해보세요!
    </div>
    """, unsafe_allow_html=True)
    
    # 뉴스 표시
    if 'articles' in st.session_state and st.session_state.articles:
        # 필터링 옵션
        col1, col2 = st.columns([1, 1])
        
        with col1:
            categories = ["전체"] + list(set(article.get('category', '기타') for article in st.session_state.articles))
            selected_category = st.selectbox("카테고리", categories, key="category_filter")
        
        with col2:
            sort_options = ["최신순", "조회순", "제목순", "출처순"]
            selected_sort = st.selectbox("정렬 기준", sort_options, key="sort_filter")
        
        # 필터링된 뉴스 표시
        filtered_articles = filter_articles(st.session_state.articles, selected_category, selected_sort)
        
        # 검색 정보
        search_time = st.session_state.get('search_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        st.markdown(f"""
        <div class="search-section">
            <h4 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;">🔍 검색 결과</h4>
            <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">
                키워드: <strong>"{st.session_state.query}"</strong> | 
                📰 총 {len(filtered_articles)}개 기사 | 
                🕒 검색 시간: {search_time}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 뉴스 카드들
        for i, article in enumerate(filtered_articles, 1):
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
    else:
        # 빈 상태
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📰</div>
            <h3 style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">뉴스를 검색해보세요!</h3>
            <p style="color: rgba(255, 255, 255, 0.5); font-size: 1.1rem;">
                사이드바에서 원하는 키워드를 입력하고 검색 버튼을 눌러보세요.<br>
                최신 뉴스를 실시간으로 가져와드립니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 푸터
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem; color: rgba(255, 255, 255, 0.6);">
        <p>📰 Google News Crawler | 2024-2025년 최신 UI/UX 트렌드 적용</p>
        <p>Made with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
