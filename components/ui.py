import streamlit as st
from contextlib import contextmanager

@contextmanager
def section(title=None, icon=None):
    """기본 섹션 컴포넌트"""
    st.markdown('<div class="section">', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div class="section-title">{icon + " " if icon else ""}{title}</div>', unsafe_allow_html=True)
    yield
    st.markdown('</div>', unsafe_allow_html=True)

@contextmanager
def card(title=None, description=None, icon=None):
    """카드 컴포넌트"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div class="card-title">{icon + " " if icon else ""}{title}</div>', unsafe_allow_html=True)
    if description:
        st.markdown(f'<div class="card-description">{description}</div>', unsafe_allow_html=True)
    yield
    st.markdown('</div>', unsafe_allow_html=True)

def info_box(content, type="info"):
    """정보 박스 컴포넌트"""
    icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "success": "✅",
        "error": "❌"
    }
    st.markdown(f'<div class="info-box info-box-{type}">{icons.get(type, "")} {content}</div>', unsafe_allow_html=True)

@contextmanager
def result_box(title=None):
    """결과 표시 컴포넌트"""
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    if title:
        st.markdown(f'### {title}')
    yield
    st.markdown('</div>', unsafe_allow_html=True)

def action_button(label, key=None, help=None):
    """액션 버튼 컴포넌트"""
    return st.button(
        label,
        key=key,
        help=help,
        use_container_width=True
    )

def header(title, description=None):
    """페이지 헤더 컴포넌트"""
    st.title(title)
    if description:
        st.markdown(f'<div class="page-description">{description}</div>', unsafe_allow_html=True)
    st.markdown("---") 