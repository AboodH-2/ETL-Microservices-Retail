#!/usr/bin/env python3
"""
Script to create a submission ZIP file for the microservices assignment.
This script collects all required files and creates a ZIP archive.
"""

import os
import zipfile
import shutil
from datetime import datetime

def create_submission_zip():
    # Set the file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'docker-microservices-submission_{timestamp}.zip'
    zip_path = os.path.join(current_dir, zip_filename)
    
    # Files and directories to include
    files_to_include = [
        'README.md',
        'DOCUMENTATION.md',
        'docker-compose.yml',
        'docker-compose-scaled.yml',
        'deploy.sh',
        'deploy-scaled.sh',
        'nginx.conf'
    ]
    
    dirs_to_include = [
        'frontend',
        'backend',
        'postgres-init',
        'mysql-init'
    ]
    
    # Create a temporary directory to organize files
    temp_dir = os.path.join(current_dir, 'temp_submission')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Copy files
    print(f"Creating submission ZIP file: {zip_filename}")
    print("Collecting files...")
    
    # Copy individual files
    for file in files_to_include:
        src_path = os.path.join(current_dir, file)
        if os.path.exists(src_path):
            print(f"Adding: {file}")
            dest_path = os.path.join(temp_dir, file)
            shutil.copy2(src_path, dest_path)
        else:
            print(f"Warning: {file} not found, skipping")
    
    # Copy directories
    for dir_name in dirs_to_include:
        src_dir = os.path.join(current_dir, dir_name)
        if os.path.exists(src_dir):
            print(f"Adding directory: {dir_name}")
            dest_dir = os.path.join(temp_dir, dir_name)
            shutil.copytree(src_dir, dest_dir)
        else:
            print(f"Warning: {dir_name} directory not found, skipping")
    
    # Create the ZIP file
    print("Creating ZIP archive...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add files from temp directory to ZIP
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Get the relative path for the ZIP file
                rel_path = os.path.relpath(file_path, temp_dir)
                print(f"Adding to ZIP: {rel_path}")
                zipf.write(file_path, rel_path)
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    print(f"\nSubmission ZIP file created successfully: {zip_filename}")
    print(f"Size: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
    print(f"Location: {zip_path}")

if __name__ == "__main__":
    create_submission_zip() 