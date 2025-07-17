#!/usr/bin/env python
"""
Wrapper script to run run_roles.py with proper environment setup for Windows.
This ensures Claude CLI can execute properly from any shell environment.
"""
import os
import sys
import subprocess
import platform

def main():
    # Set up proper environment for Windows
    env = os.environ.copy()
    
    if platform.system() == 'Windows':
        # Required for Claude CLI to find Git Bash
        env['CLAUDE_CODE_GIT_BASH_PATH'] = r'C:\Program Files\Git\bin\bash.exe'
        # Required for Windows .cmd file execution
        env['COMSPEC'] = r'C:\Windows\System32\cmd.exe'
    
    # Pass all command line arguments to run_roles.py
    cmd = ['python', 'run_roles.py'] + sys.argv[1:]
    
    # Run with the fixed environment
    result = subprocess.run(cmd, env=env)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()