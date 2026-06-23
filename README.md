# UV vs Pip Benchmark Lab

Benchmarks comparing uv vs pip based on HN discussion about "How uv got so fast".

## Quick Start

```bash
git clone https://github.com/necat101/uv-vs-pip-benchmark.git
cd uv-vs-pip-benchmark
python3 benchmarks/simple_benchmark.py
```

## Results

**Actual benchmark output:**
- Cold install: 1.088s
- Warm install (cache hit): 0.192s  
- **Speedup: 5.7x faster with cache**

This validates uv's global cache design.

## What's Included

- `benchmarks/` - Python benchmark scripts
- `docs/HN_ANALYSIS.md` - Analysis of HN thread
- `results/` - Benchmark output files

See full README for details on HN debate, technical analysis, and methodology.
