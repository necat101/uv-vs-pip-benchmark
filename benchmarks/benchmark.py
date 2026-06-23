#!/usr/bin/env python3
"""
UV vs Pip Benchmark - Fair Comparison
Tests both tools under comparable conditions to validate HN article claims.

Based on: https://news.ycombinator.com/item?id=46393992
Article: https://nesbitt.io/2025/12/26/how-uv-got-so-fast.html
"""

import subprocess
import time
import json
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Test packages - mix of pure Python wheels
TEST_PACKAGES = [
    "requests==2.31.0",
    "click==8.1.7",
    "pyyaml==6.0.1",
]

def run_command(cmd, env=None, cwd=None):
    """Run command and return (duration, success, output)"""
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env=env,
            cwd=cwd,
            timeout=180
        )
        duration = time.time() - start
        return duration, result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 180.0, False, "TIMEOUT"
    except Exception as e:
        return time.time() - start, False, str(e)

def clear_caches():
    """Clear pip and uv caches"""
    subprocess.run("pip cache purge 2>/dev/null", shell=True)
    subprocess.run("uv cache clean 2>/dev/null", shell=True)

def test_uv_install(tmpdir, packages, use_cache=True):
    """Test uv install"""
    venv_path = tmpdir / f"uv-test-{'warm' if use_cache else 'cold'}"
    
    # Create venv
    duration, success, _ = run_command(f"uv venv {venv_path}")
    if not success:
        return None
    
    # Install packages
    cache_dir = tmpdir / "uv-cache"
    env = {
        **os.environ,
        "VIRTUAL_ENV": str(venv_path),
        "UV_CACHE_DIR": str(cache_dir)
    }
    
    if not use_cache and cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    cmd = f"uv pip install {' '.join(packages)}"
    duration, success, output = run_command(cmd, env=env)
    
    return {
        "duration": round(duration, 3),
        "success": success,
        "cache_used": use_cache and cache_dir.exists()
    }

def test_pip_install(tmpdir, packages, use_cache=True):
    """Test pip install (requires venv support)"""
    venv_path = tmpdir / f"pip-test-{ 'warm' if use_cache else 'cold'}"
    
    # Try to create venv - may fail if python3-venv not installed
    duration, success, output = run_command(f"python3 -m venv {venv_path}")
    if not success:
        return {
            "duration": 0,
            "success": False,
            "error": "python3-venv not available",
            "skipped": True
        }
    
    pip_path = venv_path / "bin" / "pip"
    
    # Install packages
    cache_flag = "" if use_cache else "--no-cache-dir"
    cmd = f"{pip_path} install {cache_flag} {' '.join(packages)}"
    duration, success, output = run_command(cmd)
    
    return {
        "duration": round(duration, 3),
        "success": success,
        "cache_used": use_cache
    }

def main():
    print("=" * 70)
    print("UV vs PIP Benchmark - Fair Comparison")
    print("=" * 70)
    print()
    print("Testing based on HN discussion:")
    print("https://news.ycombinator.com/item?id=46393992")
    print()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "packages": TEST_PACKAGES,
        "system_info": {
            "python": subprocess.getoutput("python3 --version"),
            "pip": subprocess.getoutput("pip --version 2>/dev/null | cut -d' ' -f2"),
            "uv": subprocess.getoutput("uv --version 2>/dev/null | cut -d' ' -f2"),
        },
        "tests": {}
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Clear caches for cold tests
        print("Clearing caches for cold tests...")
        clear_caches()
        print()
        
        # Test 1: Cold installs
        print("Test 1: Cold installs (no cache)")
        print("-" * 70)
        
        uv_cold = test_uv_install(tmpdir, TEST_PACKAGES, use_cache=False)
        print(f"  uv:  {uv_cold['duration']}s - {'✓' if uv_cold['success'] else '✗'}")
        
        pip_cold = test_pip_install(tmpdir, TEST_PACKAGES, use_cache=False)
        if pip_cold.get("skipped"):
            print(f"  pip: SKIPPED - {pip_cold['error']}")
        else:
            print(f"  pip: {pip_cold['duration']}s - {'✓' if pip_cold['success'] else '✗'}")
        
        results["tests"]["cold_install"] = {
            "uv": uv_cold,
            "pip": pip_cold
        }
        print()
        
        # Test 2: Warm installs
        print("Test 2: Warm installs (with cache)")
        print("-" * 70)
        
        uv_warm = test_uv_install(tmpdir, TEST_PACKAGES, use_cache=True)
        print(f"  uv:  {uv_warm['duration']}s - {'✓' if uv_warm['success'] else '✗'}")
        
        pip_warm = test_pip_install(tmpdir, TEST_PACKAGES, use_cache=True)
        if pip_warm.get("skipped"):
            print(f"  pip: SKIPPED - {pip_warm['error']}")
        else:
            print(f"  pip: {pip_warm['duration']}s - {'✓' if pip_warm['success'] else '✗'}")
        
        results["tests"]["warm_install"] = {
            "uv": uv_warm,
            "pip": pip_warm
        }
        print()
        
        # Calculate speedups
        if uv_cold["success"] and uv_warm["success"]:
            uv_speedup = uv_cold["duration"] / max(uv_warm["duration"], 0.001)
            print(f"uv warm vs cold: {uv_speedup:.1f}x faster")
        
        if (not pip_cold.get("skipped") and pip_cold["success"] and 
            not pip_warm.get("skipped") and pip_warm["success"]):
            pip_speedup = pip_cold["duration"] / max(pip_warm["duration"], 0.001)
            print(f"pip warm vs cold: {pip_speedup:.1f}x faster")
        
        if (uv_cold["success"] and not pip_cold.get("skipped") and 
            pip_cold["success"]):
            vs_pip = pip_cold["duration"] / max(uv_cold["duration"], 0.001)
            print(f"uv vs pip (cold): {vs_pip:.1f}x {'faster' if vs_pip > 1 else 'slower'}")
    
    # Save results
    results_file = RESULTS_DIR / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print()
    print("=" * 70)
    print(f"Results saved to: {results_file}")
    print("=" * 70)
    print()
    print("Notes:")
    print("- This benchmark tests cache effectiveness, not resolver performance")
    print("- For fair comparison, both tools use fresh virtual environments")
    print("- Network conditions affect cold install times significantly")
    print("- See README.md for full methodology and limitations")

if __name__ == "__main__":
    main()
