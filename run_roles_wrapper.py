#!/usr/bin/env python
"""
Wrapper script to run run_roles.py with proper environment setup for Windows.
This ensures Claude CLI can execute properly from any shell environment.
"""
import os
import sys
import subprocess
import platform
from cc_logging import setup_logger, log_session_start, log_session_end, log_exception

def main():
    # Set up logger
    logger = setup_logger('cc_enhancer.wrapper')
    
    # Log session start
    log_session_start(logger, 'run_roles_wrapper.py', sys.argv[1:])
    
    return_code = 0
    
    try:
        # Set up proper environment for Windows
        env = os.environ.copy()
        
        if platform.system() == 'Windows':
            # Required for Claude CLI to find Git Bash
            env['CLAUDE_CODE_GIT_BASH_PATH'] = r'C:\Program Files\Git\bin\bash.exe'
            # Required for Windows .cmd file execution
            env['COMSPEC'] = r'C:\Windows\System32\cmd.exe'
            logger.info(f"Windows environment configured - Git Bash: {env['CLAUDE_CODE_GIT_BASH_PATH']}")
        
        # Pass all command line arguments to run_roles.py
        cmd = ['python', 'run_roles.py'] + sys.argv[1:]
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Run with the fixed environment
        result = subprocess.run(cmd, env=env)
        return_code = result.returncode
        
        if return_code != 0:
            logger.error(f"run_roles.py exited with non-zero return code: {return_code}")
            
    except Exception as e:
        log_exception(logger, e, "run_roles_wrapper.py")
        return_code = 1
    finally:
        # Log session end
        log_session_end(logger, 'run_roles_wrapper.py', return_code)
        sys.exit(return_code)

if __name__ == '__main__':
    main()