#!/usr/bin/env python3
"""사이트 HTML → PDF 로 구울 사본.

사이트는 문서끼리 상대 경로(./resume.html)로 잇는다. 그대로 file:// 에서 인쇄하면 PDF 안의
링크가 빌드한 PC 의 경로(file:///Users/…)가 되어, 받는 사람에게는 열리지 않고 로컬 경로만
드러난다. 그래서 PDF 용 사본에서만 문서 간 링크를 사이트 절대 URL 로 되돌린다.
<base> 를 쓰지 않는 이유: 문서 안 앵커(#work)까지 사이트 URL 로 바뀌어 PDF 내부 이동이 깨진다.

사용: python3 pdf_src.py <사이트 HTML> <출력 HTML>
"""
import re, sys, pathlib

SITE = "https://hoiya-woohyun.github.io/"
src, dst = map(pathlib.Path, sys.argv[1:3])

s = src.read_text(encoding="utf-8")
s = re.sub(r'href="\./index\.html', f'href="{SITE}', s)
s = re.sub(r'href="\./(?=[\w-]+\.(?:html|pdf))', f'href="{SITE}', s)
# 사본은 private/pdf-src/ 에 놓이므로 이미지 같은 사이트 자산의 상대 경로는 원본 위치 기준 file:// 로 고정한다
s = re.sub(r'src="(?=assets/)', f'src="{src.resolve().parent.as_uri()}/', s)
assert 'href="./' not in s, "절대 URL 로 바꾸지 못한 상대 링크가 남았다"

dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(s, encoding="utf-8")
