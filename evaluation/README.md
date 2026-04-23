# Evaluation Dataset Architecture

This folder is reserved for system-effect evaluation data and reports.

The planned GitHub-derived pipeline is:

1. Select trusted repositories by stars, activity, and domain relevance.
2. Harvest closed Issues and answered Discussions with high-signal replies.
3. Normalize each problem and answer into Markdown knowledge documents.
4. Generate deterministic evaluation cases from the same provenance.
5. Run RAG, Agent, and Tool metrics against the generated cases.

Current scaffold supports offline sample generation:

```bash
python scripts/build_github_dataset.py --sample
```

Real GitHub harvesting should use `GITHUB_TOKEN`, rate-limit tracking, provenance metadata, and manual review gates before data enters the benchmark set.
