import json, sys, os, re
src_file, outdir = sys.argv[1], sys.argv[2]
d = json.loads(open(src_file).read())
nb = json.loads(d['blob']['source'])
os.makedirs(outdir, exist_ok=True)
meta = d['metadata']
json.dump(meta, open(os.path.join(outdir, 'meta.json'), 'w'), indent=1)
cells = nb.get('cells', [])
allcode = []
md = []
for i, c in enumerate(cells):
    src = c.get('source', '')
    if isinstance(src, list): src = ''.join(src)
    if c.get('cell_type') == 'code':
        allcode.append(f'# ---- cell {i} ----\n' + src)
        m = re.match(r'\s*%%writefile\s+(?:-a\s+)?(\S+)\s*\n', src)
        if m:
            fname = os.path.basename(m.group(1))
            body = src[m.end():]
            open(os.path.join(outdir, fname), 'w').write(body)
            print('wrote', fname, len(body))
    else:
        md.append(src)
open(os.path.join(outdir, 'all_code.py'), 'w').write('\n\n'.join(allcode))
open(os.path.join(outdir, 'markdown.md'), 'w').write('\n\n'.join(md))
print('cells', len(cells), 'code chars', sum(len(x) for x in allcode), 'md chars', sum(len(x) for x in md))
