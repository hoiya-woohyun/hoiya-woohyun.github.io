#!/usr/bin/env python3
"""src/이력서.html → 채용 사이트 폼 붙여넣기용 평문.

사람인 등 지원서 칸은 마크다운을 렌더링하지 않는다. 굵게 표기와 링크를 걷어내고
칸 이름별로 잘라 둔다. 칸이 좁을 때를 위해 핵심 역량은 장·단 두 벌을 낸다.
"""
import io, re, sys, html as H

def txt(x):
    x = re.sub(r'<(b|strong)\b[^>]*>(.*?)</\1>', r'\2', x, flags=re.S)
    x = re.sub(r'<code\b[^>]*>(.*?)</code>', r'\1', x, flags=re.S)
    x = H.unescape(re.sub(r'<[^>]+>', '', x))
    return re.sub(r'[ \t\n]+', ' ', x).strip()

def lis(block):
    return [txt(m) for m in re.findall(r'<li\b[^>]*>((?:(?!<li|</li|<ul).)*?)</li>', block, re.S) if txt(m)]

def build(src):
    s = io.open(src, encoding='utf-8').read()
    sec = lambda name: re.search(r'<h2[^>]*>%s</h2>(.*?)</section>' % name, s, re.S).group(1)
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
    o += lis(sec('자기소개'))

    head('핵심 역량 — 전체')
    for m in re.finditer(r'<h3>(.*?)</h3>\s*<ul class="lines">(.*?)</ul>', sec('핵심 역량'), re.S):
        o.append('[%s]' % txt(m.group(1)))
        o += ['  · ' + x for x in lis(m.group(2))]
        o.append('')

    head('핵심 역량 — 칸이 좁을 때 (블록 제목만)')
    o += [txt(m) for m in re.findall(r'<h3>(.*?)</h3>', sec('핵심 역량'), re.S)]

    head('경력 사항')
    for c in sec('경력 상세').split('<div class="co">')[1:]:
        nm = re.search(r'<h3>(.*?)</h3>', c, re.S)
        if not nm: continue
        o += [rule('-'), '회사명   %s' % txt(nm.group(1))]
        for k, cls in (('기간', 'term'), ('직무', 'role')):
            v = re.search(r'<span class="%s">(.*?)</span>' % cls, c, re.S)
            if v: o.append('%s     %s' % (k, txt(v.group(1))))
        d = re.search(r'<p class="co-desc">(.*?)</p>', c, re.S)
        if d: o += ['', '설명', '  ' + txt(d.group(1))]
        b = re.search(r'<ul class="lines">(.*?)</ul>', c, re.S)
        if b: o += ['', '담당업무 및 성과'] + ['  · ' + x for x in lis(b.group(1))]
        o.append('')

    head('보유 기술')
    for m in re.finditer(r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>', sec('보유 기술'), re.S):
        o.append('[%s] %s' % (txt(m.group(1)), txt(m.group(2))))
    return '\n'.join(o).rstrip() + '\n'

if __name__ == '__main__':
    io.open(sys.argv[2], 'w', encoding='utf-8').write(build(sys.argv[1]))
