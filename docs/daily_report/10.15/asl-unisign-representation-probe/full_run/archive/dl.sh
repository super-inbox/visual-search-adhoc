set -e
cd ~/p014/archive
for s in 00 01 02 03; do
  curl -L --fail --retry 8 --retry-all-errors -C - -o how2sign_pose_format.zip.$s https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_pose_format.zip.$s
done
ls -l how2sign_pose_format.zip.0* > sizes.txt
sha256sum how2sign_pose_format.zip.0* > sha256.txt
echo DONE > dl.done
