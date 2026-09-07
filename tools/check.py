#!/usr/bin/env python3
"""산출물 회귀 검사 — 수치가 한 문서 안에서 두 번 쓰이지 않았는지,
정직성 표지가 살아 있는지 본다. 통과/실패를 종료 코드로 낸다."""
import re, sys, html as H, pathlib

site = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')

def plain(p):
    s = p.read_text(encoding='utf-8')
    s = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
    return H.unescape(re.sub(r'<[^>]+>', ' ', s))

METRICS = ['262초', '8.1분', '9개 저장소', '11.54', '26.4', '39건', '230초']
MARKERS = {
    'portfolio.html': ['대조하지 못한 항목은 숫자 없이', '고객사·건설사명',
                       '백엔드 유닛과 공동으로 축적', '제가 담당한 구간',
                       '회사 산출물이 아니라'],
    'index.html': ['사내와 별개로'],
    'career.html': ['전후 비교가 가능한 지표 없음'],
}

bad = 0
for name in ('index.html', 'portfolio.html', 'career.html'):
    t = plain(site / name)
    # 중복 금지는 이력서(한 장 안)에만 적용. 나머지 둘은 서술 + 지표 표 반복이 설계다.
    dup = [m for m in METRICS if t.count(m) > 1] if name == 'index.html' else []
    if dup:
        print('⚠️  %-15s 수치 중복 %s' % (name, dup)); bad += 1
    miss = [m for m in MARKERS.get(name, []) if m not in t]
    if miss:
        print('❌ %-15s 정직성 표지 누락 %s' % (name, miss)); bad += 1
    if not dup and not miss:
        scope = '수치 중복 없음 · ' if name == 'index.html' else ''
        print('✅ %-15s %s표지 %d건 유지' % (name, scope, len(MARKERS.get(name, []))))
sys.exit(1 if bad else 0)
