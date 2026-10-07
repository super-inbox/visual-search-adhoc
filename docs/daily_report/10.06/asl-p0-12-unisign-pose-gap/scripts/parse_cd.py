import struct, sys, json, csv
cd = open(sys.argv[1], 'rb').read()
manifest = sys.argv[2]
out = sys.argv[3]
ents = []
p = 0
while p < len(cd) and cd[p:p+4] == b'PK\x01\x02':
    (sig, vmade, vneed, flag, meth, mt, md, crc, csz, usz, nlen, elen, clen, dstart, iattr, eattr, lho) = struct.unpack('<IHHHHHHIIIHHHHHII', cd[p:p+46])
    name = cd[p+46:p+46+nlen].decode('utf-8', 'replace')
    extra = cd[p+46+nlen:p+46+nlen+elen]
    q = 0
    while q < len(extra):
        hid, hsz = struct.unpack('<HH', extra[q:q+4]); body = extra[q+4:q+4+hsz]
        if hid == 1:
            vals = []; k = 0
            for fld in ('usz', 'csz', 'lho'):
                cur = {'usz': usz, 'csz': csz, 'lho': lho}[fld]
                if cur == 0xFFFFFFFF:
                    v = struct.unpack('<Q', body[k:k+8])[0]; k += 8
                    if fld == 'usz': usz = v
                    elif fld == 'csz': csz = v
                    else: lho = v
        q += 4 + hsz
    ents.append(dict(name=name, method=meth, csz=csz, usz=usz, lho=lho, nlen=nlen))
    p += 46 + nlen + elen + clen
print('entries parsed', len(ents))
dirs = {}
for e in ents:
    top = '/'.join(e['name'].split('/')[:-1]); dirs[top] = dirs.get(top, 0) + 1
print('dirs', dirs)
ids = [r['how2sign_id'] for r in csv.DictReader(open(manifest))]
byname = {e['name'].split('/')[-1]: e for e in ents}
hit = {}
for cid in ids:
    cands = [e for e in ents if e['name'].endswith('/' + cid + '.pkl')]
    hit[cid] = cands
cov = sum(1 for v in hit.values() if v)
print('coverage of 128:', cov, 'missing:', [k for k, v in hit.items() if not v])
sel = {k: v[0] for k, v in hit.items() if v}
print('splits for hits:', set(v['name'].split('/')[-2] for v in sel.values()))
print('total compressed bytes for 128:', sum(v['csz'] for v in sel.values()), 'uncompressed', sum(v['usz'] for v in sel.values()))
print('methods', set(v['method'] for v in sel.values()))
json.dump(sel, open(out, 'w'), indent=1)
