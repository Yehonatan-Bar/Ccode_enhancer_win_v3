#!/usr/bin/env python3
"""
Script to show the differences between the last commit and the previous one.
"""

import subprocess
import sys


def get_git_diff():
    """Get the diff between the last commit and the previous one."""
    try:
        # Get the diff between HEAD and HEAD~1
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            print("Differences between the last commit and the previous one:")
            print("-" * 80)
            print(result.stdout)
        else:
            print("No differences found between the last commit and the previous one.")
            
    except subprocess.CalledProcessError as e:
        if e.stderr and "ambiguous argument 'HEAD~1'" in e.stderr:
            print("Error: This appears to be the first commit (no previous commit exists).")
        elif e.stderr:
            print(f"Git error: {e.stderr}")
        else:
            print(f"Git command failed with return code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Git is not installed or not in PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        sys.exit(1)


def get_commit_info():
    """Get information about the last two commits."""
    try:
        # Get info about the last two commits
        result = subprocess.run(
            ['git', 'log', '--oneline', '-2'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            print("\nLast two commits:")
            print(result.stdout)
            print()
            
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(f"Error getting commit info: {e.stderr}")
        else:
            print(f"Error getting commit info: Command failed with return code {e.returncode}")
    except FileNotFoundError:
        print("Error: Git is not installed or not in PATH.")
    except Exception as e:
        print(f"Unexpected error getting commit info: {type(e).__name__}: {e}")


def main():
    """Main function to handle the script execution."""
    try:
        # Check if we're in a git repository
        subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository.")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Git is not installed or not in PATH.")
        sys.exit(1)
    
    get_commit_info()
    get_git_diff()


if __name__ == "__main__":
    main()