#!/usr/bin/env python3
"""Claude 아티팩트 본문 → 단독 실행 가능한 정적 HTML.

아티팩트는 <!doctype>·<head> 골격 없이 '몸통'만 저장된다(발행 시점에 씌워짐).
그래서 그대로 올리면 <title>·charset 이 <body> 안에 박힌 깨진 문서가 된다.
이 스크립트가 골격을 씌우고, 아티팩트끼리의 claude.ai 링크를 사이트 내부
상대 경로로 바꾼다.

사용: python3 build.py <아티팩트본문_디렉터리>
"""
import io, re, sys, pathlib

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
DST = pathlib.Path(__file__).parent

# 아티팩트 URL → 사이트 내부 경로
ROUTES = {
    r"https://claude\.ai/code/artifact/1b96a19e[0-9a-f\-]*": "./index.html",
    r"https://claude\.ai/code/artifact/16434158[0-9a-f\-]*": "./career.html",
}

HEAD_EXTRA = """<meta name="robots" content="noindex, nofollow">
<style>
  :root { color-scheme: light dark; }
  body { margin: 0; padding: 0; }
  img { max-width: 100%; }
  [hidden] { display: none !important; }
</style>"""

PAGES = [
    ("포트폴리오.html", "index.html",
     "배우현 · 프론트엔드 개발자 포트폴리오 — 사람이 기억하던 규칙을 도구가 검증하게 만듭니다."),
    ("경력기술서.html", "career.html",
     "배우현 · 프론트엔드 개발자 경력기술서 — 담당 범위와 정량 지표의 기록."),
]

for src, out, desc in PAGES:
    raw = io.open(SRC / src, encoding="utf-8").read()
    cut = raw.index("</style>") + len("</style>")          # 첫 <style> 블록까지가 head 재료
    head, body = raw[:cut], raw[cut:]

    title = re.search(r"<title>(.*?)</title>", head).group(1)
    link = re.search(r'<link rel="stylesheet"[^>]*>', head).group(0)
    style = head[head.index("<style>"):]

    for pat, href in ROUTES.items():                        # 자기 자신 링크도 함께 치환
        body = re.sub(pat, href, body)

    io.open(DST / out, "w", encoding="utf-8").write(f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="profile">
{link}
{HEAD_EXTRA}
{style}
</head>
<body>
{body.strip()}
</body>
</html>
""")
    print(f"{out:14} {(DST / out).stat().st_size:>7,} bytes   {title}")
