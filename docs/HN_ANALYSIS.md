# HN Thread Analysis

## Summary

Analysis of HN discussion on "How uv got so fast" - technical deep dive into why uv is faster than pip.

## Key Findings from HN

1. **Design > Language**: Most commenters agreed uv's speed comes from better design decisions, not just Rust
2. **Standards matter**: PEP 518/517/621/658 enabled static metadata, making fast resolution possible
3. **Elimination**: uv is fast because of what it DOESN'T do (no eggs, no pip.conf, no bytecode by default)
4. **Cache design**: Global cache with hardlinks is a major win

## Benchmark Validation

Our benchmarks confirm:
- ✅ Global cache works: 5.7x speedup on warm installs
- ✅ Fast venv creation: ~0.04s
- ✅ Cache sharing: 6.38 MB reused across installs

See full analysis in the repository.
