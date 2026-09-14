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
# 내비의 정본은 GitHub Pages 절대 URL 이다 — 아티팩트에서 눌러도 claude.ai 뷰어가 아니라
# 사이트로 간다(사이트가 아티팩트와 같은 HTML 을 낸다). 빌드에서만 상대 경로로 바꾼다.
# 긴 경로를 먼저 치환해야 루트 규칙이 앞을 잘라먹지 않는다.
ROUTES = {
    r"https://hoiya-woohyun\.github\.io/resume\.html": "./resume.html",
    r"https://hoiya-woohyun\.github\.io/career\.html": "./career.html",
    r"https://hoiya-woohyun\.github\.io/(?![\w.])": "./index.html",
    # 과거 본문에 남아 있을 수 있는 아티팩트 URL 도 함께 흡수한다
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

PRINT_CSS = """<style>
/* ── 인쇄(PDF 저장) ──────────────────────────────────────────
   글자를 이미지로 굽지 않는다. 브라우저 인쇄를 그대로 쓰므로
   PDF 안에서 복사·검색이 되고 채용 사이트의 파서가 읽을 수 있다. */
@media print {
  /* 페이지 번호는 문서가 직접 찍는다(@page 여백 상자, Chrome 131+).
     브라우저 인쇄 대화상자의 "머리글 및 바닥글"(날짜·제목·URL)은 CSS 로 끌 수 없으니
     사용자가 끄고, 번호는 여기서 나온다. */
  @page {
    margin: 14mm 12mm 16mm;
    @bottom-center {
      content: counter(page) " / " counter(pages);
      font: 8.5pt/1 'Apple SD Gothic Neo', 'Malgun Gothic', system-ui, sans-serif;
      color: #8A94A6;
    }
  }

  /* 화면 전용 요소 — 고정 내비는 인쇄하면 매 장 상단에 반복된다 */
  .sitenav, .rail, .printbtn { display: none !important; }

  /* 시스템이 다크 모드여도 흰 바탕으로 인쇄되도록 팔레트를 라이트로 고정 */
  :root, :root[data-theme="dark"] {
    color-scheme: light;
    --ground: #FFFFFF; --surface: #FFFFFF; --surface-2: #FFFFFF; --sunken: #F4F6FA;
    --ink: #111827; --ink-2: #33405A; --ink-3: #56637C;
    --rule: #C7D0DD; --rule-2: #DFE5EE;
    --accent: #14448F; --accent-2: #14448F;
    --wash: #EEF3FB; --accent-wash: #EEF3FB;
    --shadow: none;
  }
  body { background: #FFFFFF !important; }

  /* 화면 폭 제약을 풀고 한 단으로 — 지면 폭은 용지가 정한다 */
  .wrap { max-width: none !important; padding-inline: 0 !important; }
  .page-grid { display: block !important; }

  /* 장 경계에서 갈리면 안 되는 것 — 작은 단위만 묶는다.
     큰 블록까지 묶으면 남은 자리에 못 들어가 통째로 다음 장으로 밀리고,
     밀린 만큼이 빈칸으로 남는다(21쪽짜리에서 4~5쪽 분량이 이렇게 버려졌다). */
  .fact, .metrics > div, .stack-row, .ratio, .cat > div, .abil > li,
  .blk, .rec-meta, .acts > li, .prev-item, .tnote, tr
  { break-inside: avoid; page-break-inside: avoid; }

  /* 반대로 큰 컨테이너는 갈려도 된다 — 갈리는 지점은 위 규칙이 잡아준다 */
  .rec, .recs, .rec-body, .cap, .case, .tool, .cv > div, .shift, .trace,
  .built, .sect, .tablewrap, .scroll, table
  { break-inside: auto; page-break-inside: auto; }

  h1, h2, h3, h4, h5 { break-after: avoid; page-break-after: avoid; }
  /* 한 줄만 남기고 갈리는 것도 빈칸만큼 보기 나쁘다 */
  p, li { orphans: 2; widows: 2; }

  /* 화면용 여백은 지면에서 낭비다 */
  section.band, .sect { padding-block: 16px !important; }
  .sect + .sect { margin-top: 22px !important; }
  .hero { padding-block: 0 22px !important; }
  .hero-in, .page { padding-block: 0 !important; }
  .facts { margin-top: 24px !important; }
  .rec { box-shadow: none !important; }

  /* 가로 스크롤 컨테이너는 지면에서 펼친다 — 안 그러면 표 오른쪽이 잘린다 */
  .tablewrap, .scroll { overflow: visible !important; }
  table { min-width: 0 !important; }

  a { text-decoration: none; }
}

/* 내비의 인쇄 버튼 */
.printbtn {
  font: inherit; font-size: 12.5px; line-height: inherit;
  color: var(--ink-3); background: transparent;
  border: 1px solid var(--rule); padding: 5px 12px;
  margin-left: 4px; cursor: pointer; white-space: nowrap;
}
.printbtn:hover { color: var(--accent); border-color: var(--accent); }
</style>"""

NAV_CSS = """<style>
/* ── 사이트 내비 — 세 페이지에서 픽셀 단위로 같아야 한다 ──────────────
   각 문서의 본문 폰트가 다르다(A4 문서는 Apple SD Gothic Neo 10pt,
   포트폴리오는 Gothic A1 15px). 내비가 본문에서 폰트를 상속하면 페이지를
   옮길 때마다 글자 폭이 달라져 헤더가 흔들린다 — 그래서 여기서 자기 값을 고정한다.
   현재 페이지 링크를 굵게 하는 것도 같은 이유로 하지 않는다(볼드 폭만큼 내비가 밀린다).
   현재 위치는 굵기가 아니라 색·배경·테두리로 표시한다.
   이 블록은 각 문서의 <style> 뒤에 주입되므로 문서 쪽 .sitenav 규칙을 덮는다. */
.sitenav {
  position: sticky; top: 0; z-index: 50;
  background: var(--surface); border-bottom: 1px solid var(--rule);
  font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', system-ui, sans-serif;
  font-size: 12.5px; line-height: 1.4; letter-spacing: normal;
}
.sitenav .sitenav-in {
  display: flex; align-items: center; flex-wrap: wrap; gap: 6px 18px;
  max-width: 1180px; margin-inline: auto; padding: 12px 28px;
}
.sitenav .sitenav-who {
  font-size: 15px; font-weight: 700; letter-spacing: -.02em;
  color: var(--ink); line-height: 1.4;
}
.sitenav .sitenav-role {
  font-size: 12.5px; font-weight: 400; letter-spacing: normal;
  color: var(--ink-3); line-height: 1.4;
}
.sitenav nav { margin-left: auto; display: flex; align-items: center; gap: 4px; }
.sitenav nav a, .sitenav .printbtn {
  display: inline-flex; align-items: center; box-sizing: border-box; height: 28px;
  margin: 0; padding: 0 12px;
  font-family: inherit; font-size: 12.5px; font-weight: 500;
  line-height: 1; letter-spacing: normal;
  text-decoration: none; white-space: nowrap;
  color: var(--ink-3); background: transparent;
  border: 1px solid transparent; border-radius: 0; cursor: pointer;
}
.sitenav nav a:hover, .sitenav .printbtn:hover { color: var(--ink); border-color: var(--rule); }
.sitenav nav a[aria-current="page"] {
  color: var(--accent); border-color: var(--rule);
  background: var(--wash); font-weight: 500;
}
.sitenav .printbtn { margin-left: 4px; border-color: var(--rule); }
.sitenav .printbtn:hover { color: var(--accent); border-color: var(--accent); }
</style>"""

PRINT_BTN = """      <button type="button" class="printbtn" onclick="window.print()"
        title="인쇄 대화상자에서 대상을 &quot;PDF로 저장&quot;으로 선택하고, 옵션의 &quot;머리글 및 바닥글&quot;은 끄세요 — 페이지 번호는 문서가 직접 찍습니다">PDF 저장</button>
"""

PAGES = [
    ("포트폴리오.html", "index.html",
     "배우현 · 프론트엔드 개발자 포트폴리오 — 사람이 기억하던 규칙을 타입 체크와 CI가 검증하게 만듭니다."),
    ("이력서.html", "resume.html",
     "배우현 · 프론트엔드 개발자 이력서 — 6개 제품 병행 담당, 규칙을 타입 체크와 CI가 검증하게 만듭니다."),
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

    old_nav_end = "    </nav>\n  </div>\n</header>"        # 아티팩트에는 없고 사이트에만 붙는다
    assert body.count(old_nav_end) == 1, "내비 끝을 찾지 못함"
    body = body.replace(old_nav_end, PRINT_BTN + old_nav_end, 1)

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
{NAV_CSS}
{PRINT_CSS}
</head>
<body>
{body.strip()}
</body>
</html>
""")
    print(f"{out:14} {(DST / out).stat().st_size:>7,} bytes   {title}")

# 옛 주소 — 포트폴리오가 index 로 옮겨가기 전에 공유된 링크가 살아 있도록 리다이렉트만 남긴다
io.open(DST / "portfolio.html", "w", encoding="utf-8").write("""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=./index.html">
<link rel="canonical" href="https://hoiya-woohyun.github.io/">
<meta name="robots" content="noindex">
<title>배우현 포트폴리오</title></head>
<body><p>포트폴리오는 <a href="./index.html">https://hoiya-woohyun.github.io/</a> 로 옮겼습니다.</p></body></html>
""")
print("portfolio.html  → index.html 리다이렉트")
