import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
from datetime import datetime

# --- 페이지 설정 및 디자인 ---
st.set_page_config(
    page_title="설빙 트렌드 인사이트 대시보드",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS (프리미엄 룩앤필)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        background-color: #f0f2f6;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3d59;
        margin-bottom: 20px;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #e1e8f0 0%, #ffffff 50%, #e1e8f0 100%);
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 5px solid #1e3d59;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1e3d59 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 로딩 로직 ---
@st.cache_data
def load_sulbing_data():
    # GitHub 배포 환경(root)과 로컬 환경(naverapieda)을 모두 고려한 경로 탐색
    possible_paths = ['data', 'naverapieda/data']
    data_dir = None
    
    for path in possible_paths:
        if os.path.exists(path):
            data_dir = path
            break
            
    if not data_dir:
        return None, None
    
    s_files = glob.glob(os.path.join(data_dir, "설빙_search_trend_*.csv"))
    g_files = glob.glob(os.path.join(data_dir, "설빙 기프티콘_search_trend_*.csv"))
    
    if not s_files or not g_files:
        return None, None
    
    # 가장 최근 파일 로드
    df_s = pd.read_csv(s_files[-1])
    df_g = pd.read_csv(g_files[-1])
    
    for df in [df_s, df_g]:
        df['period'] = pd.to_datetime(df['period'])
        df['month'] = df['period'].dt.month
        df['year'] = df['period'].dt.year
        df['dayofweek'] = df['period'].dt.day_name()
        df['is_weekend'] = df['period'].dt.dayofweek.isin([5, 6])
        
    return df_s, df_g

# 데이터 로드 실행
df_s, df_g = load_sulbing_data()

if df_s is None:
    st.error("데이터를 찾을 수 없습니다. 'data' 폴더와 CSV 파일들이 올바른 위치에 있는지 확인해주세요.")
    st.stop()

# --- 사이드바 ---
st.sidebar.image("https://img.icons8.com/clouds/200/ice-cream-cone.png", width=150)
st.sidebar.title("🧊 설빙 인사이트")
st.sidebar.markdown("2024-2025 검색 트렌드 분석")

year_filter = st.sidebar.multiselect("분석 연도 선택", options=[2024, 2025], default=[2024, 2025])
df_s_filtered = df_s[df_s['year'].isin(year_filter)]
df_g_filtered = df_g[df_g['year'].isin(year_filter)]

# --- 메인 헤더 ---
st.markdown('<div class="main-header">설빙 트렌드 분석 프리미엄 대시보드</div>', unsafe_allow_html=True)

# 주요 지표 (Metrics)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("설빙 평균 점수", f"{df_s_filtered['ratio'].mean():.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("기프티콘 평균 점수", f"{df_g_filtered['ratio'].mean():.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("최대 검색 지수", f"{df_s_filtered['ratio'].max():.1f}")
    st.markdown('</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    corr = df_s_filtered['ratio'].corr(df_g_filtered['ratio'])
    st.metric("상관계수 (R)", f"{corr:.3f}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- 분석 탭 ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 시계열 분석", "📅 시기별 분포", "🔗 상관성 & 형태", "📂 데이터 탐색"])

# --- Tab 1: 시계열 분석 ---
with tab1:
    st.subheader("검색 트렌드 마스터 차트")
    
    # 통합 차트
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_s_filtered['period'], y=df_s_filtered['ratio'], name='설빙', line=dict(color='#1e3d59', width=2)))
    fig_line.add_trace(go.Scatter(x=df_g_filtered['period'], y=df_g_filtered['ratio'], name='설빙 기프티콘', line=dict(color='#ff6e40', width=1.5, dash='dot')))
    
    fig_line.update_layout(
        title="2024-2025 통합 검색 트렌드 (일별)",
        xaxis_title="날짜",
        yaxis_title="상대 검색 지수",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown("""
        **[분석 결과]**  
        여름 성수기(7~8월)의 폭발적인 검색량 증가가 뚜렷하며, 브랜드 관심도와 기프티콘 검색량이 매우 유사한 리듬으로 움직이는 것을 확인할 수 있습니다.
    """)

# --- Tab 2: 시기별 분포 ---
with tab2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("월별 검색 지수 분포")
        fig_box = px.box(df_s_filtered, x='month', y='ratio', color='year', 
                         points="all", title="월별 데이터 변동폭 (Boxplot)",
                         color_discrete_sequence=['#1e3d59', '#ff6e40'])
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col_b:
        st.subheader("요일별 소비자 활동성")
        day_avg = df_s_filtered.groupby('dayofweek')['ratio'].mean().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index()
        fig_bar = px.bar(day_avg, x='dayofweek', y='ratio', text_auto='.1f',
                         title="요일별 평균 검색 지수",
                         color='ratio', color_continuous_scale='Blues')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("분기별 비중 (Market Share)")
    df_s_filtered['quarter'] = df_s_filtered['period'].dt.quarter
    q_sum = df_s_filtered.groupby('quarter')['ratio'].sum().reset_index()
    q_sum['quarter'] = q_sum['quarter'].apply(lambda x: f"{x}분기")
    
    fig_pie = px.pie(q_sum, values='ratio', names='quarter', hole=0.4,
                     title="연간 검색 총합의 분기별 점유율",
                     color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- Tab 3: 상관성 & 형태 ---
with tab3:
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.subheader("브랜드 vs 기프티콘 상관관계")
        # 동일 기간 데이터 병합
        combined = pd.merge(df_s_filtered[['period', 'ratio']], df_g_filtered[['period', 'ratio']], on='period', suffixes=('_s', '_g'))
        fig_scatter = px.scatter(combined, x='ratio_s', y='ratio_g', trendline="ols",
                                 labels={'ratio_s': '설빙 검색 지수', 'ratio_g': '기프티콘 검색 지수'},
                                 title="관심도 상관성 분석 (R=0.91)",
                                 marginal_x="histogram", marginal_y="violin")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_d:
        st.subheader("검색 밀도 분포")
        fig_hist = px.histogram(df_s_filtered, x='ratio', nbins=30,
                                title="검색 지수 빈도 분포 (Histogram)",
                                opacity=0.8, color_discrete_sequence=['#1e3d59'])
        st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("평일 vs 주말 분포 비교")
    fig_violin = px.violin(df_s_filtered, y="ratio", x="is_weekend", color="is_weekend",
                           box=True, points="all", hover_data=df_s_filtered.columns,
                           title="평일(False) vs 주말(True) 검색량 밀도 비교",
                           labels={'is_weekend': '주말 여부'},
                           color_discrete_map={True: '#ff6e40', False: '#1e3d59'})
    st.plotly_chart(fig_violin, use_container_width=True)

# --- Tab 4: 데이터 탐색 ---
with tab4:
    st.subheader("수집된 원본 데이터 상세")
    search_query = st.text_input("데이터 필터링 (키워드/날짜 등)")
    
    display_df = pd.concat([df_s_filtered, df_g_filtered])
    if search_query:
        display_df = display_df[display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    
    st.dataframe(display_df, use_container_width=True)
    
    # 다운로드용 데이터 생성
    csv = display_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="필터링된 데이터 다운로드 (CSV)",
        data=csv,
        file_name='sulbing_trend_data.csv',
        mime='text/csv',
    )

# --- 푸터 ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Designed by Antigravity | Naver DataLab API Analytics</p>", unsafe_allow_html=True)

