# Decomposition evaluation corpus

This is a small, reviewable M1 regression corpus. Each fixture records a
publicly inspectable project/issue or project/PR reference and the
retrospectively reconstructed need, competing approaches, and dependencies.
The labels are stable evaluation keys; the candidate may use any prose, but it
must preserve the same structure.

Run the structural report with:

```sh
python3 tools/eval/decomposition.py
```

The harness deliberately does not call a model. A model runner writes one JSON
prediction map per run, then this tool scores it. Use `--runs` for inter-run
variance and `--write-judge-prompt` to produce the bounded LLM-judge prompt.
Judge output is a separately reviewable annotation and cannot override the
structural metrics.

## Similarity calibration

`calibration.json` is a small, versioned repeated-ingestion corpus. Every pair
has a hand-reviewed duplicate label, a source reference, and either an exact
external-reference match or a fixed semantic similarity score. The exact match
is accepted first; semantic pairs become duplicate proposals when their score
meets a threshold.

Run the threshold report with:

```sh
python3 tools/eval/decomposition.py \
  --calibration-corpus evals/decomposition/calibration.json
```

For each threshold, `duplicate_rate` is recall over labelled duplicates and
`false_merge_rate` is the fraction of labelled non-duplicates proposed as
merges. The default selection rule chooses the highest duplicate rate with a
false-merge rate at most 10%, breaking ties toward the higher threshold. The
fixture's provenance and the rule are emitted in the report, so changing the
corpus or scorer requires a new version and review rather than silently moving
the band.
