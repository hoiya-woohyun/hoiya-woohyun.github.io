import re, sys, html as H
A, B = '\x01', '\x02'

def txt(x):
    # 태그를 그냥 지우면 앞뒤 글자가 붙는다("프로덕트 센터웹팀 리드"). 줄바꿈과 배지는
    # 지우기 전에 공백 자리를 남긴다. 단 숫자 바로 뒤의 <small> 은 단위 접미사(8.1<small>분)
    # 이므로 띄우지 않는다 — 소속 배지(…클레온<small>프로덕트 센터)와 여기서 갈린다.
    # <em> 은 숫자 뒤에도 단위가 아니라 배지(2023.07<em>4개월)라 같은 가드를 두지 않는다.
    x = re.sub(r'<br\b[^>]*>', ' ', x)
    x = re.sub(r'(?<![0-9])<small\b[^>]*>', ' ', x)
    x = re.sub(r'<em\b[^>]*>', ' ', x)
    x = H.unescape(re.sub(r'<[^>]+>', '', x)).replace(A, '').replace(B, '')
    return re.sub(r'[ \t\n]+', ' ', x).strip()

def md(path):
    s = open(path, encoding='utf-8').read()
    # 다이어그램 SVG 는 버리기 전에 라벨과 <text> 를 한 줄로 뽑는다 — 리뷰어가 읽는
    # 추출본에 안 실리면 그 안의 사내 용어·약어가 리뷰 사각지대가 된다.
    def svg(m):
        lab = re.search(r'aria-label="([^"]*)"', m.group(0))
        ts = [txt(t) for t in re.findall(r'<text\b[^>]*>(.*?)</text>', m.group(0), re.S)]
        ts = [t for t in ts if t]
        if not lab and not ts: return ''
        head = '[다이어그램' + (': ' + H.unescape(lab.group(1)) if lab else '') + ']'
        return '<p>' + head + (' ' + ' · '.join(ts) if ts else '') + '</p>'
    s = re.sub(r'<svg\b.*?</svg>', svg, s, flags=re.S)
    s = re.sub(r'<(style|script)\b.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<nav\b.*?</nav>', '', s, flags=re.S)
    s = re.sub(r'<(\w+)[^>]*class="sitenav"[^>]*>.*?</\1>', '', s, flags=re.S)

    # 기간·배지·블록 라벨은 span/div 라 태그 제거 때 본문에 묻히거나 사라진다.
    # 리뷰어가 기간과 「문제/수행/성과」 구분을 못 보면 종결 규칙·도입부 대응을 검증할 수 없다.
    s = re.sub(r'<span class="term">(.*?)</span>', lambda m: '<p>기간: %s</p>' % txt(m.group(1)), s, flags=re.S)
    s = re.sub(r'<span class="note[^"]*">(.*?)</span>', lambda m: '<p>[배지: %s]</p>' % txt(m.group(1)), s, flags=re.S)
    s = re.sub(r'<div class="label">(.*?)</div>', lambda m: '<p>▸ %s</p>' % txt(m.group(1)), s, flags=re.S)

    # 비율 카드(.ratio): 라벨과 분수를 한 줄로. 통째로 떨어지면 예고 문장만 남아 허위 지적을 낳는다.
    s = re.sub(r'<div class="ratio">.*?<span class="lab">(.*?)</span>\s*<span class="num">(.*?)</span>.*?</div>\s*</div>\s*</div>',
               lambda m: '<p>- %s: %s</p>' % (txt(m.group(1)), txt(m.group(2))), s, flags=re.S)

    # 표
    def tb(m):
        rows, out = re.findall(r'<tr\b[^>]*>(.*?)</tr>', m.group(0), re.S), []
        for k, r in enumerate(rows):
            c = [txt(x) for x in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', r, re.S)]
            if not c: continue
            out.append('| ' + ' | '.join(c) + ' |')
            if k == 0: out.append('|' + '---|' * len(c))
        return A + '\n'.join(out) + B
    s = re.sub(r'<table\b.*?</table>', tb, s, flags=re.S)

    # 항목 라벨(b.k)은 CSS ::after 로 구분자를 넣으므로, 평문에서는 직접 붙여준다
    s = re.sub(r'<b class="k">(.*?)</b>', lambda m: '**%s** · ' % txt(m.group(1)), s, flags=re.S)
    # 인라인 강조
    s = re.sub(r'<(b|strong)\b[^>]*>(.*?)</\1>', lambda m: '**%s**' % txt(m.group(2)), s, flags=re.S)
    s = re.sub(r'<code\b[^>]*>(.*?)</code>', lambda m: '`%s`' % txt(m.group(1)), s, flags=re.S)

    # 제목 (중첩 li 안의 h3 을 먼저 빼내야 본문에 붙지 않는다)
    s = re.sub(r'<(h[1-4])\b[^>]*>(.*?)</\1>',
               lambda m: A + '\n' + '#' * int(m.group(1)[1]) + ' ' + txt(m.group(2)) + B, s, flags=re.S)
    # 정의 목록
    s = re.sub(r'<dt\b[^>]*>(.*?)</dt>\s*<dd\b[^>]*>(.*?)</dd>',
               lambda m: A + '- **%s** — %s' % (txt(m.group(1)), txt(m.group(2))) + B, s, flags=re.S)
    # 하위 지표(ul.ev)를 가진 li 는 부모와 자식을 한 번에 낸다.
    # 따로 처리하면 txt() 가 자식 마커를 지워 부모 줄로 흡수된다.
    def li_ev(m):
        out = A + '- ' + txt(m.group(1)) + B
        for i in re.findall(r'<li\b[^>]*>(.*?)</li>', m.group(2), re.S):
            if txt(i): out += A + '  - ' + txt(i) + B
        tail = txt(m.group(3))          # </ul> 뒤의 근거 주석(span.src)
        if tail: out += A + '  ' + tail + B
        return out
    # 경력기술서는 </ul> 뒤에 근거 주석이 붙으므로 꼬리를 group 3 으로 받는다
    s = re.sub(r'<li\b[^>]*>((?:(?!<li|</li|<ul).)*?)<ul class="ev">(.*?)</ul>((?:(?!</li>).)*?)</li>',
               li_ev, s, flags=re.S)
    # 중첩 없는 li 만 (바깥 li 는 안쪽 마커를 그대로 통과시킨다)
    for _ in range(4):
        s = re.sub(r'<li\b[^>]*>((?:(?!<li|</li|<ul|<ol).)*?)</li>',
                   lambda m: A + '- ' + txt(m.group(1)) + B if txt(m.group(1)) else '', s, flags=re.S)
    s = re.sub(r'<p\b[^>]*>((?:(?!<p\b).)*?)</p>',
               lambda m: A + '\n' + txt(m.group(1)) + B if txt(m.group(1)) else '', s, flags=re.S)

    out = [x for x in re.findall(A + r'(.*?)' + B, s, re.S) if x.strip()]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip() + '\n'

if __name__ == '__main__':
    open(sys.argv[2], 'w', encoding='utf-8').write(md(sys.argv[1]))
