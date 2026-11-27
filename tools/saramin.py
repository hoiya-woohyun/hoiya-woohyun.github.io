#!/usr/bin/env python3
"""src/이력서.html → 채용 사이트 폼 붙여넣기용 평문.

사람인 등 지원서 칸은 마크다운을 렌더링하지 않는다. 굵게 표기와 링크를 걷어내고
칸 이름별로 잘라 둔다. 핵심 역량 섹션이 있는 원고에서는 칸이 좁을 때를 위해 장·단 두 벌을 낸다.

목록은 상위 「  - 」, 하위(ul.ev) 「    - 」 로 낸다. 하위 목록이 있는 항목도 상위 문장을 잃지 않게
paste.py 의 중첩 파서(items_of)를 쓰고, 목록 범위는 ul 여닫힘 짝으로 자른다.
"""
import io, re, sys, html as H
from paste import items_of, ul_lines, intro_paras


def bullets(block):
    block = re.sub(r'<b class="k">(.*?)</b>', r'\1 · ', block, flags=re.S)   # 핵심 역량 라벨 — h2md 와 같은 구분
    return [('    - ' if d else '  - ') + t for d, t in items_of(block)]

def txt(x):
    x = re.sub(r'<(b|strong)\b[^>]*>(.*?)</\1>', r'\2', x, flags=re.S)
    x = re.sub(r'<code\b[^>]*>(.*?)</code>', r'\1', x, flags=re.S)
    x = H.unescape(re.sub(r'<[^>]+>', '', x))
    return re.sub(r'[ \t\n]+', ' ', x).strip()

def lis(block):
    return [txt(m) for m in re.findall(r'<li\b[^>]*>((?:(?!<li|</li|<ul).)*?)</li>', block, re.S) if txt(m)]

def proj_head(p):
    """제품명 (한 줄 설명 · 기간)."""
    get = lambda pat: (lambda m: txt(m.group(1)) if m else '')(re.search(pat, p, re.S))
    extra = ' · '.join(x for x in (get(r'<span class="note[^"]*">(.*?)</span>'), get(r'<span class="term">(.*?)</span>')) if x)
    return get(r'<h4>(.*?)</h4>') + (' (%s)' % extra if extra else '')

def build(src):
    s = io.open(src, encoding='utf-8').read()
    def sec(name):
        m = re.search(r'<h2[^>]*>%s</h2>(.*?)</section>' % name, s, re.S)
        return m.group(1) if m else None
    o, W = [], 60
    rule = lambda c: c * W
    def head(t):
        o.extend(['', rule('='), t, rule('='), ''])

    tag = txt(re.search(r'<p class="tagline">(.*?)</p>', s, re.S).group(1))
    total = txt(re.search(r'<dt>총 경력</dt>\s*<dd>(.*?)</dd>', s, re.S).group(1))

    o += [rule('='), '채용 사이트 폼 붙여넣기용 — 배우현',
          '자동 생성 · 원본 src/이력서.html · 총 경력 %s' % total, rule('='), '',
          '· 각 칸의 내용을 같은 이름 칸에 그대로 붙여넣으세요. 서식은 없습니다.',
          '· 「=」「-」 선은 구분용이니 붙여넣지 마세요.',
          '· 이 파일은 재생성됩니다. 손으로 고치면 다음 make 에 사라집니다.']

    head('이력서 제목 / 한 줄 소개')
    o.append(tag)

    head('자기소개')
    o += intro_paras(sec('자기소개'))

    core = sec('핵심 역량')          # 이력서에서 걷어낸 섹션 — 있는 원고(옛 시안 등)에서만 칸을 낸다
    if core:
        head('핵심 역량 — 전체')
        for m in re.finditer(r'<h3>(.*?)</h3>', core, re.S):
            o.append('[%s]' % txt(m.group(1)))
            o += bullets(ul_lines(core, m.end()))
            o.append('')

        head('핵심 역량 — 칸이 좁을 때 (블록 제목만)')
        o += [txt(m) for m in re.findall(r'<h3>(.*?)</h3>', core, re.S)]

    head('경력 사항')
    for c in re.split(r'<div class="co(?: long)?">', sec('경력 상세'))[1:]:
        nm = re.search(r'<h3>(.*?)</h3>', c, re.S)
        if not nm: continue
        o += [rule('-'), '회사명   %s' % txt(nm.group(1))]
        for k, cls in (('기간', 'term'), ('직무', 'role')):
            v = re.search(r'<span class="%s">(.*?)</span>' % cls, c, re.S)
            if v: o.append('%s     %s' % (k, txt(v.group(1))))
        d = re.search(r'<p class="co-desc">(.*?)</p>', c, re.S)
        if d: o += ['', '설명', '  ' + txt(d.group(1))]
        co_only, *projs = c.split('<div class="proj">')       # 제품 소제목(div.proj)이 있으면 제품별로
        b = ul_lines(co_only)
        if b: o += ['', '담당업무 및 성과'] + bullets(b)
        for p in projs:
            o += ['', '■ ' + proj_head(p)]
            mine = re.search(r'<p class="proj-role">(.*?)</p>', p, re.S)
            if mine: o.append('  ' + txt(mine.group(1)))
            o += bullets(ul_lines(p))
        o.append('')

    head('개인 프로젝트')
    for c in sec('개인 프로젝트').split('<div class="co">')[1:]:
        o.append('프로젝트명   %s' % txt(re.search(r'<h3>(.*?)</h3>', c, re.S).group(1)))
        for k, cls in (('기간', 'term'), ('역할', 'role')):
            o.append('%s     %s' % (k, txt(re.search(r'<span class="%s">(.*?)</span>' % cls, c, re.S).group(1))))
        o += ['', '설명', '  ' + txt(re.search(r'<p class="co-desc">(.*?)</p>', c, re.S).group(1))]
        o += ['', '내용'] + bullets(ul_lines(c))

    head('보유 기술')
    for m in re.finditer(r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>', sec('보유 기술'), re.S):
        o.append('[%s] %s' % (txt(m.group(1)), txt(m.group(2))))
    return '\n'.join(o).rstrip() + '\n'

if __name__ == '__main__':
    io.open(sys.argv[2], 'w', encoding='utf-8').write(build(sys.argv[1]))
