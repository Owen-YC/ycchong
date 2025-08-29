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

# Gemini API 설정
genai.configure(api_key="AIzaSyCJ1F-HMS4NkQ64f1tDRqJV_N9db0MmKpI")
model = genai.GenerativeModel('gemini-pro')

# 페이지 설정
st.set_page_config(
    page_title="SCM Risk 관리 대시보드 Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 - 가독성 개선
st.markdown("""
<style>
    /* 전체 배경 - 밝은 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* 메인 헤더 */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        color: #ffffff;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        letter-spacing: -0.02em;
    }
    
    /* 뉴스 카드 - 가독성 개선 */
    .news-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* 뉴스 제목 */
    .news-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e3a8a;
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
    
    /* 뉴스 링크 버튼 */
    .news-link {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .news-link:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        color: white;
        text-decoration: none;
    }
    
    /* Streamlit 버튼 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* 검색 통계 카드 */
    .search-stats {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* 위험 지표 */
    .risk-indicator {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
    
    /* 챗봇 컨테이너 */
    .chatbot-container {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* 필터 컨테이너 */
    .filter-container {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

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
                # 엔터키 검색을 위한 form 사용
                with st.form("search_form"):
                    query = st.text_input("SCM Risk 키워드를 입력하세요", placeholder="예: 공급망, 물류, 운송...")
                    num_results = st.slider("검색 결과 개수", 100, 1000, 500)
                    submit_button = st.form_submit_button("🔍 SCM Risk 분석", type="primary")
                    
                    if submit_button:
                        if not query.strip():
                            st.error("검색어를 입력해주세요!")
                        else:
                            st.success(f"✅ '{query}' 키워드로 검색을 시작합니다!")
                            st.session_state.query = query
                            st.session_state.num_results = num_results
            
            elif search_option == "빠른 검색":
                quick_queries = ["SCM", "공급망", "물류", "운송", "창고", "재고", "배송", "Risk", "위험", "중단"]
                query = st.selectbox("SCM Risk 키워드 선택", quick_queries)
                num_results = st.slider("검색 결과 개수", 100, 1000, 500)
                
                if st.button("🔍 SCM Risk 분석", type="primary"):
                    st.success(f"✅ '{query}' 키워드로 검색을 시작합니다!")
                    st.session_state.query = query
                    st.session_state.num_results = num_results
            
            else:  # SCM Risk 분석
                query = "SCM"
                num_results = 500
                
                if st.button("🔍 SCM Risk 분석", type="primary"):
                    st.success(f"✅ '{query}' 키워드로 검색을 시작합니다!")
                    st.session_state.query = query
                    st.session_state.num_results = num_results
        
        # 메인 컨텐츠
        if 'query' in st.session_state:
            st.markdown("### 📰 SCM Risk 관련 뉴스")
            st.info(f"🔍 '{st.session_state.query}' 키워드로 검색된 결과입니다.")
            
            # 뉴스 필터링 옵션
            col1, col2 = st.columns([1, 3])
            with col1:
                sort_option = st.selectbox(
                    "정렬 기준",
                    ["최신순", "조회순", "제목순", "출처순"],
                    key="sort_articles"
                )
            
            # 샘플 뉴스 데이터
            sample_news = [
                {
                    "title": "글로벌 SCM 위기, 기업들의 디지털 전환 가속화",
                    "source": "SCM뉴스",
                    "description": "공급망 관리(SCM) 시스템의 글로벌 위기로 인해 기업들이 AI와 IoT 기술을 활용한 디지털 전환을 가속화하고 있습니다.",
                    "url": "https://www.scm-news.com/global-crisis-digital-transformation",
                    "published_time": "2024-01-15T10:30:00Z",
                    "views": 4500
                },
                {
                    "title": "반도체 부족으로 인한 자동차 생산 중단 확산",
                    "source": "자동차뉴스",
                    "description": "글로벌 반도체 부족으로 인해 주요 자동차 제조업체들의 생산 중단이 확산되고 있습니다.",
                    "url": "https://www.autonews.com/semiconductor-shortage-production-disruption",
                    "published_time": "2024-01-14T15:45:00Z",
                    "views": 3800
                },
                {
                    "title": "해운비 상승으로 인한 물류 비용 증가 심화",
                    "source": "물류뉴스",
                    "description": "글로벌 해운비 상승으로 인해 수출입 기업들의 물류 비용이 크게 증가하고 있습니다.",
                    "url": "https://www.logistics-news.com/shipping-cost-increase",
                    "published_time": "2024-01-13T09:20:00Z",
                    "views": 5200
                }
            ]
            
            # 뉴스 표시
            for i, article in enumerate(sample_news, 1):
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
    
    with tab2:
        st.markdown("### 🗺️ 글로벌 SCM Risk 지도")
        
        # 샘플 지도 데이터
        risk_locations = [
            {"name": "중국 상하이", "lat": 31.2304, "lng": 121.4737, "risk": "높음", "description": "공급망 중단 위험", "color": "red"},
            {"name": "미국 로스앤젤레스", "lat": 34.0522, "lng": -118.2437, "risk": "중간", "description": "항구 혼잡", "color": "orange"},
            {"name": "독일 함부르크", "lat": 53.5511, "lng": 9.9937, "risk": "낮음", "description": "물류 지연", "color": "green"},
            {"name": "한국 부산", "lat": 35.1796, "lng": 129.0756, "risk": "낮음", "description": "정상 운영", "color": "green"}
        ]
        
        # 지도 생성
        m = folium.Map(
            location=[20, 0],
            zoom_start=2,
            tiles='OpenStreetMap'
        )
        
        for location in risk_locations:
            popup_html = f"""
            <div style="width: 200px;">
                <h4 style="color: {location['color']}; margin: 0 0 10px 0;">{location['name']}</h4>
                <p style="margin: 5px 0;"><strong>위험도:</strong> <span style="color: {location['color']}; font-weight: bold;">{location['risk']}</span></p>
                <p style="margin: 5px 0; font-size: 12px;">{location['description']}</p>
                <button onclick="alert('관련 뉴스를 검색합니다: {location['name']}')" 
                        style="background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; margin-top: 10px;">
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
        
        folium_static(m, width=1000, height=600)
        
        # 위험도 범례
        st.markdown("#### 🚨 위험도 범례")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("🔴 **높음** - 즉시 대응 필요")
        with col2:
            st.markdown("🟠 **중간** - 모니터링 필요")
        with col3:
            st.markdown("🟢 **낮음** - 정상 운영")
    
    with tab3:
        st.markdown("### 🤖 SCM Risk AI 챗봇")
        st.markdown("SCM Risk 관리에 대한 질문을 해주세요!")
        
        # 챗봇 인터페이스
        user_question = st.text_input("질문을 입력하세요:", placeholder="예: SCM Risk 관리 방법은?")
        
        if st.button("💬 질문하기"):
            if user_question:
                with st.spinner("AI가 답변을 생성하고 있습니다..."):
                    try:
                        prompt = f"""
                        당신은 SCM(공급망관리) Risk 관리 전문가입니다. 
                        다음 질문에 대해 전문적이고 실용적인 답변을 제공해주세요:
                        
                        질문: {user_question}
                        
                        답변은 한국어로 작성하고, SCM Risk 관리 관점에서 구체적이고 실용적인 조언을 포함해주세요.
                        """
                        
                        response = model.generate_content(prompt)
                        
                        st.markdown("#### 🤖 AI 답변:")
                        st.markdown(f"""
                        <div class="chatbot-container">
                            <p style="color: #475569; font-size: 1.1rem; line-height: 1.6;">
                                {response.text}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"AI 응답 생성 중 오류가 발생했습니다: {str(e)}")
            else:
                st.warning("질문을 입력해주세요!")

if __name__ == "__main__":
    main()
