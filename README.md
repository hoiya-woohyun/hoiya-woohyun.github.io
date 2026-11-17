# 배우현 · 프론트엔드 개발자

세 장짜리 정적 사이트입니다. 외부 의존은 Google Fonts 뿐입니다.

| 페이지 | 내용 | 빌드 입력 |
|---|---|---|
| `index.html` | 포트폴리오 (작업 사례와 판단 근거) | `src/포트폴리오.html` |
| `resume.html` | 이력서 | `src/이력서.html` |
| `career.html` | 경력기술서 (담당 범위와 정량 지표) | `src/경력기술서.html` |

루트의 세 HTML 과 네 PDF(`portfolio.pdf` · `resume.pdf` · `career.pdf` · 이력서+경력기술서 통합본 `resume-career.pdf`)는 **산출물이라
직접 편집하지 않습니다.** `src/` 의 본문을 고친 뒤 `make` 로 다시 만듭니다. `build.py` 가
doctype·head 골격과 「PDF 저장」 버튼을 씌우고, 내비의 절대 URL 을 사이트 내부 상대 경로로
바꿉니다. `make pdf` 는 headless Chrome 으로 브라우저 머리글·바닥글(날짜·제목·URL) 없이
PDF 를 굽고, 버튼은 인쇄 창 대신 이 파일을 내려받습니다 — **본문을 고치면 PDF 도 함께 커밋합니다.**
