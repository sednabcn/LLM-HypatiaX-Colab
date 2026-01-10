# Julia Registry Update Guide

Complete guide for updating Julia package registries and managing packages.

## 📦 Table of Contents

1. [Updating the General Registry](#1-updating-the-general-registry)
2. [Updating All Installed Packages](#2-updating-all-installed-packages)
3. [Updating Specific Packages](#3-updating-specific-packages)
4. [Managing Custom Registries](#4-managing-custom-registries)
5. [Registering Your Own Package](#5-registering-your-own-package)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Updating the General Registry

### Method 1: Using Pkg REPL (Recommended)

```julia
# Enter package mode by pressing ]
julia> ]

# Update registry
(@v1.10) pkg> registry update

# Or shorter version
(@v1.10) pkg> reg up
```

### Method 2: Using Pkg API

```julia
using Pkg

# Update all registries
Pkg.Registry.update()

# Or explicitly update General registry
Pkg.Registry.update("General")
```

### Method 3: Command Line

```bash
# From terminal (outside Julia)
julia -e 'using Pkg; Pkg.Registry.update()'
```

---

## 2. Updating All Installed Packages

### Update All Packages in Current Environment

```julia
# In Pkg REPL
] update

# Or using Pkg API
using Pkg
Pkg.update()
```

### Update Registry + Packages (Combined)

```julia
] registry update
] update

# Or in one line with API
using Pkg
Pkg.Registry.update()
Pkg.update()
```

### Update with Verbose Output

```julia
using Pkg
Pkg.update(; verbose=true)
```

---

## 3. Updating Specific Packages

### Update Single Package

```julia
# In Pkg REPL
] update PackageName

# Or using API
using Pkg
Pkg.update("PackageName")
```

### Update Multiple Specific Packages

```julia
] update Package1 Package2 Package3

# Or
using Pkg
Pkg.update(["Package1", "Package2", "Package3"])
```

### Pin Package to Specific Version (Prevent Updates)

```julia
# Pin to current version
] pin PackageName

# Pin to specific version
] pin PackageName@v1.2.3

# Unpin to allow updates
] free PackageName
```

---

## 4. Managing Custom Registries

### Add Custom Registry

```julia
using Pkg

# Add registry by URL
Pkg.Registry.add("https://github.com/YourOrg/YourRegistry.git")

# Add registry by RegistrySpec
Pkg.Registry.add(RegistrySpec(url="https://github.com/YourOrg/YourRegistry.git"))

# Add with specific name
Pkg.Registry.add(RegistrySpec(
    url="https://github.com/YourOrg/YourRegistry.git",
    name="MyRegistry"
))
```

### List All Registries

```julia
] registry status

# Or
using Pkg
Pkg.Registry.status()
```

### Remove Registry

```julia
using Pkg
Pkg.Registry.rm("RegistryName")
```

### Update Specific Registry

```julia
using Pkg
Pkg.Registry.update("MyCustomRegistry")
```

---

## 5. Registering Your Own Package

### Prerequisites

1. **GitHub Repository** with your package
2. **JuliaRegistries bot** installed
3. **Project.toml** with proper metadata

### Automatic Registration (Recommended)

#### Step 1: Install JuliaRegistrator

```julia
] add JuliaRegistrator
```

#### Step 2: Create Registration PR

**Option A: GitHub Comment (Easiest)**

1. Go to your package repository on GitHub
2. Create a new issue or commit
3. Comment: `@JuliaRegistrator register`

The bot will automatically:
- Check version number
- Verify tests pass
- Create PR to General registry

**Option B: Using LocalRegistry.jl**

```julia
using Pkg
Pkg.add("LocalRegistry")

using LocalRegistry

# Register to General registry
register("YourPackageName")

# Or register to custom registry
register("YourPackageName", registry="MyRegistry")
```

### Manual Registration

#### Step 1: Prepare Package

```julia
# Ensure Project.toml has required fields
"""
name = "YourPackage"
uuid = "12345678-1234-1234-1234-123456789abc"
authors = ["Your Name <email@example.com>"]
version = "0.1.0"

[deps]
PackageA = "uuid-here"

[compat]
julia = "1.6"
PackageA = "1.2"
"""
```

#### Step 2: Tag Release

```bash
git tag v0.1.0
git push --tags
```

#### Step 3: Submit to Registry

1. Fork https://github.com/JuliaRegistries/General
2. Run registration script
3. Submit PR

```julia
using Pkg
Pkg.Registry.add(RegistrySpec(url="https://github.com/JuliaRegistries/General.git"))
```

---

## 6. Troubleshooting

### Registry Update Fails

```julia
# Remove and re-add General registry
using Pkg
Pkg.Registry.rm("General")
Pkg.Registry.add(RegistrySpec(url="https://github.com/JuliaRegistries/General.git"))
```

### Package Not Found After Registry Update

```julia
# Force update and resolve
using Pkg
Pkg.Registry.update()
Pkg.resolve()
Pkg.instantiate()
```

### Corrupted Registry

```bash
# Delete registry directory manually
# Linux/Mac:
rm -rf ~/.julia/registries/General

# Windows:
# Delete C:\Users\YourName\.julia\registries\General

# Then re-add in Julia:
using Pkg
Pkg.Registry.add(RegistrySpec(url="https://github.com/JuliaRegistries/General.git"))
```

### Verify Registry Status

```julia
using Pkg

# Check registry location
println(Pkg.depots1())

# List all registries
Pkg.Registry.status()

# Check specific package availability
] add PackageName  # Will show if found in registry
```

### Update Fails Due to Conflicts

```julia
# Check status of packages
] status

# Resolve dependency conflicts
] resolve

# If still failing, try:
] update --manifest  # Update Manifest.toml

# Nuclear option: rebuild environment
using Pkg
Pkg.rm(["Package1", "Package2"])  # Remove problematic packages
Pkg.Registry.update()
Pkg.add(["Package1", "Package2"])  # Re-add them
```

---

## 📋 Quick Reference Commands

| Task | Command |
|------|---------|
| Update registry | `] registry update` |
| Update all packages | `] update` |
| Update specific package | `] update PackageName` |
| List registries | `] registry status` |
| Add custom registry | `Pkg.Registry.add("url")` |
| Register package | `@JuliaRegistrator register` (GitHub) |
| Pin package version | `] pin PackageName@v1.2.3` |
| Free pinned package | `] free PackageName` |

---

## 🔧 Best Practices

1. **Regular Updates**: Update registry weekly
   ```julia
   # Add to startup.jl for automatic updates
   using Pkg
   Pkg.Registry.update()
   ```

2. **Before Adding Packages**: Always update registry first
   ```julia
   ] registry update
   ] add NewPackage
   ```

3. **Use Version Bounds**: Specify compat in Project.toml
   ```toml
   [compat]
   PackageA = "1.2, 2"
   julia = "1.6"
   ```

4. **Test Before Registering**: Ensure tests pass
   ```julia
   ] test YourPackage
   ```

5. **Semantic Versioning**: Follow semver for releases
   - `1.0.0` → `1.0.1` (bug fixes)
   - `1.0.0` → `1.1.0` (new features)
   - `1.0.0` → `2.0.0` (breaking changes)

---

## 🚀 Advanced: Automated Updates

### GitHub Actions for Auto-Registry Update

Create `.github/workflows/RegistryUpdate.yml`:

```yaml
name: Update Registry

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:      # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: julia-actions/setup-julia@v1
        with:
          version: '1.10'
      
      - name: Update Registry
        run: |
          julia -e '
            using Pkg
            Pkg.Registry.update()
            Pkg.update()
          '
      
      - name: Run Tests
        run: |
          julia --project -e '
            using Pkg
            Pkg.test()
          '
```

### Startup Script for Auto-Updates

Add to `~/.julia/config/startup.jl`:

```julia
# Auto-update registry on Julia startup (once per day)
try
    using Pkg
    registry_path = joinpath(DEPOT_PATH[1], "registries", "General")
    
    if isdir(registry_path)
        # Check if last update was > 24 hours ago
        last_update = mtime(registry_path)
        if time() - last_update > 86400  # 24 hours
            @info "Updating package registry..."
            Pkg.Registry.update()
        end
    else
        @info "Adding General registry..."
        Pkg.Registry.add("General")
    end
catch e
    @warn "Registry update failed" exception=e
end
```

---

## 📚 Additional Resources

- **Official Docs**: https://pkgdocs.julialang.org/
- **Registry GitHub**: https://github.com/JuliaRegistries/General
- **Package Guidelines**: https://julialang.github.io/Pkg.jl/
- **Registrator Docs**: https://github.com/JuliaRegistries/Registrator.jl

---

**Last Updated**: December 25, 2025  
**Julia Version Compatibility**: 1.6+
