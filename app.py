# app.py

import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from components.ui import section, card, info_box, header

# 페이지 설정
st.set_page_config(
    page_title="기록물 전산화 도구 모음",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 적용
def load_css(css_file):
    with open(css_file, encoding='utf-8') as f:
        return f"<style>{f.read()}</style>"

# 타이포그래피 스타일 적용
st.markdown(load_css("styles/typography.css"), unsafe_allow_html=True)

# 세션 상태 초기화
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'name' not in st.session_state:
    st.session_state['name'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

# 인증 설정 로드
with open('config.yaml', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# 인증 객체 생성
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# 로그인 위젯 표시
name, authentication_status, username = authenticator.login('로그인', 'main')

if authentication_status == False:
    st.error('아이디나 비밀번호가 올바르지 않습니다.')
elif authentication_status == None:
    st.warning('아이디와 비밀번호를 입력하세요.')
else:
    # 사이드바 구성
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50.png?text=Logo", use_column_width=True)
        st.divider()
        
        # 사용자 정보 표시
        st.markdown(f"### 👤 {st.session_state['name']}님 환영합니다!")
        authenticator.logout('로그아웃', 'sidebar')
        
        st.divider()
        st.markdown("### 🧰 도구 모음")
        st.markdown("현재 사용 가능한 도구:")
        current_page = "홈"
        
        menu_items = {
            "🏠 홈": "홈",
            "📅 연호 변환기": "연호 변환기",
            "🔜 추가 예정": "추가 예정"
        }
        
        for label, page in menu_items.items():
            if page == current_page:
                st.markdown(f"**{label}** ←")
            else:
                st.markdown(label)
        
        st.divider()
        st.markdown("### ℹ️ 정보")
        st.markdown("버전: 1.0.0")
        st.markdown("[사용 설명서]()")
        st.markdown("[피드백 보내기]()")

    # 헤더
    header(
        "기록물 전산화 도구 모음",
        "경상북도교육청 2025년 중요기록물 전산화(DB구축) 사업을 위한 특수 목적 도구 모음입니다."
    )

    # 프로젝트 정보
    with section("프로젝트 소개", "📋"):
        st.markdown("""
        이 애플리케이션은 **경상북도교육청 2025년 중요기록물 전산화(DB구축) 사업**을 지원하기 위한 특수 목적 도구 모음입니다.
        """)
        
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                with card("목적", icon="🎯"):
                    st.markdown("""
                    - 기록물 전산화 작업의 효율성 향상
                    - 데이터 표준화 및 품질 관리 지원
                    - 작업 프로세스 개선 및 자동화
                    """)
            
            with col2:
                with card("연계 정보", icon="🔄"):
                    st.markdown("""
                    이 도구 모음은 독립적으로 개발되어 테스트된 후, 향후 공정관리 솔루션과 연계되어 통합 운영될 예정입니다.
                    """)

    # 사용 가능한 도구 소개
    with section("사용 가능한 도구", "📌"):
        st.markdown("### 현재 사용 가능한 도구")
        
        tools_col1, tools_col2 = st.columns(2)
        
        with tools_col1:
            with card("연호 변환기", icon="📅", description="다양한 연호를 서기(西紀) 연도로 변환합니다."):
                st.markdown("""
                - 단기 → 서기 변환
                - 일본 연호 → 서기 변환
                - YYYY 형식 통일
                """)
                st.button("🔗 바로가기", key="goto_chrono")
        
        with tools_col2:
            with card("추가 예정", icon="🔜"):
                st.markdown("""
                - 추가 도구 개발 중
                - 사용자 피드백 반영
                - 지속적 업데이트
                """)
                st.button("🔔 알림 신청", key="notify_new", disabled=True)
        
        info_box("사업 진행에 따라 필요한 도구들이 지속적으로 추가될 예정입니다.", "info")

    # 사용 방법
    with section("사용 방법", "💡"):
        st.markdown("### 시작하기")
        usage_col1, usage_col2 = st.columns(2)
        
        with usage_col1:
            with card("기본 사용법"):
                st.markdown("""
                1. 왼쪽 사이드바에서 원하는 도구를 선택합니다.
                2. 각 도구의 설명을 참고하여 필요한 작업을 수행합니다.
                3. 결과를 확인하고 활용합니다.
                """)
        
        with usage_col2:
            with card("팁"):
                st.markdown("""
                - 📱 모바일에서도 사용 가능합니다.
                - 💾 결과를 CSV로 저장할 수 있습니다.
                - ❓ 각 기능에 도움말이 제공됩니다.
                """)
        
        info_box("각 도구는 독립적으로 작동하며, 추후 공정관리 솔루션과 통합될 예정입니다.", "warning")

    # 푸터
    st.divider()
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        st.markdown('<div class="footer-text" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("Made with ❤️ for 경상북도교육청")
        st.markdown('<div class="version-text">버전: 1.0.0</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) 