# 기록물 전산화 도구 모음

경상북도교육청 2025년 중요기록물 전산화(DB구축) 사업을 위한 특수 목적 도구 모음입니다.

## 주요 기능

- 연호 변환기: 단기/일본 연호를 서기로 변환
- 추가 기능 개발 중

## 기술 스택

- Frontend: Streamlit
- 인증: streamlit-authenticator
- 데이터 처리: pandas
- API: FastAPI

## 로컬 개발 환경 설정

1. Python 3.12 이상 설치
2. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```
3. 앱 실행:
   ```bash
   streamlit run app.py
   ```

## 배포 정보

이 애플리케이션은 Streamlit Community Cloud에서 호스팅됩니다.

- 배포 URL: [추가 예정]
- 테스트 계정:
  - 관리자: admin / admin123
  - 일반 사용자: user1 / admin123

## 보안 정보

- 모든 비밀번호는 bcrypt로 해시되어 저장됩니다.
- 인증은 쿠키 기반으로 관리됩니다.
- 실제 운영 환경에서는 테스트 계정을 제거하고 실제 사용자 계정으로 교체해야 합니다.

## 라이선스

이 프로젝트는 비공개 소프트웨어입니다. 무단 사용 및 배포를 금지합니다.