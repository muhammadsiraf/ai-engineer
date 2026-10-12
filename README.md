# AI Engineering Course — Lab-First Curriculum

An original, open curriculum for software engineers moving into AI/LLM engineering:
from transformer fundamentals to production RAG, fine-tuning, vLLM serving,
evaluation/MLOps, and agents.

**Structure:** 8 modules · 114 lessons · 49 coding challenges.

## Layout

```
modules/
  01-transformer-foundations/
    lessons/NNN-slug.md          # readings (15-30 min each)
    challenges/NNN_slug.py       # do-first coding challenges (stub + TODOs)
    challenges/test_NNN_slug.py  # pytest harness per challenge
  02-using-llms-via-api/
  ...
```

## How to work through it

1. Read the lessons in numbered order. Lessons reference their paired challenges.
2. Do each challenge **before** moving on — run the tests:

```bash
pip install -r requirements.txt
pytest modules/01-transformer-foundations/challenges/test_010_bpe_merge_step.py -v
```

3. Each challenge file has function stubs with docstrings describing the task.
   Tests start skipped-fail; make them pass. Reference solutions are NOT provided —
   the tests are the spec.

## Modules

| # | Module | Lessons | Challenges |
|---|--------|---------|------------|
| 1 | How LLMs actually work | 18 | 9 |
| 2 | Using LLMs via API | 18 | 9 |
| 3 | LLM Inference & Optimization | 12 | 6 |
| 4 | Retrieval-Augmented Generation | 13 | 5 |
| 5 | Fine-Tuning & Alignment | 14 | 5 |
| 6 | Production Serving | 13 | 5 |
| 7 | Evaluation & MLOps | 13 | 5 |
| 8 | Agents & Tool Use | 13 | 5 |

## Prerequisites

- Comfortable Python (functions, classes, packaging)
- Basic ML literacy helpful for Module 1 (we build it up anyway)
- Everything runs on CPU unless noted; PyTorch exercises are small-scale
