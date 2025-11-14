import pkg_resources
import sys

def check_versions(requirements_file='requirements.txt'):
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"{'Package':<30} {'Required':<15} {'Installed':<15} {'Status'}")
    print("="*75)
    
    for req in requirements:
        try:
            pkg = pkg_resources.Requirement.parse(req)
            installed = pkg_resources.get_distribution(pkg.project_name)
            
            status = "✓ OK"
            if pkg.specifier and installed.version not in pkg.specifier:
                status = "⚠ MISMATCH"
            
            print(f"{pkg.project_name:<30} {str(pkg.specifier):<15} {installed.version:<15} {status}")
        except Exception as e:
            print(f"{req:<30} {'ERROR':<15} {str(e):<15}")

if __name__ == "__main__":
    check_versions()
