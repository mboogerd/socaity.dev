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
