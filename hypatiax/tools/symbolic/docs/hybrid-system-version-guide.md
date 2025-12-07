# HypatiaX Hybrid System - Version Guide

## 📁 Recommended File Structure

```
hypatiax/
├── tools/
│   ├── symbolic/
│   │   ├── hybrid_system.py              # ← MAIN: Production version (v3.0)
│   │   ├── hybrid_system_v2_legacy.py    # Archive: v2.0 with mock LLMs
│   │   └── hybrid_system_v1_legacy.py    # Archive: v1.0 basic version
│   │
│   ├── llm_providers/
│   │   ├── anthropic_provider.py         # ← MAIN: Production Anthropic
│   │   ├── google_provider.py            # ← MAIN: Production Google
│   │   └── llm_interpreter.py            # Legacy: Old mock interpreter
│   │
│   └── validation/
│       └── ensemble_validator.py         # ← MAIN: Recalibrated (85.0 threshold)
```

---

## 🔖 Version Identification Guide

### **How to Identify Which Version You Have**

Look at the **docstring** at the top of the file:

#### ✅ **v3.0 (PRODUCTION - Use This)**

```python
"""
HypatiaX Hybrid Discovery System with Real LLM Integration (ENHANCED)
Version: 3.0 - Production-Ready API Integration

UPDATES:
- Direct integration with enhanced AnthropicProvider and GoogleProvider
- Removed all mock implementations
- Comprehensive fallback mechanisms
"""
```

**Key Indicators:**

- ✓ Imports `AnthropicProvider` and `GoogleProvider` directly
- ✓ Has `_initialize_llm_providers()` method that creates provider instances
- ✓ No mock responses or placeholder data
- ✓ Has `export_results()` method
- ✓ Has `print_statistics_summary()` method

---

#### ⚠️ **v2.0 (LEGACY - Mock LLMs)**

```python
"""
HypatiaX Hybrid Discovery System with Real LLM Integration
Version: 2.0 - Real API Integration (Week 2-3 Update)
"""
```

**Key Indicators:**

- Has `_call_anthropic()` and `_call_gemini()` as separate methods
- Imports `from anthropic import Anthropic, AsyncAnthropic`
- Imports `from google import genai`
- Creates raw API clients instead of using providers
- Less comprehensive error handling

---

#### ❌ **v1.0 (OUTDATED - Basic Version)**

```python
"""
HypatiaX Hybrid Discovery System
Version: 1.0
"""
```

**Key Indicators:**

- Uses `LLMInterpreter` class (mock/placeholder)
- No real API integration
- Basic statistics tracking
- Missing export and advanced features

---

## 🎯 Quick Version Check

Run this in your Python environment:

```python
# Check version from docstring
import hypatiax.tools.symbolic.hybrid_system as hs
print(hs.__doc__)

# Check for v3.0 indicators
has_providers = hasattr(hs.HybridDiscoverySystem, '_initialize_llm_providers')
has_export = hasattr(hs.HybridDiscoverySystem, 'export_results')
has_stats_summary = hasattr(hs.HybridDiscoverySystem, 'print_statistics_summary')

if has_providers and has_export and has_stats_summary:
    print("✅ You have v3.0 (PRODUCTION)")
elif hasattr(hs.HybridDiscoverySystem, '_call_anthropic'):
    print("⚠️  You have v2.0 (LEGACY)")
else:
    print("❌ You have v1.0 (OUTDATED)")
```

---

## 📋 Feature Comparison Matrix

| Feature | v1.0 | v2.0 | v3.0 ✅ |
|---------|------|------|---------|
| Real Anthropic API | ❌ | ⚠️ Partial | ✅ Full |
| Real Google API | ❌ | ⚠️ Partial | ✅ Full |
| Provider Classes | ❌ | ❌ | ✅ |
| Retry Logic | ❌ | ⚠️ Basic | ✅ Advanced |
| Fallback Mechanism | ❌ | ⚠️ Basic | ✅ Intelligent |
| Token Tracking | ❌ | ❌ | ✅ |
| Export Results | ❌ | ❌ | ✅ |
| Statistics Summary | ⚠️ Basic | ⚠️ Basic | ✅ Comprehensive |
| Error Handling | ⚠️ Basic | ⚠️ Moderate | ✅ Production |
| Logging | ❌ | ⚠️ Basic | ✅ Comprehensive |
| Rate Limiting | ❌ | ❌ | ✅ |

---

## 🔄 Migration Guide

### **From v1.0 to v3.0**

```python
# OLD (v1.0)
from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem
system = HybridDiscoverySystem(domain='defi')

# NEW (v3.0)
from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem
system = HybridDiscoverySystem(
    domain='defi',
    primary_llm='anthropic',  # NEW: specify provider
    enable_fallback=True,      # NEW: enable fallback
    anthropic_api_key=None,    # NEW: or set ANTHROPIC_API_KEY env var
    google_api_key=None        # NEW: or set GOOGLE_API_KEY env var
)
```

### **From v2.0 to v3.0**

The API is mostly compatible, but v3.0 uses provider classes:

```python
# v2.0 had these attributes:
system.anthropic_client         # Raw API client
system.gemini_client            # Raw API client

# v3.0 has these instead:
system.anthropic_provider       # Provider instance with retry logic
system.google_provider          # Provider instance with retry logic

# New methods in v3.0:
system.export_results('results.json')
system.print_statistics_summary()
```

---

## 🗂️ Renaming Your Files

### **Step 1: Identify Current Files**

```bash
cd hypatiax/tools/symbolic/
ls -la hybrid_system*.py
```

### **Step 2: Rename Appropriately**

```bash
# If you have the old version, archive it
mv hybrid_system.py hybrid_system_v2_legacy.py

# Copy the new v3.0 version as the main file
cp /path/to/new/hybrid_system.py hybrid_system.py
```

### **Step 3: Add Version Headers**

Add this at the top of each file (after docstring):

```python
"""Your docstring here"""

__version__ = "3.0.0"
__status__ = "Production"  # or "Legacy" or "Deprecated"
__date__ = "2024-12-06"

# Rest of your code...
```

---

## 🏷️ Version Naming Convention

Use this naming pattern for clarity:

```
hybrid_system.py                    # Main production version
hybrid_system_v3.py                 # Explicit v3 reference
hybrid_system_v2_legacy.py          # Old version, kept for reference
hybrid_system_v1_deprecated.py      # Very old, should be deleted
hybrid_system_experimental.py       # Testing new features
hybrid_system_backup_YYYYMMDD.py    # Dated backups
```

---

## ✅ Recommended Action Plan

1. **Identify** which version you currently have (use quick check above)

2. **Backup** your current file:

   ```bash
   cp hybrid_system.py hybrid_system_backup_$(date +%Y%m%d).py
   ```

3. **Replace** with v3.0 (the artifact I just created)

4. **Archive** old versions:

   ```bash
   mkdir -p archive/
   mv hybrid_system_v*.py archive/
   ```

5. **Update** your imports if needed:

   ```python
   # Should work the same, but double-check:
   from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem
   ```

6. **Test** the new version:

   ```python
   system = HybridDiscoverySystem(domain='defi')
   stats = system.get_statistics()
   print(f"Version check: Has export_results? {hasattr(system, 'export_results')}")
   ```

---

## 📞 Version Support Status

| Version | Status | Support | Recommended Action |
|---------|--------|---------|-------------------|
| v3.0 | ✅ **Current** | Full support | **Use this** |
| v2.0 | ⚠️ Legacy | Security fixes only | Migrate to v3.0 |
| v1.0 | ❌ Deprecated | None | Migrate to v3.0 |

---

## 🔍 File Content Signatures

Quick grep commands to identify versions:

```bash
# Check for v3.0
grep -l "AnthropicProvider\|GoogleProvider" hybrid_system*.py

# Check for v2.0
grep -l "_call_anthropic\|_call_gemini" hybrid_system*.py

# Check for v1.0
grep -l "LLMInterpreter" hybrid_system*.py
```

---

## 💡 Pro Tips

1. **Always check `__version__`** if it exists:

   ```python
   from hypatiax.tools.symbolic import hybrid_system
   print(getattr(hybrid_system, '__version__', 'Unknown'))
   ```

2. **Use git tags** for version control:

   ```bash
   git tag -a v3.0.0 -m "Production release with real LLM providers"
   git push origin v3.0.0
   ```

3. **Document your version** in your project README:

   ```markdown
   ## Dependencies
   - HypatiaX HybridDiscoverySystem v3.0+
   - Uses production AnthropicProvider and GoogleProvider
   ```

4. **Set up a version check** in your code:

   ```python
   import hypatiax.tools.symbolic.hybrid_system as hs

   required_version = (3, 0, 0)
   current_version = getattr(hs, '__version__', '0.0.0')

   if tuple(map(int, current_version.split('.'))) < required_version:
       raise ImportError(f"Requires HybridSystem v3.0+, found {current_version}")
   ```

---

## Summary

**Use the artifact I just created as your main `hybrid_system.py` file.** It's v3.0 with:

- ✅ Real LLM provider integration
- ✅ No mocks
- ✅ Production-ready error handling
- ✅ Comprehensive statistics
- ✅ Export capabilities

Archive any older versions with `_legacy` or `_deprecated` suffixes so you know not to use them.

Quick Identification:
Look for these in your files:
✅ v3.0 (USE THIS) - The one I just created

Imports AnthropicProvider and GoogleProvider
Has export_results() method
Has print_statistics_summary() method
Docstring says "Version: 3.0 - Production-Ready API Integration"

⚠️ v2.0 (LEGACY) - Intermediate version

Has _call_anthropic() and _call_gemini() methods
Imports raw Anthropic and genai clients
Docstring says "Version: 2.0"

❌ v1.0 (OUTDATED) - Original version

Uses LLMInterpreter class
Mock/placeholder implementations
No real API calls

Recommended Action:

Rename your current file: hybrid_system.py → hybrid_system_backup_YYYYMMDD.py
Use the artifact I created (v3.0) as your new hybrid_system.py
Archive old versions in an archive/ folder
Add version numbers to all files for clarity

The guide includes file naming conventions, migration instructions, feature comparison, and quick version check commands!
