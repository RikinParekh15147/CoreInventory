import json

try:
    with open('django_error.html', 'r', encoding='utf-8') as f:
        html = f.read()
except UnicodeDecodeError:
    with open('django_error.html', 'r', encoding='utf-16') as f:
        html = f.read()

import re
frames = re.findall(r'<span class="fname">([^<]+)</span>, line <span class="lineno">(\d+)</span>, in <span class="funcName">([^<]+)</span>', html)

with open('trace_frames.txt', 'w', encoding='utf-8') as out:
    if frames:
        for f in frames[-30:]:
            out.write(f'File {f[0]}, line {f[1]}, in {f[2]}\n')
    else:
        out.write('No frames found\n')
