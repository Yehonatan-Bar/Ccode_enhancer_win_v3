#!/usr/bin/env python3
"""
Script to show the differences between the last commit and the current uncommitted code.
"""

import subprocess
import sys
from cc_logging import setup_logger, log_exception


def get_git_diff():
    """Get the diff between the last commit and current uncommitted changes."""
    logger = setup_logger('cc_enhancer.git_diff')
    logger.debug("Starting git diff generation")
    
    try:
        all_output = []
        
        # First, get the diff for tracked files
        result = subprocess.run(
            ['git', 'diff', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            logger.info(f"Found modified tracked files: {len(result.stdout.splitlines())} lines")
            all_output.append("=== Modified tracked files ===")
            all_output.append(result.stdout)
        else:
            logger.debug("No modified tracked files found")
        
        # Get the list of untracked files
        untracked_result = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if untracked_result.stdout:
            untracked_files = untracked_result.stdout.strip().split('\n')
            untracked_files = [f for f in untracked_files if f]  # Remove empty strings
            logger.info(f"Found {len(untracked_files)} untracked files")
            
            # Filter out less important files to focus on code changes
            important_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
                                  '.cs', '.rb', '.go', '.rs', '.swift', '.php', '.html', '.css',
                                  '.json', '.xml', '.yaml', '.yml', '.md', '.txt']
            filtered_files = []
            for f in untracked_files:
                # Skip claude output files and archive directory
                if 'claude_output_' in f or f.startswith('archive/'):
                    continue
                # Include files with important extensions or no extension (could be scripts)
                if any(f.endswith(ext) for ext in important_extensions) or '.' not in f:
                    filtered_files.append(f)
            
            untracked_files = filtered_files
            logger.debug(f"Filtered to {len(untracked_files)} relevant untracked files")
            
            if untracked_files:
                all_output.append("\n=== New untracked files ===")
                for file in untracked_files:
                    all_output.append(f"\n+++ New file: {file}")
                    try:
                        # Try to show content of new text files (skip binary)
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Create a diff-like format for new files
                            all_output.append(f"@@ -0,0 +1,{len(content.splitlines())} @@")
                            for i, line in enumerate(content.splitlines()[:100], 1):  # Limit to first 100 lines
                                all_output.append(f"+{line}")
                            if len(content.splitlines()) > 100:
                                all_output.append(f"... [{len(content.splitlines()) - 100} more lines]")
                    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
                        all_output.append("[Binary file or directory]")
                    except Exception as e:
                        all_output.append(f"[Could not read file: {e}]")
        
        # Reorder output: new files first, then modified files
        final_output = []
        
        # Find new files section and add it first
        new_files_index = -1
        for i, item in enumerate(all_output):
            if "=== New untracked files ===" in item:
                new_files_index = i
                break
        
        if new_files_index >= 0:
            # Add new files section first
            final_output.extend(all_output[new_files_index:])
        
        # Then add modified files
        if result.stdout:
            if final_output:
                final_output.append("\n")
            final_output.extend(all_output[:new_files_index if new_files_index >= 0 else len(all_output)])
        
        # Output everything
        if final_output:
            logger.info(f"Generated diff output: {len('\n'.join(final_output).splitlines())} lines")
            print("Differences between the last commit and current uncommitted changes:")
            print("-" * 80)
            
            combined_output = '\n'.join(final_output)
            lines = combined_output.splitlines()
            
            if len(lines) > 500:
                for i, line in enumerate(lines[:500]):
                    print(line)
                print(f"\n[Output truncated at line 500 - total output was {len(lines)} lines]")
            else:
                print(combined_output)
        else:
            logger.info("No uncommitted changes found")
            print("No uncommitted changes found.")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed with return code {e.returncode}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
            print(f"Git error: {e.stderr}")
        else:
            print(f"Git command failed with return code {e.returncode}")
        log_exception(logger, e, "get_git_diff")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error("Git is not installed or not in PATH")
        print("Error: Git is not installed or not in PATH.")
        log_exception(logger, e, "get_git_diff")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in get_git_diff: {type(e).__name__}: {e}")
        print(f"Unexpected error: {type(e).__name__}: {e}")
        log_exception(logger, e, "get_git_diff")
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
    logger = setup_logger('cc_enhancer.git_diff')
    logger.info("git_diff_last_commit.py started")
    
    try:
        # Check if we're in a git repository
        subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError:
        logger.error("Not in a git repository")
        print("Error: Not in a git repository.")
        sys.exit(1)
    except FileNotFoundError:
        logger.error("Git is not installed or not in PATH")
        print("Error: Git is not installed or not in PATH.")
        sys.exit(1)
    
    get_commit_info()
    get_status_info()
    get_git_diff()


if __name__ == "__main__":
    main()