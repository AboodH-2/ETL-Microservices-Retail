#!/usr/bin/env python3
"""
Cleanup script to prepare the repository for GitHub.
This script removes unnecessary files and directories.
"""

import os
import shutil
import glob

def cleanup():
    """Remove unnecessary files and directories"""
    # Directories to remove
    dirs_to_remove = [
        "docker-airflow/logs",
        "**/temp_submission",
        "**/__pycache__",
        "**/.ipynb_checkpoints",
        "**/build",
        "**/dist",
    ]
    
    # Files to remove
    file_patterns_to_remove = [
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/*.so",
        "**/*.zip",
        "**/*.tar.gz",
        "**/*.log",
        "**/*.sqlite",
        "**/*.db",
        "**/.DS_Store",
    ]
    
    print("Cleaning up repository for GitHub...")
    
    # Remove directories
    for dir_pattern in dirs_to_remove:
        for dir_path in glob.glob(dir_pattern, recursive=True):
            if os.path.exists(dir_path):
                print(f"Removing directory: {dir_path}")
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    print(f"Error removing {dir_path}: {str(e)}")
    
    # Remove files
    for file_pattern in file_patterns_to_remove:
        for file_path in glob.glob(file_pattern, recursive=True):
            if os.path.exists(file_path):
                print(f"Removing file: {file_path}")
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing {file_path}: {str(e)}")
    
    print("Cleanup completed successfully!")

if __name__ == "__main__":
    cleanup() 