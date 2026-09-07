import re, sys, html as H
A, B = '\x01', '\x02'

def txt(x):
    x = H.unescape(re.sub(r'<[^>]+>', '', x)).replace(A, '').replace(B, '')
    return re.sub(r'[ \t\n]+', ' ', x).strip()

def md(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<(style|script|svg)\b.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<nav\b.*?</nav>', '', s, flags=re.S)
    s = re.sub(r'<(\w+)[^>]*class="sitenav"[^>]*>.*?</\1>', '', s, flags=re.S)

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
