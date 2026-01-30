# 3-Step Setup: Stay Under 1000 Minutes/Month

## Step 1: Save the Workflow File

Create this file: `.github/workflows/tests.yml`

Copy the **entire workflow** from the "GitHub Actions Workflow" artifact I provided.

## Step 2: Save the Test Runner

Create this file: `run_tests.py`

Copy the **entire script** from the "Simple Test Runner Script" artifact.

## Step 3: Commit and Push

```bash
git add .github/workflows/tests.yml run_tests.py
git commit -m "Add optimized test workflow"
git push
```

**That's it!** ✅

---

## What This Does

### For Pull Requests (Every PR)
- ✅ Runs **5 critical tests only** (~3 minutes)
- ✅ Skips if PR is draft
- ✅ Skips if only docs changed
- 💰 **Cost:** ~180 min/month (60 PRs × 3 min)

### Weekly (Every Sunday 2 AM)
- ✅ Runs **all tests** (~25 minutes)
- ✅ Saves test history
- ✅ Detects regressions
- ✅ Creates issue if fails
- 💰 **Cost:** ~100 min/month (4 Sundays × 25 min)

### Total Monthly Usage
**~280-350 minutes** (well under 1000!) 🎉

---

## Testing It Works

### Test locally first:
```bash
# Quick test (3 min)
python run_tests.py --quick-only

# Full test (25 min)
python run_tests.py --all
```

### Test the workflow:
1. Create a draft PR → workflow should **NOT** run
2. Mark PR as "Ready for review" → workflow **should run** (quick tests)
3. Wait until Sunday → workflow **should run** (full tests)

---

## Monitoring Usage

### Check current usage:
```bash
# View the tracking file
cat .ci/monthly_minutes.txt

# It shows total minutes used this month
```

### Reset monthly (automatic):
The counter should be reset manually on the 1st of each month, or you can automate it.

---

## If You Need to Run Tests Manually

Go to Actions → "Test Suite" → "Run workflow"

Choose:
- `quick` = 5 critical tests (~3 min)
- `full` = All tests (~25 min)

---

## Customizing

### Change which tests are "critical":

Edit `run_tests.py`, find this function:

```python
def get_critical_tests():
    return [
        'mechanics_kinetic_energy',      # Change these
        'chemistry_ideal_gas_law',       # to your
        'electromagnetism_coulombs_law', # most critical
        'thermodynamics_stefan_boltzmann',
        'quantum_planck'
    ]
```

### Change weekly schedule:

Edit `.github/workflows/tests.yml`, find:

```yaml
schedule:
  - cron: '0 2 * * 0'  # Sunday 2 AM
  #           │ │ │ │
  #           │ │ │ └─ Day (0=Sunday, 1=Monday, etc)
  #           │ │ └─── Month
  #           │ └───── Day of month
  #           └─────── Hour (UTC)
```

Examples:
- `'0 2 * * 1'` = Monday
- `'0 2 * * 1,4'` = Monday and Thursday
- `'0 2 1 * *'` = 1st of every month

---

## FAQ

**Q: What if I have more than 60 PRs per month?**

A: Limit quick tests to important PRs only:
```yaml
on:
  pull_request:
    branches: [main]  # Only main branch
```

**Q: What if tests are taking longer than expected?**

A: Reduce test data size in `run_tests.py`:
```python
num_samples=200  # Change to 150 or 100
```

**Q: Can I skip the weekly tests sometimes?**

A: Yes! Just pause the workflow:
- Go to Actions → "Test Suite"
- Click "..." → "Disable workflow"
- Re-enable when needed

**Q: How do I know if I'm approaching the limit?**

A: The workflow will show a warning in the Actions log when you hit 800 minutes (80% of limit).

---

## Troubleshooting

### "Workflow doesn't run on PR"

Check:
1. Is the PR a draft? (should skip)
2. Did you only change docs? (should skip)
3. Are Python files changed? (should run)

### "Tests taking too long"

1. Check the timeout is working:
   ```yaml
   timeout-minutes: 10  # Should kill after 10 min
   ```

2. Reduce retries in `run_tests.py`:
   ```python
   max_retries=1  # Change from 3 to 1
   ```

### "Can't push tracking file"

This is normal if you don't have write permissions. You can safely ignore this error or remove the `track-usage` job entirely.

---

## Summary

✅ **Simple setup:** 2 files
✅ **Low usage:** ~300 min/month
✅ **Good coverage:** Quick tests on PRs, full tests weekly
✅ **Budget safe:** Well under 1000 min limit

You're all set! 🚀
