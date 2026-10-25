source ~/p014/env.sh; cd ~/p014
date -u +%FT%TZ > stage3.start
$PY -I probe/scripts/extract_representations.py --unisign-repo $REPO --mt5 $MT5 --ckpt $CKPT --manifest probe/splits/manifest.csv --roles probe_train,test_clean --zip $Z --out ~/p014/features --device cuda --save-seq-roles test_clean > stage3.log 2>&1
echo $? > stage3.exit; date -u +%FT%TZ > stage3.end
