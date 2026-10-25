#!/usr/bin/env bash
# Rebuild the Uni-Sign error-taxonomy analysis from the restored P0-12 T4/fp16 predictions. CPU only, ~15 s.
# Needs: python3 with numpy + sacrebleu 2.x; pltrdy rouge==1.0.1 on PYTHONPATH for corpus ROUGE (verification step), e.g.
#   pip install --target /tmp/pylib rouge==1.0.1 && ROUGE_PYLIB=/tmp/pylib bash scripts/run_all.sh
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${ROUGE_PYLIB:-}${PYTHONPATH:+:$PYTHONPATH}"
python3 verify_predictions.py      # hard gate: 128 rows, order, no blanks/shifts, metrics reproduce
python3 build_inputs.py            # -> inputs_128.jsonl
python3 taxonomy.py                # -> annotations, failure_matrix, review queue, representative failures, summary
python3 validate_outputs.py        # structural / exactness / labelling-discipline checks
