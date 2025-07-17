#!/usr/bin/env python3
"""
Script to show the differences between the last commit and the current uncommitted code.
"""

import subprocess
import sys


def get_git_diff():
    """Get the diff between the last commit and current uncommitted changes."""
    try:
        # Get the diff between HEAD and working directory
        result = subprocess.run(
            ['git', 'diff', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            print("Differences between the last commit and current uncommitted changes:")
            print("-" * 80)
            
            # Split output into lines and limit to 500 lines
            lines = result.stdout.splitlines()
            if len(lines) > 500:
                for i, line in enumerate(lines[:500]):
                    print(line)
                print(f"\n[Output truncated at line 500 - total output was {len(lines)} lines]")
            else:
                print(result.stdout)
        else:
            print("No uncommitted changes found.")
            
    except subprocess.CalledProcessError as e:
        if e.stderr:
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
    """Get information about the last commit and current status."""
    try:
        # Get info about the last commit
        result = subprocess.run(
            ['git', 'log', '--oneline', '-1'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            print("\nLast commit:")
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


def get_status_info():
    """Get git status information."""
    try:
        # Get git status
        result = subprocess.run(
            ['git', 'status', '--short'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            print("Current git status:")
            print(result.stdout)
        else:
            print("Working directory is clean.")
            
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(f"Error getting status: {e.stderr}")
        else:
            print(f"Error getting status: Command failed with return code {e.returncode}")
    except FileNotFoundError:
        print("Error: Git is not installed or not in PATH.")
    except Exception as e:
        print(f"Unexpected error getting status: {type(e).__name__}: {e}")


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
    get_status_info()
    get_git_diff()


if __name__ == "__main__":
    main()