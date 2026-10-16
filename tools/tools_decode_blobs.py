"""Safely extract embedded agent sources from notebook code without executing it.
Finds string literals (or ''.join((...)) of literals / base64.b64decode('...') calls) and tries
decoding them as base85+zlib, base64+gzip(tar), base64+zlib, base64 plain python."""
import ast, base64, zlib, gzip, io, tarfile, sys, os, hashlib

def literal_strings(tree):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            val = node.value
            s = None
            try:
                if isinstance(val, ast.Constant) and isinstance(val.value, (str, bytes)):
                    s = val.value
                elif isinstance(val, ast.Call):
                    # ''.join((...)) or base64.b64decode('...') etc
                    f = val.func
                    if isinstance(f, ast.Attribute) and f.attr == 'join' and val.args:
                        arg = val.args[0]
                        if isinstance(arg, (ast.Tuple, ast.List)):
                            parts = [ast.literal_eval(e) for e in arg.elts]
                            s = ''.join(parts)
                    elif val.args and isinstance(val.args[0], ast.Constant) and isinstance(val.args[0].value, (str, bytes)):
                        s = val.args[0].value
                    elif val.args and isinstance(val.args[0], ast.Call):
                        inner = val.args[0]
                        if inner.args and isinstance(inner.args[0], ast.Constant):
                            s = inner.args[0].value
            except Exception:
                s = None
            if isinstance(s, (str, bytes)) and len(s) > 2000:
                out.append((names, s))
    return out

def try_decode(s):
    if isinstance(s, str):
        b = s.encode()
    else:
        b = s
    results = []
    for name, fn in [
        ('b85zlib', lambda x: zlib.decompress(base64.b85decode(x))),
        ('b64gzip', lambda x: gzip.decompress(base64.b64decode(x))),
        ('b64zlib', lambda x: zlib.decompress(base64.b64decode(x))),
        ('b64', lambda x: base64.b64decode(x, validate=True)),
        ('b85', lambda x: base64.b85decode(x)),
    ]:
        try:
            r = fn(b)
            results.append((name, r))
            break
        except Exception:
            continue
    return results

def main(src_py, outdir):
    code = open(src_py).read()
    cells = code.split('# ---- cell ')
    os.makedirs(outdir, exist_ok=True)
    found = 0
    for ci, c in enumerate(cells):
        body = c.split('\n', 1)[1] if '\n' in c else ''
        # strip ipython magics
        lines = [l for l in body.split('\n') if not l.lstrip().startswith(('%', '!'))]
        try:
            tree = ast.parse('\n'.join(lines))
        except SyntaxError as e:
            continue
        for names, s in literal_strings(tree):
            for kind, data in try_decode(s):
                # tar?
                try:
                    tf = tarfile.open(fileobj=io.BytesIO(data))
                    for m in tf.getmembers():
                        if m.isfile():
                            fb = tf.extractfile(m).read()
                            p = os.path.join(outdir, os.path.basename(m.name))
                            open(p, 'wb').write(fb)
                            print(f'cell{ci} {names} {kind} tar-> {m.name} {len(fb)} sha={hashlib.sha256(fb).hexdigest()[:12]}')
                            found += 1
                    continue
                except Exception:
                    pass
                # maybe gzip inside
                try:
                    data2 = gzip.decompress(data)
                    tf = tarfile.open(fileobj=io.BytesIO(data2))
                    for m in tf.getmembers():
                        if m.isfile():
                            fb = tf.extractfile(m).read()
                            p = os.path.join(outdir, os.path.basename(m.name))
                            open(p, 'wb').write(fb)
                            print(f'cell{ci} {names} {kind}+gz tar-> {m.name} {len(fb)}')
                            found += 1
                    continue
                except Exception:
                    pass
                nm = (names[0] if names else f'blob{ci}') + '.bin'
                if data[:200].lstrip().startswith((b'#', b'import', b'"""', b'from', b"'''")) or b'def agent' in data[:200000]:
                    nm = (names[0] if names else f'blob{ci}') + '.py'
                open(os.path.join(outdir, nm), 'wb').write(data)
                print(f'cell{ci} {names} {kind} -> {nm} {len(data)}')
                found += 1
    print('found', found)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
