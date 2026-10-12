"""Challenge 050 — Compute the DPO loss.

Lesson: 120 — DPO and preference data.

    margin(y_c, y_r) = [π_θ(y_c|x) − π_ref(y_c|x)]
                     − [π_θ(y_r|x) − π_ref(y_r|x)]     (log-prob deltas)

    L = −log σ( β · margin )          σ = logistic, β default 0.1

Implement (pure Python, math module only):

  - sigmoid(z) -> float        (numerically stable for large |z|)
  - dpo_loss(policy_chosen_logp, policy_rejected_logp,
             ref_chosen_logp, ref_rejected_logp, beta=0.1) -> float

Properties the tests encode:
    all four log-probs equal            → L = ln 2   (no signal)
    margin > 0 (chosen better)          → L < ln 2
    margin grows                        → L falls toward 0
    margin < 0 (preference backwards)   → L > ln 2
    raising β sharpens: bigger β, same margin → lower loss
    reference deltas cancel: adding the same constant to policy AND
    reference logp of a response leaves L unchanged
    stability: |β·margin| = 50 must not overflow

Run:  pytest modules/05-fine-tuning/challenges/test_050_compute_dpo_loss.py -v
"""

import math


def sigmoid(z: float) -> float:
    raise NotImplementedError


def dpo_loss(
    policy_chosen_logp: float,
    policy_rejected_logp: float,
    ref_chosen_logp: float,
    ref_rejected_logp: float,
    beta: float = 0.1,
) -> float:
    raise NotImplementedError
