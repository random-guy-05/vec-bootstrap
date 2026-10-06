# Source contract

Verified **2026-10-05**. The official Virtual Embryo Challenge website and public scorer are authoritative if anything changes after this snapshot.

- Challenge overview/timeline: https://virtualembryo.ai/challenge
- Tasks and official split structure: https://virtualembryo.ai/challenge/tasks
- Data: https://virtualembryo.ai/challenge/data
- Evaluation/scoring: https://virtualembryo.ai/challenge/evaluation
- Rules and held-out-data restrictions: https://virtualembryo.ai/challenge/rules
- Community Contribution Award: https://virtualembryo.ai/challenge/community
- Public local scorer: https://github.com/aristoteleo/veckit
- PyPI scorer release used by CI/runtime docs: `veckit==0.1.2`

## Current phase facts used by these tools

P2 is active on 2026-10-01. P3 starts **2026-10-20**. At P3 start, validation ground truth is released for retraining while test ground truth remains hidden. The rules prohibit measured held-out stages/genotypes while they rank.

Official task split summary:

- T1: train E8.5/E9.5, validation E10.5, hidden test E12.5.
- T2 heart: E8.25 train, E8.5 interpolation validation, E8.75 train, E9.5 train, E10.5 extrapolation validation, E12.5 extrapolation test.
- T2 embryo: E6.75 train, E7.25 train, E7.5 validation, E7.75 test, E8.0 train.
- T3: Mab21l2 KO E9.5 released perturbation, Gata4 KO E8.75 validation, beta-catenin KO E8.75 hidden test; E8.75 WT is the matched reference.

`veckit` scores only against local files supplied by the participant. A pseudo-target is training/released data and is **not** a preview of hidden leaderboard performance.
