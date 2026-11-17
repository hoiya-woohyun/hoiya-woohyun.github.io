# 이력서 문서군 — 한 번에 빌드
#
# 원본은 src/*.html 하나뿐이다. 나머지는 전부 여기서 나온다.
#   src/*.html ──┬─> index(포트폴리오)/resume/career.html     (GitHub Pages)
#                ├─> private/현재본-md/*.md                (사람이 읽는 용)
#                ├─> private/현재본-md/사람인-붙여넣기.txt  (채용 사이트 폼)
#                ├─> private/현재본-md/플랫폼-붙여넣기.txt  (자기소개·프로젝트별 설명)
#                └─> portfolio/resume/career.pdf           (GitHub Pages · 내비 「PDF 저장」 · 지원처 첨부)
#                    + resume-career.pdf (이력서+경력기술서 통합본)
#
# private/ 는 .gitignore 대상이다 — 사내 지표가 담긴 산출물이라 커밋하지 않는다.
#
# 산출물을 고치지 마라 — 다음 make 에 사라진다. 고칠 곳은 항상 src/*.html.

SITE := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PRIV := $(SITE)/private
SRC  := $(SITE)/src
TOOL := $(SITE)/tools
MD   := $(PRIV)/현재본-md
DOCS := 이력서 경력기술서 포트폴리오
CHROME := /Applications/Google Chrome.app/Contents/MacOS/Google Chrome

.PHONY: all build md saramin paste pdf check clean help

all: build pdf md saramin paste	## 빌드 + PDF + md + 붙여넣기 텍스트 (기본)
	@echo "\n✅ 완료. 원본은 $(SRC)/*.html — 산출물을 고치지 마세요."

build:				## src/*.html → index(포트폴리오)/resume/career.html
	@cd "$(SITE)" && python3 build.py src

md:				## src/*.html → 현재본-md/*.md (읽기용)
	@for f in $(DOCS); do python3 "$(TOOL)/h2md.py" "$(SRC)/$$f.html" "$(MD)/$$f.md"; done
	@echo "md      → $(MD)/{이력서,경력기술서,포트폴리오}.md"

saramin:			## 이력서 → 채용 사이트 폼 붙여넣기용 평문
	@python3 "$(TOOL)/saramin.py" "$(SRC)/이력서.html" "$(MD)/사람인-붙여넣기.txt"
	@echo "saramin → $(MD)/사람인-붙여넣기.txt"

paste:				## 이력서 + 경력기술서 → 채용 플랫폼용 자기소개·프로젝트별 설명 평문(번호 체계)
	@python3 "$(TOOL)/paste.py" "$(SRC)/이력서.html" "$(SRC)/경력기술서.html" "$(MD)/플랫폼-붙여넣기.txt"
	@echo "paste   → $(MD)/플랫폼-붙여넣기.txt"

# 브라우저 인쇄 창은 머리글·바닥글(날짜·제목·URL)을 끌 수 없다 — 그래서 여기서 끈 채로 구워
# 사이트에 함께 올리고, 내비 「PDF 저장」 은 이 파일을 내려받는다. 이름은 build.py 의 PAGES 와 같아야 한다.
# 인쇄 원본은 문서 간 링크를 사이트 절대 URL 로 바꾼 사본(tools/pdf_src.py) — 상대 링크는 PDF 에서 file:// 가 된다.
PDFS := index.html:portfolio.pdf resume.html:resume.pdf career.html:career.pdf
# 통합본 — 이름은 build.py 의 COMBINED_PDF 와 같아야 한다. pdfunite 는 poppler(brew install poppler).
COMBINED := resume-career.pdf

pdf: build			## index/resume/career.html → portfolio/resume/career.pdf (머리글·바닥글 없음)
	@for p in $(PDFS); do h=$${p%%:*}; o=$${p##*:}; \
	  python3 "$(TOOL)/pdf_src.py" "$(SITE)/$$h" "$(PRIV)/pdf-src/$$h" || exit 1; \
	  "$(CHROME)" --headless --disable-gpu --no-pdf-header-footer --virtual-time-budget=10000 \
	    --print-to-pdf="$(SITE)/$$o" "file://$(PRIV)/pdf-src/$$h" 2>/dev/null || exit 1; \
	  echo "pdf     → $$o (원본은 $$h)"; done
	@pdfunite "$(SITE)/resume.pdf" "$(SITE)/career.pdf" "$(SITE)/$(COMBINED)" || exit 1
	@echo "pdf     → $(COMBINED) (resume.pdf + career.pdf, 내비 「이력서 + 경력기술서 PDF」)"

check:				## 수치 중복·정직성 표지 검사
	@python3 "$(TOOL)/check.py" "$(SITE)"

clean:				## 산출물 md·txt 삭제 (src 는 건드리지 않음)
	@rm -f $(MD)/이력서.md $(MD)/경력기술서.md $(MD)/포트폴리오.md $(MD)/사람인-붙여넣기.txt $(MD)/플랫폼-붙여넣기.txt

help:				## 이 목록
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/	—/' | expand -t 12
