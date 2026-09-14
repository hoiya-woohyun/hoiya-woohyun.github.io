#!/usr/bin/env python3
"""src/이력서.html + src/경력기술서.html → 채용 플랫폼 붙여넣기용 평문.

사람인·잡코리아·원티드의 자기소개·경력 칸에 그대로 붙일 수 있게, 두 문서에서
자기소개와 회사·프로젝트별 설명만 뽑아 한 파일로 합친다. 이런 칸은 마크다운을
렌더링하지 않으므로 서식 기호 없이 번호 체계로만 구조를 낸다.

  절      1. / 1.1 / 1.1.1   (문서 절 · 회사 · 프로젝트)
  항목    1) 2) 3)           (수행·성과 줄)
  하위    (1) (2)            (지표·세부)

  자기소개 · 한 줄 소개 · 보유 기술  ← 이력서
  회사 설명 · 프로젝트(문제·수행·성과) ← 경력기술서 (없는 회사는 이력서 경력 상세로 대신)

사용: python3 tools/paste.py src/이력서.html src/경력기술서.html <출력.txt>
"""
import io, re, sys, html as H
from html.parser import HTMLParser


def txt(x):
    """태그를 걷어내고 한 줄로. 굵게·코드는 서식 없이 본문에 녹인다."""
    x = re.sub(r'<br\s*/?>', ' ', x)
    x = H.unescape(re.sub(r'<[^>]+>', '', x))
    return re.sub(r'[ \t\n]+', ' ', x).strip()


class Lines(HTMLParser):
    """<ul class="lines"> 안의 li 를 (깊이, 텍스트) 목록으로. ul.ev 하위 항목은 깊이 1."""
    def __init__(self):
        super().__init__(); self.items, self.depth, self.open = [], -1, []
    def handle_starttag(self, tag, attrs):
        if tag == 'ul': self.depth += 1
        elif tag == 'li':
            self.items.append([self.depth, '']); self.open.append(len(self.items) - 1)
        elif tag == 'br' and self.open: self.items[self.open[-1]][1] += ' '
    def handle_endtag(self, tag):
        if tag == 'ul': self.depth -= 1
        elif tag == 'li' and self.open: self.open.pop()
    def handle_data(self, data):
        if self.open: self.items[self.open[-1]][1] += data
    def result(self):
        items = [(d, re.sub(r'[ \t\n]+', ' ', t).strip()) for d, t in self.items if t.strip()]
        base = min((d for d, _ in items), default=0)      # 바깥 ul 없이 li 만 받아도 최상위는 깊이 0
        return [(d - base, t) for d, t in items]


def lines(block):
    """항목은 1) 2), 하위 항목은 (1) (2) — 상위 항목이 바뀌면 하위 번호를 다시 센다."""
    p = Lines(); p.feed(block); o, n, m = [], 0, 0
    for d, t in p.result():
        if d == 0:
            n += 1; m = 0; o.append('%d) %s' % (n, t))
        else:
            m += 1; o.append('   (%d) %s' % (m, t))
    return o


def section(s, name):
    return re.search(r'<h2[^>]*>%s</h2>(.*?)</section>' % name, s, re.S).group(1)


def first(pat, s):
    m = re.search(pat, s, re.S)
    return txt(m.group(1)) if m else ''


def companies(sec):
    """경력 상세 섹션을 회사 단위로. 각 원소는 (이름, 역할, 기간, 설명, 성과 li HTML, 프로젝트 HTML 목록)."""
    out = []
    for chunk in sec.split('<div class="co">')[1:]:
        name = first(r'<h3>(.*?)</h3>', chunk)
        role = first(r'<span class="role">(.*?)</span>', chunk)
        term = first(r'<span class="term">(.*?)</span>', chunk)
        desc = first(r'<p class="co-desc">(.*?)</p>', chunk)
        co_only = chunk.split('<div class="proj">')[0]
        ul = re.search(r'<ul class="lines">(.*?)</ul>\s*</div>', co_only, re.S)
        projs = chunk.split('<div class="proj">')[1:]
        out.append((name, role, term, desc, ul.group(1) if ul else '', projs))
    return out


def project(p, num):
    o = []
    title = first(r'<h4>(.*?)</h4>', p)
    term = first(r'<span class="term">(.*?)</span>', p)
    note = first(r'<span class="note[^"]*">(.*?)</span>', p)
    meta = ' · '.join(x for x in (term, note) if x)
    o += ['%s %s%s' % (num, title, ' (%s)' % meta if meta else ''), '']
    for piece in re.sub(r'<!--.*?-->', '', p, flags=re.S).split('<div class="block">')[1:]:
        label = first(r'<div class="label">(.*?)</div>', piece)
        body = piece.split('</div>', 1)[1]          # 라벨 뒤 전부 — 닫는 태그가 섞여도 txt/Lines 가 걷어낸다
        if '<ul' in body:
            o += ['[%s]' % label] + lines(body) + ['']
        else:
            o += ['[%s] %s' % (label, txt(body)), '']
    return o


def build(resume, career):
    r = io.open(resume, encoding='utf-8').read()
    c = io.open(career, encoding='utf-8').read()
    o = []

    total = first(r'<dt>총 경력</dt>\s*<dd>(.*?)</dd>', r)
    W = 64
    o += ['=' * W, '채용 플랫폼 붙여넣기용 — 배우현',
          '자동 생성 · 원본 src/이력서.html · src/경력기술서.html · 총 경력 %s' % total, '=' * W, '',
          '· 자기소개 칸에는 「2. 자기소개」를, 경력 칸에는 회사 절(3.1, 3.2 …)을 통째로 붙여넣으세요.',
          '· 서식 기호는 없습니다. 번호(1. / 1) / (1))가 곧 계층입니다.',
          '· 「=」 선은 구분용이니 붙여넣지 마세요. 이 파일은 재생성됩니다 — 손으로 고치면 다음 make 에 사라집니다.', '']

    o += ['1. 한 줄 소개', first(r'<p class="tagline">(.*?)</p>', r), '']

    o += ['2. 자기소개']
    for i, (_, t) in enumerate(Lines_of(section(r, '자기소개')), 1):
        o.append('%d) %s' % (i, t))
    o.append('')

    o += ['3. 경력 · 프로젝트', '']
    career_by_name = {n: (role, term, desc, projs)
                      for n, role, term, desc, _, projs in companies(section(c, '경력 상세'))}
    for ci, (name, role, term, desc, ul, _) in enumerate(companies(section(r, '경력 상세')), 1):
        o += ['=' * W, '3.%d %s | %s | %s' % (ci, name, role, term), '']
        if name in career_by_name:
            _, _, cdesc, projs = career_by_name[name]
            o += [cdesc or desc, '']
            for pi, p in enumerate(projs, 1): o += project(p, '3.%d.%d' % (ci, pi))
        else:
            if desc: o += [desc, '']
            if ul: o += ['[주요 업무 및 성과]'] + lines(ul) + ['']

    o += ['=' * W, '4. 보유 기술']
    for i, m in enumerate(re.finditer(r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>', section(r, '보유 기술'), re.S), 1):
        o.append('%d) %s: %s' % (i, txt(m.group(1)), txt(m.group(2))))
    return '\n'.join(o).rstrip() + '\n'


def Lines_of(block):
    p = Lines(); p.feed(block); return p.result()


if __name__ == '__main__':
    io.open(sys.argv[3], 'w', encoding='utf-8').write(build(sys.argv[1], sys.argv[2]))
