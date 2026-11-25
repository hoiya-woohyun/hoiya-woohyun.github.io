#!/usr/bin/env python3
"""산출물 회귀 검사 — 수치가 한 문서 안에서 두 번 쓰이지 않았는지,
정직성 표지가 살아 있는지 본다. 통과/실패를 종료 코드로 낸다."""
import re, sys, html as H, pathlib

site = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')

def plain(p):
    s = p.read_text(encoding='utf-8')
    s = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
    return H.unescape(re.sub(r'<[^>]+>', ' ', s))

METRICS = ['115초', '8.1분', '10개 저장소']
# 문서 간 정합 — 같은 사실이 세 문서에서 한 표기로만 쓰여야 한다.
# 한 문서만 고치고 다른 둘을 놓친 회귀가 실제로 있었다(43건 vs 40건+봇 3건).
# 항목: 금지 표기 → (정본 표기, 이유). 정본은 docs/편집원칙.md §3.10.
VARIANTS = {
    '론칭':            ('런칭', '표기 통일 — 실무 표기 우선(2026-11-17 사용자 요청)'),
    '단지 관리자 운영툴': ('관리사무소 운영툴', '제품명 통일 — 사내 운영 콘솔과 구분(2026-11-17 사용자 결정)'),
    '(주)':             ('주식회사 …', '회사명은 전부 주식회사 접두 형식'),
    'HT Beyond':       ('주식회사 에이치티비욘드', '영문 표기 금지'),
    '년차':            ('7년 9개월', '경력은 한 축으로'),
    '나머지 43건':      ('40건 … (나머지 3건은 봇 생성분)', '원장 §⑤: 팀원 40 · 봇 3'),
    'pre_build':       ('PR 사전 빌드 워크플로', '사내 워크플로 이름 노출'),
    '리드타임':         ('버그 처리 시간', '면접관·기획자가 쓰지 않는 통계 용어'),
    '결함 유입':        ('신규 버그 접수', '면접관·기획자가 쓰지 않는 통계 용어'),
    '상위 10% 구간':    ('오래 걸릴 때', '면접관·기획자가 쓰지 않는 통계 용어'),
    '이 문서에 대하여':  ('(섹션 없음)', '경력기술서에 문서 설명 섹션을 두지 않는다'),
}

MARKERS = {
    # 포트폴리오 = 01 개인 제품 + 02 회사 사례 3건(2026-11-08 Work 절 복원). 정직성 표지:
    # 대조 범위 선언 · 회사 산출물과의 경계 · 아직 막지 못한 노출 경로의 인정.
    # 2026-11-17 포트폴리오를 프로젝트 카드 형식으로 개편하며 01 Project 의 사례 글과 머리말을 걷어냄
    'index.html': ['대조하지 못한 항목은 숫자 없이'],
    # 이력서의 개인 셀프 리뷰 게이트 항목은 2026-11-16 사용자 결정으로 삭제
    'resume.html': [],
    # 경력기술서 해명 단락은 2026-11-16 삭제 — 남은 정직성 문구는 지표 근거 표 안에 있다:
    # 구조 값이 전후 측정이 아님(§1.8). 사이니지 CMS 버그 처리 시간 지표(인과 미분리 표지)는
    # 근거 부족으로 2026-11-17 사용자 결정에 따라 삭제
    'career.html': ['전후 측정값이 아닌 구조 값'],
}

bad = 0
for name in ('index.html', 'resume.html', 'career.html'):
    t = plain(site / name)
    # 중복 금지는 이력서 resume.html(한 장 안)에만 적용. 나머지 둘은 서술 + 지표 표 반복이 설계다.
    dup = [m for m in METRICS if t.count(m) > 1] if name == 'resume.html' else []
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
        scope = '수치 중복 없음 · ' if name == 'resume.html' else ''
        print('✅ %-15s %s표지 %d건 유지' % (name, scope, len(MARKERS.get(name, []))))
sys.exit(1 if bad else 0)
