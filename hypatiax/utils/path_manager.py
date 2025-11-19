import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PathManager:
    """Universal path manager for local, GitHub, and cloud environments"""
    
    def __init__(self, project_name: str = "LLM-HypatiaX-Colab"):
        self.project_name = project_name
        self.environment = self._detect_environment()
        self.project_root = self._get_project_root()
        
        logger.info(f"Environment detected: {self.environment}")
        logger.info(f"Project root: {self.project_root}")
    
    def _detect_environment(self) -> str:
        """Detect the current execution environment"""
        try:
            # Google Colab
            if 'COLAB_GPU' in os.environ or os.path.exists('/content'):
                return 'colab'
            # GitHub Actions
            elif os.getenv('GITHUB_ACTIONS') == 'true':
                return 'github'
            # Kaggle
            elif os.path.exists('/kaggle'):
                return 'kaggle'
            # AWS/Cloud (check common cloud indicators)
            elif os.getenv('AWS_EXECUTION_ENV') or os.getenv('LAMBDA_TASK_ROOT'):
                return 'aws'
            # Azure
            elif os.getenv('AZURE_FUNCTIONS_ENVIRONMENT'):
                return 'azure'
            # Docker
            elif os.path.exists('/.dockerenv'):
                return 'docker'
            # Local
            else:
                return 'local'
        except Exception as e:
            logger.warning(f"Error detecting environment: {e}. Defaulting to 'local'")
            return 'local'
    
    def _get_project_root(self) -> Path:
        """Get project root based on environment"""
        try:
            # Check for explicit environment variable first
            if os.getenv('PROJECT_ROOT'):
                root = Path(os.getenv('PROJECT_ROOT'))
                if root.exists():
                    return root
                logger.warning(f"PROJECT_ROOT env var set but path doesn't exist: {root}")
            
            # Environment-specific paths
            env_paths = {
                'colab': [
                    Path(f'/content/drive/MyDrive/{self.project_name}'),
                    Path(f'/content/{self.project_name}')
                ],
                'github': [
                    Path(os.getenv('GITHUB_WORKSPACE', '.')),
                    Path('.')
                ],
                'kaggle': [
                    Path(f'/kaggle/working/{self.project_name}'),
                    Path(f'/kaggle/input/{self.project_name}')
                ],
                'aws': [
                    Path(f'/tmp/{self.project_name}'),
                    Path(f'./{self.project_name}')
                ],
                'azure': [
                    Path(f'/home/{self.project_name}'),
                    Path(f'./{self.project_name}')
                ],
                'docker': [
                    Path(f'/app/{self.project_name}'),
                    Path(f'./{self.project_name}')
                ],
                'local': [
                    Path(self.project_name),
                    Path(f'./{self.project_name}'),
                    Path.cwd() / self.project_name
                ]
            }
            
            # Try each path for the detected environment
            for path in env_paths.get(self.environment, []):
                if path.exists():
                    logger.info(f"Found project root: {path}")
                    return path.resolve()
            
            # Fallback: search in parent directories
            current = Path.cwd()
            for _ in range(5):  # Search up to 5 levels up
                candidate = current / self.project_name
                if candidate.exists():
                    logger.info(f"Found project root in parent: {candidate}")
                    return candidate.resolve()
                current = current.parent
            
            # Last resort: use current directory
            logger.warning(f"Project directory '{self.project_name}' not found. Using current directory.")
            return Path.cwd()
            
        except Exception as e:
            logger.error(f"Error getting project root: {e}")
            return Path.cwd()
    
    def get_path(self, *parts: str, must_exist: bool = False) -> Optional[Path]:
        """
        Build path from project root
        
        Args:
            *parts: Path components
            must_exist: If True, return None if path doesn't exist
        
        Returns:
            Path object or None if must_exist=True and path doesn't exist
        """
        try:
            path = self.project_root.joinpath(*parts)
            
            if must_exist and not path.exists():
                logger.error(f"Required path does not exist: {path}")
                return None
            
            return path
            
        except Exception as e:
            logger.error(f"Error building path: {e}")
            return None
    
    def walk_directory(self, *parts: str, 
                      file_pattern: Optional[str] = None,
                      exclude_dirs: Optional[List[str]] = None) -> List[Tuple[str, List[str], List[str]]]:
        """
        Walk directory with error handling
        
        Args:
            *parts: Path components from project root
            file_pattern: Filter files by extension (e.g., '.txt', '.py')
            exclude_dirs: Directory names to exclude
        
        Returns:
            List of (root, dirs, files) tuples
        """
        results = []
        exclude_dirs = exclude_dirs or ['.git', '__pycache__', 'node_modules', '.venv']
        
        try:
            target_path = self.get_path(*parts, must_exist=True)
            
            if not target_path:
                logger.error(f"Cannot walk non-existent path: {'/'.join(parts)}")
                return results
            
            if not target_path.is_dir():
                logger.error(f"Path is not a directory: {target_path}")
                return results
            
            logger.info(f"Walking directory: {target_path}")
            
            for root, dirs, files in os.walk(target_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                # Filter files by pattern if specified
                if file_pattern:
                    files = [f for f in files if f.endswith(file_pattern)]
                
                results.append((root, dirs, files))
                
            logger.info(f"Successfully walked directory. Found {len(results)} entries.")
            return results
            
        except PermissionError as e:
            logger.error(f"Permission denied accessing directory: {e}")
        except OSError as e:
            logger.error(f"OS error while walking directory: {e}")
        except Exception as e:
            logger.error(f"Unexpected error walking directory: {e}")
        
        return results
    
    def list_files(self, *parts: str, 
                   recursive: bool = True,
                   file_pattern: Optional[str] = None) -> List[Path]:
        """
        List all files in directory
        
        Args:
            *parts: Path components from project root
            recursive: Include subdirectories
            file_pattern: Filter by extension
        
        Returns:
            List of file paths
        """
        files = []
        
        try:
            target_path = self.get_path(*parts, must_exist=True)
            
            if not target_path:
                return files
            
            if recursive:
                pattern = f"**/*{file_pattern}" if file_pattern else "**/*"
                files = [f for f in target_path.glob(pattern) if f.is_file()]
            else:
                pattern = f"*{file_pattern}" if file_pattern else "*"
                files = [f for f in target_path.glob(pattern) if f.is_file()]
            
            logger.info(f"Found {len(files)} files")
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return files
    
    def ensure_directory(self, *parts: str) -> Optional[Path]:
        """
        Create directory if it doesn't exist
        
        Args:
            *parts: Path components from project root
        
        Returns:
            Path object or None on error
        """
        try:
            path = self.get_path(*parts)
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {path}")
            return path
        except Exception as e:
            logger.error(f"Error creating directory: {e}")
            return None
    
    def validate_path(self, *parts: str) -> bool:
        """Check if path exists and is accessible"""
        try:
            path = self.get_path(*parts)
            return path.exists() and os.access(path, os.R_OK)
        except Exception as e:
            logger.error(f"Error validating path: {e}")
            return False


# ============================================
# USAGE EXAMPLES
# ============================================

def main():
    """Example usage of PathManager"""
    
    # Initialize path manager
    pm = PathManager("LLM-HypatiaX-OLD")
    
    # Example 1: Walk a specific directory
    print("\n" + "="*50)
    print("Example 1: Walking directory")
    print("="*50)
    
    results = pm.walk_directory("hypatiax", "datasets", "queries", "tableau", "testing")
    
    if results:
        for root, dirs, files in results:
            print(f"\nDirectory: {root}")
            print(f"Subdirectories: {dirs}")
            print(f"Files: {files}")
    else:
        print("No results found or directory doesn't exist")
    
    # Example 2: List all Python files recursively
    print("\n" + "="*50)
    print("Example 2: List Python files")
    print("="*50)
    
    py_files = pm.list_files("hypatiax", recursive=True, file_pattern=".py")
    for file in py_files[:10]:  # Show first 10
        print(f"  {file}")
    
    # Example 3: Get specific file path
    print("\n" + "="*50)
    print("Example 3: Get specific path")
    print("="*50)
    
    config_path = pm.get_path("hypatiax", "config.json", must_exist=False)
    if config_path:
        print(f"Config path: {config_path}")
        print(f"Exists: {config_path.exists()}")
    
    # Example 4: Validate path
    print("\n" + "="*50)
    print("Example 4: Validate path")
    print("="*50)
    
    is_valid = pm.validate_path("hypatiax", "datasets")
    print(f"Path is valid and accessible: {is_valid}")
    
    # Example 5: Create directory
    print("\n" + "="*50)
    print("Example 5: Ensure directory exists")
    print("="*50)
    
    output_dir = pm.ensure_directory("output", "results")
    if output_dir:
        print(f"Output directory ready: {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
