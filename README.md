# 배우현 · 프론트엔드 개발자

세 장짜리 정적 사이트입니다. 외부 의존은 Google Fonts 뿐입니다.

| 페이지 | 내용 | 빌드 입력 |
|---|---|---|
| `index.html` | 이력서 | `src/이력서.html` |
| `portfolio.html` | 포트폴리오 (작업 사례와 판단 근거) | `src/포트폴리오.html` |
| `career.html` | 경력기술서 (담당 범위와 정량 지표) | `src/경력기술서.html` |

루트의 세 HTML 은 **산출물이라 직접 편집하지 않습니다.** `src/` 의 본문을 고친 뒤
`python3 build.py src` 로 다시 만듭니다. `build.py` 가 doctype·head 골격과 인쇄 버튼을
씌우고, 내비의 절대 URL 을 사이트 내부 상대 경로로 바꿉니다.
