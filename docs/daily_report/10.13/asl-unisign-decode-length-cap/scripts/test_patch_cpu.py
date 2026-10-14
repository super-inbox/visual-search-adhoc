# CPU self-test of patch/fine_tuning_decode_length.patch (no model, no GPU).
#   1. the patch applies cleanly to the pinned upstream fine_tuning.py and yields the recorded patched sha256
#   2. the padding safeguard never changes decoded text: for outputs <= 150 ids it builds the same tensor as upstream;
#      for longer outputs (where upstream raises) the text equals decoding with no extra padding at all
#   3. the diagnostic parser reports EOS / generated-token count / cap hit correctly on generate()-shaped id rows
# The padding and diag expressions below are asserted to appear verbatim in the patched file, so this test cannot drift.
# Usage: python -I test_patch_cpu.py <pristine upstream fine_tuning.py> <mt5-base tokenizer dir>
import os, subprocess, sys, tempfile, shutil, hashlib, random
import torch
from torch.nn.utils.rnn import pad_sequence
from transformers import AutoTokenizer

HERE = os.path.dirname(os.path.abspath(__file__))
PATCH = os.path.join(HERE, '..', 'patch', 'fine_tuning_decode_length.patch')
UP_SHA = '3249a0aa642258779b1a70ace78c74c1fcc58b3ab7470397ea1890702c9528af'
PATCHED_SHA = 'f13e168967c974fc690a1a8393326b5aeceb1e3aaba91521953687ee7fed99bc'
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()

up, tokdir = sys.argv[1:3]
assert sha(up) == UP_SHA, 'not the pinned upstream fine_tuning.py'
tmp = tempfile.mkdtemp()
shutil.copy(up, os.path.join(tmp, 'fine_tuning.py'))
subprocess.run(['git', 'init', '-q'], cwd=tmp, check=True)
subprocess.run(['git', 'apply', os.path.abspath(PATCH)], cwd=tmp, check=True)
patched = open(os.path.join(tmp, 'fine_tuning.py')).read()
assert sha(os.path.join(tmp, 'fine_tuning.py')) == PATCHED_SHA, 'patched sha256 mismatch'
NEW_PAD = 'torch.ones(max(150, max(len(t) for t in tgt_pres))-len(tgt_pres[0]))'
for frag in [NEW_PAD, "max_new_tokens=UNISIGN_MAX_NEW_TOKENS", "ids = t.tolist(); gen = ids[1:]",
             "n = gen.index(tokenizer.eos_token_id) if eos else len(gen)",
             "'hit_cap': (not eos) and len(gen) >= UNISIGN_MAX_NEW_TOKENS", "num_beams = 4,"]:
    assert frag in patched, frag
assert 'max_new_tokens=100' not in patched and 'torch.ones(150-len(tgt_pres[0]))' not in patched
print('1. patch applies; patched sha256 OK')

tok = AutoTokenizer.from_pretrained(tokdir, legacy=True)
EOS, PAD = tok.eos_token_id, tok.pad_token_id
words = 'we are going to take the ring and rub it here because it is a good idea you know'.split()
rnd = random.Random(0)


def fake_batch(n_new_list, max_new):
    """generate()-shaped rows: [decoder_start=0] + ids (+EOS if finished) padded with pad=0 to the batch max length."""
    rows = []
    for n in n_new_list:
        ids = []
        while len(ids) < n:
            ids += tok(' '.join(rnd.choices(words, k=8)), add_special_tokens=False)['input_ids']
        ids = ids[:n]
        rows.append([0] + ids + ([EOS] if n < max_new else []))
    L = max(map(len, rows))
    return [torch.tensor(r + [PAD] * (L - len(r))) for r in rows]


def decode_upstream(tgt_pres):
    tgt_pres = list(tgt_pres)
    pad_tensor = torch.ones(150 - len(tgt_pres[0])) * EOS
    tgt_pres[0] = torch.cat((tgt_pres[0], pad_tensor.long()), dim=0)
    return tok.batch_decode(pad_sequence(tgt_pres, batch_first=True, padding_value=EOS), skip_special_tokens=True)


def decode_patched(tgt_pres):
    tgt_pres = list(tgt_pres)
    pad_tensor = torch.ones(max(150, max(len(t) for t in tgt_pres))-len(tgt_pres[0])) * EOS
    tgt_pres[0] = torch.cat((tgt_pres[0], pad_tensor.long()), dim=0)
    return tok.batch_decode(pad_sequence(tgt_pres, batch_first=True, padding_value=EOS), skip_special_tokens=True)


def decode_plain(tgt_pres):
    return [tok.decode(t, skip_special_tokens=True) for t in tgt_pres]


def diag(tgt_pres, max_new):
    out = []
    for t in tgt_pres:
        ids = t.tolist(); gen = ids[1:]
        eos = EOS in gen
        n = gen.index(EOS) if eos else len(gen)
        out.append({'eos': eos, 'n_gen_tokens': n, 'hit_cap': (not eos) and len(gen) >= max_new})
    return out


n_cases = 0
for max_new in (100, 150, 256):
    for _ in range(40):
        lens = [rnd.randint(1, max_new) for _ in range(8)]
        if rnd.random() < 0.3: lens[0] = max_new  # first row hits the cap (the row upstream pads)
        b = fake_batch(lens, max_new)
        p = decode_patched(b)
        assert p == decode_plain(b), 'patched padding changed decoded text'
        if max(len(t) for t in b) <= 150:  # upstream works here and must be identical
            assert p == decode_upstream(b)
        else:
            try:
                decode_upstream(b); upstream_ok = True
            except RuntimeError:
                upstream_ok = False
            assert not upstream_ok or len(b[0]) <= 150
        for d, n in zip(diag(b, max_new), lens):
            assert d['hit_cap'] == (n == max_new) and d['eos'] == (n < max_new) and d['n_gen_tokens'] == n
        n_cases += 1
print(f'2/3. {n_cases} synthetic batches: padding safeguard text-identical (== upstream wherever upstream runs); '
      'diag EOS / token count / cap-hit correct')
b = fake_batch([256] + [10] * 7, 256)
try:
    decode_upstream(b); print('note: upstream did not fail on a 257-id first row')
except RuntimeError as e:
    print(f'   confirmed: upstream padding raises on a 257-id first row ({type(e).__name__}); patched decodes it')
shutil.rmtree(tmp)
print('PASS')
