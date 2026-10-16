import json, sys, os, re, subprocess
src_file, outdir = sys.argv[1], sys.argv[2]
d = json.loads(open(src_file).read())
os.makedirs(outdir, exist_ok=True)
meta = d['metadata']
json.dump(meta, open(os.path.join(outdir, 'meta.json'), 'w'), indent=1)
src = d['blob']['source']
if meta.get('kernel_type') == 'script' or not src.lstrip().startswith('{'):
    open(os.path.join(outdir, 'all_code.py'), 'w').write('# ---- cell 0 ----\n' + src)
    open(os.path.join(outdir, 'markdown.md'), 'w').write('')
    print('script kernel', len(src))
else:
    nb = json.loads(src)
    cells = nb.get('cells', [])
    allcode, md = [], []
    for i, c in enumerate(cells):
        s = c.get('source', '')
        if isinstance(s, list): s = ''.join(s)
        if c.get('cell_type') == 'code':
            allcode.append(f'# ---- cell {i} ----\n' + s)
            m = re.match(r'\s*%%writefile\s+(?:-a\s+)?(\S+)\s*\n', s)
            if m:
                fname = os.path.basename(m.group(1))
                open(os.path.join(outdir, fname), 'w').write(s[m.end():])
                print('writefile', fname, len(s) - m.end())
        else:
            md.append(s)
    open(os.path.join(outdir, 'all_code.py'), 'w').write('\n\n'.join(allcode))
    open(os.path.join(outdir, 'markdown.md'), 'w').write('\n\n'.join(md))
    print('notebook cells', len(cells))
subprocess.run([sys.executable, 'tools_decode_blobs.py', os.path.join(outdir, 'all_code.py'), os.path.join(outdir, 'extracted')])
