#!/usr/bin/env python3
"""
Virtual Environment Explorer
Shows where packages are installed in your venv
"""

import os
import site
import sys
from pathlib import Path


def get_venv_info():
    """Get information about the current virtual environment"""
    info = {}

    # Check if in venv
    info["in_venv"] = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)

    # Get paths
    info["python_executable"] = sys.executable
    info["python_version"] = sys.version.split()[0]
    info["sys_prefix"] = sys.prefix
    info["site_packages"] = site.getsitepackages()

    return info


def get_package_location(package_name):
    """Get the installation location of a package"""
    try:
        module = __import__(package_name)
        if hasattr(module, "__file__"):
            return Path(module.__file__).parent
        else:
            return "Built-in module (no file location)"
    except ImportError:
        return f"Package '{package_name}' not installed"


def format_size(bytes):
    """Format bytes to human readable size"""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def get_directory_size(path):
    """Calculate total size of directory"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except (PermissionError, FileNotFoundError):
        pass
    return total


def list_installed_packages():
    """List all installed packages in site-packages"""
    site_packages = site.getsitepackages()[0]
    packages = []

    try:
        for item in os.listdir(site_packages):
            item_path = os.path.join(site_packages, item)
            if os.path.isdir(item_path) and not item.endswith(".dist-info"):
                # Skip special directories
                if item in ["__pycache__", "pip", "setuptools", "pkg_resources"]:
                    continue
                size = get_directory_size(item_path)
                packages.append((item, size))
    except (PermissionError, FileNotFoundError):
        pass

    return sorted(packages, key=lambda x: x[1], reverse=True)


def main():
    print("=" * 70)
    print("🐍 VIRTUAL ENVIRONMENT EXPLORER")
    print("=" * 70)

    # Get venv info
    info = get_venv_info()

    print("\n📍 ENVIRONMENT STATUS")
    print("-" * 70)
    if info["in_venv"]:
        print("✓ Running in a virtual environment")
    else:
        print("⚠ NOT in a virtual environment (using system Python)")

    print(f"\n🐍 Python Executable:")
    print(f"   {info['python_executable']}")

    print(f"\n📦 Python Version:")
    print(f"   {info['python_version']}")

    print(f"\n🏠 System Prefix:")
    print(f"   {info['sys_prefix']}")

    print("\n📂 SITE-PACKAGES LOCATIONS")
    print("-" * 70)
    for i, path in enumerate(info["site_packages"], 1):
        print(f"{i}. {path}")
        if os.path.exists(path):
            size = get_directory_size(path)
            print(f"   Size: {format_size(size)}")
            print(f"   Exists: ✓")
        else:
            print(f"   Exists: ✗")

    # Check specific packages
    print("\n🔍 CHECKING KEY PACKAGES")
    print("-" * 70)
    packages_to_check = [
        "hypatiax",
        "spacy",
        "en_core_web_sm",
        "pandas",
        "numpy",
    ]

    for pkg in packages_to_check:
        location = get_package_location(pkg)
        if isinstance(location, Path):
            print(f"\n✓ {pkg}")
            print(f"   Location: {location}")
            if location.exists():
                size = get_directory_size(location)
                print(f"   Size: {format_size(size)}")
        else:
            print(f"\n✗ {pkg}")
            print(f"   {location}")

    # List all packages
    print("\n📊 TOP 10 LARGEST PACKAGES")
    print("-" * 70)
    packages = list_installed_packages()[:10]

    if packages:
        print(f"{'Package':<30} {'Size':>15}")
        print("-" * 70)
        for pkg_name, size in packages:
            print(f"{pkg_name:<30} {format_size(size):>15}")
    else:
        print("No packages found or cannot access site-packages")

    # Show directory structure
    print("\n🌳 VIRTUAL ENVIRONMENT STRUCTURE")
    print("-" * 70)
    venv_root = Path(sys.prefix)
    print(f"{venv_root.name}/")

    # Determine OS-specific subdirectories
    if sys.platform == "win32":
        bin_dir = "Scripts"
        lib_dir = "Lib"
    else:
        bin_dir = "bin"
        lib_dir = "lib"

    structure = [
        (bin_dir, "Executables and scripts"),
        (lib_dir, "Python libraries"),
        ("include", "C header files"),
        ("pyvenv.cfg", "Configuration file"),
    ]

    for name, description in structure:
        path = venv_root / name
        if path.exists():
            print(f"├── {name}/ {'✓':<5} {description}")
        else:
            print(f"├── {name}/ {'✗':<5} {description}")

    # Show site-packages contents
    if info["site_packages"]:
        site_pkg = Path(info["site_packages"][0])
        if site_pkg.exists():
            print(f"│   └── site-packages/")

            # Count items
            try:
                items = list(site_pkg.iterdir())
                pkg_count = sum(1 for i in items if i.is_dir() and not i.name.endswith(".dist-info"))
                print(f"        └── {pkg_count} packages installed")
            except PermissionError:
                print(f"        └── Cannot access directory")

    print("\n" + "=" * 70)
    print("💡 QUICK COMMANDS")
    print("=" * 70)
    print("\nFind package location:")
    print('  python -c "import PKG; print(PKG.__file__)"')
    print("\nList all packages:")
    print("  pip list")
    print("\nShow package details:")
    print("  pip show PACKAGE_NAME")
    print("\nCheck venv activation:")
    if sys.platform == "win32":
        print("  echo %VIRTUAL_ENV%")
    else:
        print("  echo $VIRTUAL_ENV")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
