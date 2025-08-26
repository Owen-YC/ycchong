import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
from datetime import datetime
import pandas as pd

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
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .news-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .news-meta {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 0.5rem;
    }
    .news-description {
        font-size: 1rem;
        color: #495057;
        line-height: 1.5;
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
</style>
""", unsafe_allow_html=True)

def get_user_agent():
    """랜덤 User-Agent 반환"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    ]
    return random.choice(user_agents)

def crawl_google_news(query, num_results=10):
    """구글 뉴스에서 뉴스 기사를 크롤링"""
    try:
        # 구글 뉴스 URL 생성
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR%3Ako"
        
        headers = {
            'User-Agent': get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 요청 간격 조절
        time.sleep(random.uniform(1, 2))
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        
        # 구글 뉴스의 기사 요소들을 찾아서 파싱
        news_items = soup.find_all('article', limit=num_results)
        
        for item in news_items:
            try:
                # 제목 추출
                title_element = item.find('h3') or item.find('h4')
                if not title_element:
                    continue
                title = title_element.get_text(strip=True)
                
                # URL 추출
                link_element = item.find('a')
                if not link_element or not link_element.get('href'):
                    continue
                
                # 구글 뉴스의 상대 URL을 절대 URL로 변환
                article_url = link_element['href']
                if article_url.startswith('./'):
                    article_url = 'https://news.google.com' + article_url[1:]
                elif article_url.startswith('/'):
                    article_url = 'https://news.google.com' + article_url
                
                # 출처 추출
                source_element = item.find('div', {'data-n-tid': True}) or item.find('span')
                source = source_element.get_text(strip=True) if source_element else "Unknown"
                
                # 발행 시간 추출 (가능한 경우)
                time_element = item.find('time')
                published_time = time_element.get('datetime') if time_element else None
                
                # 설명 추출 (가능한 경우)
                description_element = item.find('p') or item.find('span', class_='')
                description = description_element.get_text(strip=True) if description_element else None
                
                if title and article_url:
                    article = {
                        'title': title,
                        'url': article_url,
                        'source': source,
                        'published_time': published_time,
                        'description': description
                    }
                    articles.append(article)
                    
            except Exception as e:
                st.error(f"개별 기사 파싱 오류: {e}")
                continue
        
        return articles
        
    except Exception as e:
        st.error(f"크롤링 오류: {e}")
        return []

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
        st.header("🔧 설정")
        
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
    
    # 메인 컨텐츠
    if 'articles' in st.session_state and st.session_state.articles:
        articles = st.session_state.articles
        
        # 통계 정보
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 뉴스 수", len(articles))
        with col2:
            sources = set(article['source'] for article in articles)
            st.metric("뉴스 출처 수", len(sources))
        with col3:
            st.metric("검색 시간", datetime.now().strftime("%H:%M:%S"))
        
        # 뉴스 목록
        st.subheader("📰 뉴스 목록")
        
        for i, article in enumerate(articles, 1):
            with st.container():
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
                    <a href="{article['url']}" target="_blank" style="color: #1f77b4; text-decoration: none;">
                        🔗 원문 보기
                    </a>
                </div>
                """, unsafe_allow_html=True)
        
        # 데이터프레임으로 표시
        st.subheader("📊 데이터 테이블")
        df = pd.DataFrame(articles)
        st.dataframe(df, use_container_width=True)
        
        # CSV 다운로드
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 파일 다운로드",
            data=csv,
            file_name=f"google_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
