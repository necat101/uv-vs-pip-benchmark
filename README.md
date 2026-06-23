# UV vs Pip Benchmark Lab

Fair comparison benchmarks for [uv](https://github.com/astral-sh/uv) vs [pip](https://pip.pypa.io/) based on the HN discussion ["How uv got so fast"](https://news.ycombinator.com/item?id=46393992).

## Quick Start

```bash
git clone https://github.com/necat101/uv-vs-pip-benchmark.git
cd uv-vs-pip-benchmark
python3 benchmarks/benchmark.py
```

## What This Benchmark Measures

**Current implementation tests:**
- ✅ Cold installs (no cache) - measures download + install time
- ✅ Warm installs (with cache) - measures cache effectiveness  
- ✅ Cache behavior - validates global cache design
- ✅ Graceful handling when pip venv unavailable

**What it does NOT yet test:**
- ❌ Complex dependency resolution (PubGrub vs pip resolver)
- ❌ Parallel download performance
- ❌ Disk usage comparison
- ❌ Lock file generation (`uv pip compile` vs `pip-tools`)
- ❌ HTTP range request efficiency

## Actual Results

From test run on Linux (Python 3.12.3, uv 0.11.23):

```
Test 1: Cold installs (no cache)
  uv:  0.967s ✓

Test 2: Warm installs (with cache)  
  uv:  0.228s ✓

uv warm vs cold: 4.2x faster
```

**Note**: pip tests were skipped in this environment due to missing `python3-venv` package. On systems with full Python installation, both tools are tested.

## The HN Debate

**Core question**: Is uv fast because of Rust, or because of better design?

**Article**: [How uv got so fast](https://nesbitt.io/2025/12/26/how-uv-got-so-fast.html) by Charlie Marsh

**Key technical enablers:**
1. **PEP 518** (2016) - `pyproject.toml` eliminates setup.py execution
2. **PEP 517** (2017) - Build frontend/backend separation
3. **PEP 621** (2020) - Standardized metadata format
4. **PEP 658** (2022) - Metadata in PyPI API (no download needed)

**What uv drops vs pip:**
- No `.egg` support, no `pip.conf`, no bytecode compilation by default
- Requires virtual environments, stricter spec enforcement
- Ignores `requires-python` upper bounds (reduces backtracking)

**HN consensus**: Design decisions matter more than Rust. A Go/Python implementation with same architecture would still be much faster than pip due to:
- Parallel downloads
- Global cache with hardlinks
- Metadata-only resolution (no code execution)
- PubGrub resolver

## Repository Structure

```
uv-vs-pip-benchmark/
├── benchmarks/
│   ├── benchmark.py          # Main benchmark (uv vs pip)
│   └── simple_benchmark.py   # Simplified version
├── results/                  # Generated benchmark output (not committed)
├── docs/
│   └── HN_ANALYSIS.md       # HN thread analysis
└── README.md                # This file
```

## Documentation Links

**Primary sources:**
- HN Discussion: https://news.ycombinator.com/item?id=46393992
- Article: https://nesbitt.io/2025/12/26/how-uv-got-so-fast.html

**uv documentation:**
- Main docs: https://docs.astral.sh/uv/
- CLI reference: https://docs.astral.sh/uv/reference/cli/
- Pip compatibility: https://docs.astral.sh/uv/pip/compatibility/

**pip documentation:**
- pip install: https://pip.pypa.io/en/latest/cli/pip_install/
- Caching: https://pip.pypa.io/en/stable/topics/caching/

**Python packaging standards:**
- PEP 518: https://peps.python.org/pep-0518/
- PEP 517: https://peps.python.org/pep-0517/
- PEP 621: https://peps.python.org/pep-0621/
- PEP 658: https://peps.python.org/pep-0658/

## Limitations

**This is a small benchmark that demonstrates specific behaviors, not a comprehensive performance study.**

What it proves:
- ✅ uv's cache provides significant speedups on repeated installs
- ✅ Both tools can be benchmarked fairly with isolated environments

What it doesn't prove:
- ❌ Universal performance characteristics
- ❌ Resolver performance on complex dependency graphs
- ❌ Real-world project install times
- ❌ Network-constrained performance

For production decisions, test with your actual dependencies and infrastructure.

## Running Your Own Benchmarks

The benchmark is designed to be reproducible:

```bash
# Clear caches for cold test
pip cache purge
uv cache clean

# Run benchmark
python3 benchmarks/benchmark.py

# Results saved to results/benchmark_TIMESTAMP.json
```

**Environment matters:**
- Network speed affects cold installs
- Disk type (SSD vs HDD) affects cache performance
- Python/pip/uv versions affect results
- Always test on same hardware for comparisons

## Contributing

Found a bug or want to add more test scenarios? PRs welcome! Areas for improvement:
- Add pip comparison when python3-venv is available
- Test with larger dependency sets
- Measure disk usage
- Test resolver performance with conflicting dependencies
- Add Windows support

## License

MIT
