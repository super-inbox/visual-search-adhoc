source ~/p014/env.sh; cd ~/p014
date -u +%FT%TZ > stage4.start
$PY -I probe/scripts/decode_baseline.py --unisign-repo $REPO --mt5 $MT5 --ckpt $CKPT --manifest probe/splits/manifest.csv --roles test_clean --zip $Z --out ~/p014/decode --device cuda > stage4.log 2>&1
echo $? > stage4.exit; date -u +%FT%TZ > stage4.end
