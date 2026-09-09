# 이력서 문서군 — 한 번에 빌드
#
# 원본은 src/*.html 하나뿐이다. 나머지는 전부 여기서 나온다.
#   src/*.html ──┬─> index/portfolio/career.html            (GitHub Pages)
#                ├─> private/현재본-md/*.md                (사람이 읽는 용)
#                ├─> private/현재본-md/사람인-붙여넣기.txt  (채용 사이트 폼)
#                └─> private/이력서-배우현.pdf             (지원처 첨부)
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

.PHONY: all build md saramin pdf check clean help

all: build md saramin		## 빌드 + md + 붙여넣기 텍스트 (기본)
	@echo "\n✅ 완료. 원본은 $(SRC)/*.html — 산출물을 고치지 마세요."

build:				## src/*.html → index/portfolio/career.html
	@cd "$(SITE)" && python3 build.py src

md:				## src/*.html → 현재본-md/*.md (읽기용)
	@for f in $(DOCS); do python3 "$(TOOL)/h2md.py" "$(SRC)/$$f.html" "$(MD)/$$f.md"; done
	@echo "md      → $(MD)/{이력서,경력기술서,포트폴리오}.md"

saramin:			## 이력서 → 채용 사이트 폼 붙여넣기용 평문
	@python3 "$(TOOL)/saramin.py" "$(SRC)/이력서.html" "$(MD)/사람인-붙여넣기.txt"
	@echo "saramin → $(MD)/사람인-붙여넣기.txt"

pdf: build			## index.html → 이력서-배우현.pdf (첨부용)
	@"$(CHROME)" --headless --disable-gpu --no-pdf-header-footer \
	  --print-to-pdf="$(PRIV)/이력서-배우현.pdf" "file://$(SITE)/index.html"
	@echo "pdf     → $(PRIV)/이력서-배우현.pdf (원본이 index.html 로 바뀌었습니다)"

check:				## 수치 중복·정직성 표지 검사
	@python3 "$(TOOL)/check.py" "$(SITE)"

clean:				## 산출물 md·txt 삭제 (src 는 건드리지 않음)
	@rm -f $(MD)/이력서.md $(MD)/경력기술서.md $(MD)/포트폴리오.md $(MD)/사람인-붙여넣기.txt

help:				## 이 목록
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/	—/' | expand -t 12
