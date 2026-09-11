#!/usr/bin/env python3
"""산출물 회귀 검사 — 수치가 한 문서 안에서 두 번 쓰이지 않았는지,
정직성 표지가 살아 있는지 본다. 통과/실패를 종료 코드로 낸다."""
import re, sys, html as H, pathlib

site = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')

def plain(p):
    s = p.read_text(encoding='utf-8')
    s = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
    return H.unescape(re.sub(r'<[^>]+>', ' ', s))

METRICS = ['262초', '8.1분', '9개 저장소', '26.4', '39건', '230초']
# 문서 간 정합 — 같은 사실이 세 문서에서 한 표기로만 쓰여야 한다.
# 한 문서만 고치고 다른 둘을 놓친 회귀가 실제로 있었다(43건 vs 40건+봇 3건).
# 항목: 금지 표기 → (정본 표기, 이유). 정본은 docs/편집원칙.md §3.10.
VARIANTS = {
    '런칭':            ('론칭', '표기 통일'),
    '(주)':             ('주식회사 …', '회사명은 전부 주식회사 접두 형식'),
    'HT Beyond':       ('주식회사 에이치티비욘드', '영문 표기 금지'),
    '년차':            ('7년 6개월', '경력은 한 축으로'),
    '나머지 43건':      ('40건 … (나머지 3건은 봇 생성분)', '원장 §⑤: 팀원 40 · 봇 3'),
    'pre_build':       ('PR 사전 빌드 워크플로', '사내 워크플로 이름 노출'),
}

MARKERS = {
    'portfolio.html': ['대조하지 못한 항목은 숫자 없이', '고객사·건설사명',
                       '백엔드 팀과 공동으로 축적', '제가 담당한 구간',
                       '회사 산출물이 아니라'],
    'index.html': ['사내와 별개로'],
    'career.html': ['전후 비교가 가능한 지표가 없습니다'],
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
    var = [(v, VARIANTS[v][0]) for v in VARIANTS if v in t]
    if var:
        for v, canon in var:
            print('❌ %-15s 표기 불일치 %r → %r' % (name, v, canon))
        bad += 1
    if not dup and not miss and not var:
        scope = '수치 중복 없음 · ' if name == 'index.html' else ''
        print('✅ %-15s %s표지 %d건 유지' % (name, scope, len(MARKERS.get(name, []))))
sys.exit(1 if bad else 0)
