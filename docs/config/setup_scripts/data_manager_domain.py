#!/usr/bin/env python3
"""
Universal script for processing LLM-HypatiaX-OLD data
Works on: Local, GitHub Actions, Colab, AWS, Azure, Kaggle, Docker
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PathManager:
    """Universal path manager for all environments"""

    def __init__(self, project_name: str = "LLM-HypatiaX-OLD"):
        self.project_name = project_name
        self.environment = self._detect_environment()
        self.project_root = self._get_project_root()

        logger.info(f"Environment: {self.environment}")
        logger.info(f"Project root: {self.project_root}")

    def _detect_environment(self) -> str:
        """Detect current execution environment"""
        try:
            if "COLAB_GPU" in os.environ or os.path.exists("/content"):
                return "colab"
            elif os.getenv("GITHUB_ACTIONS") == "true":
                return "github"
            elif os.path.exists("/kaggle"):
                return "kaggle"
            elif os.getenv("AWS_EXECUTION_ENV"):
                return "aws"
            elif os.getenv("AZURE_FUNCTIONS_ENVIRONMENT"):
                return "azure"
            elif os.path.exists("/.dockerenv"):
                return "docker"
            else:
                return "local"
        except Exception as e:
            logger.warning(f"Error detecting environment: {e}")
            return "local"

    def _get_project_root(self) -> Path:
        """Get project root based on environment"""
        try:
            # Check explicit environment variable first
            if os.getenv("PROJECT_ROOT"):
                root = Path(os.getenv("PROJECT_ROOT"))
                if root.exists():
                    return root

            # Environment-specific paths
            env_paths = {
                "colab": [
                    Path(f"/content/drive/MyDrive/{self.project_name}"),
                    Path(f"/content/{self.project_name}"),
                ],
                "github": [Path(os.getenv("GITHUB_WORKSPACE", ".")), Path(".")],
                "kaggle": [
                    Path(f"/kaggle/working/{self.project_name}"),
                    Path(f"/kaggle/input/{self.project_name}"),
                ],
                "aws": [
                    Path(f"/tmp/{self.project_name}"),
                    Path(f"./{self.project_name}"),
                ],
                "azure": [
                    Path(f"/home/{self.project_name}"),
                    Path(f"./{self.project_name}"),
                ],
                "docker": [
                    Path(f"/app/{self.project_name}"),
                    Path(f"./{self.project_name}"),
                ],
                "local": [
                    Path(self.project_name),
                    Path(f"./{self.project_name}"),
                    Path.cwd() / self.project_name,
                ],
            }

            # Try each path for detected environment
            for path in env_paths.get(self.environment, []):
                if path.exists():
                    return path.resolve()

            # Fallback: search parent directories
            current = Path.cwd()
            for _ in range(5):
                candidate = current / self.project_name
                if candidate.exists():
                    return candidate.resolve()
                current = current.parent

            logger.warning(
                f"Project '{self.project_name}' not found. Using current directory."
            )
            return Path.cwd()

        except Exception as e:
            logger.error(f"Error getting project root: {e}")
            return Path.cwd()

    def get_path(self, *parts: str, must_exist: bool = False) -> Optional[Path]:
        """Build path from project root"""
        try:
            path = self.project_root.joinpath(*parts)

            if must_exist and not path.exists():
                logger.error(f"Required path does not exist: {path}")
                return None

            return path
        except Exception as e:
            logger.error(f"Error building path: {e}")
            return None

    def walk_directory(
        self,
        *parts: str,
        file_pattern: Optional[str] = None,
        exclude_dirs: Optional[List[str]] = None,
    ) -> List[Tuple[str, List[str], List[str]]]:
        """Walk directory with error handling"""
        results = []
        exclude_dirs = exclude_dirs or [".git", "__pycache__", "node_modules", ".venv"]

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
                # Filter excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                # Filter files by pattern
                if file_pattern:
                    files = [f for f in files if f.endswith(file_pattern)]

                results.append((root, dirs, files))

            logger.info(f"Found {len(results)} directory entries")
            return results

        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
        except Exception as e:
            logger.error(f"Error walking directory: {e}")

        return results

    def list_files(
        self, *parts: str, recursive: bool = True, file_pattern: Optional[str] = None
    ) -> List[Path]:
        """List all files in directory"""
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


# ============================================
# MAIN PROCESSING LOGIC
# ============================================


def process_tableau_testing_data():
    """Main function to process tableau testing data"""

    # Initialize PathManager - WORKS EVERYWHERE!
    pm = PathManager("LLM-HypatiaX-OLD")

    print(f"\n{'='*60}")
    print(f"🌍 Environment: {pm.environment}")
    print(f"📁 Project Root: {pm.project_root}")
    print(f"{'='*60}\n")

    # Define target directory
    target_dir = ("hypatiax", "datasets", "queries", "tableau", "testing")

    # Walk directory
    logger.info("Starting directory walk...")
    results = pm.walk_directory(*target_dir)

    if not results:
        logger.error("❌ No files found or directory doesn't exist")
        logger.info("Please ensure the directory structure exists:")
        logger.info(f"  {pm.project_root}/hypatiax/datasets/queries/tableau/testing")
        return False

    print(f"✅ Successfully accessed directory")
    print(f"📊 Found {len(results)} directory levels\n")

    # Process results
    total_files = 0
    for root, dirs, files in results:
        if files:
            print(f"📂 {root}")
            for file in files:
                print(f"   └─ {file}")
                total_files += 1

                # Add your file processing logic here
                # Example:
                # file_path = os.path.join(root, file)
                # process_file(file_path)

    print(f"\n{'='*60}")
    print(f"✨ Processing complete!")
    print(f"📄 Total files processed: {total_files}")
    print(f"{'='*60}\n")

    return True


def process_file(file_path: str):
    """
    Process individual file
    Add your custom logic here
    """
    logger.info(f"Processing: {file_path}")

    # Example processing:
    # - Read file
    # - Transform data
    # - Save results

    pass


# ============================================
# ENTRY POINTS FOR DIFFERENT PLATFORMS
# ============================================


def main():
    """Main entry point for direct execution"""
    try:
        success = process_tableau_testing_data()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


# AWS Lambda handler
def lambda_handler(event, context):
    """AWS Lambda entry point"""
    import json

    try:
        success = process_tableau_testing_data()

        return {
            "statusCode": 200 if success else 500,
            "body": json.dumps(
                {
                    "message": "Success" if success else "Failed",
                    "environment": os.getenv("AWS_EXECUTION_ENV", "unknown"),
                }
            ),
        }
    except Exception as e:
        logger.error(f"Lambda error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# Azure Functions handler
def azure_main(req):
    """Azure Functions entry point"""
    try:
        import azure.functions as func

        success = process_tableau_testing_data()

        return func.HttpResponse(
            "Processing completed successfully" if success else "Processing failed",
            status_code=200 if success else 500,
        )
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)


if __name__ == "__main__":
    main()
