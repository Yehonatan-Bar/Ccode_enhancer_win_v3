#!/usr/bin/env python3
"""
Simple script to run Claude and print the response.
Sets up the required environment for Claude on Windows.
Supports role-based prompting with git diff integration.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path
import xml.etree.ElementTree as ET
import threading
import queue
import time
from datetime import datetime
from cc_logging import setup_logger, log_exception


def validate_claude_installation():
    """Check if Claude CLI is installed and accessible."""
    logger = setup_logger('cc_enhancer.claude')
    logger.debug("Validating Claude CLI installation")
    
    commands_to_try = ['claude', 'claude-code']
    
    # On Windows, also try with .cmd extension and full npm path
    if platform.system() == "Windows":
        npm_path = os.path.expanduser(r"~\AppData\Roaming\npm")
        commands_to_try.extend([
            'claude.cmd',
            'claude-code.cmd',
            os.path.join(npm_path, 'claude.cmd'),
            os.path.join(npm_path, 'claude-code.cmd')
        ])
    
    for cmd in commands_to_try:
        try:
            # Try with shell=True on Windows to handle .cmd files properly
            shell = platform.system() == "Windows" and cmd.endswith('.cmd')
            logger.debug(f"Trying command: {cmd} (shell={shell})")
            result = subprocess.run(
                [cmd, '--version'] if not shell else f'"{cmd}" --version',
                capture_output=True,
                text=True,
                shell=shell
            )
            if result.returncode == 0:
                logger.info(f"Found working Claude CLI: {cmd}")
                return True
            else:
                logger.debug(f"Command {cmd} failed with return code {result.returncode}")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            logger.debug(f"Command {cmd} not found or failed: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error checking {cmd}: {e}")
            continue
    
    logger.error("Claude CLI not found in any expected location")
    return False


def setup_claude_environment():
    """Set up CLAUDE_CODE_GIT_BASH_PATH if not already set."""
    logger = setup_logger('cc_enhancer.claude')
    logger.debug("Setting up Claude environment")
    
    # First check if Claude is installed
    if not validate_claude_installation():
        print("Error: Claude CLI is not installed or not in PATH.")
        print("Please install Claude Code first: npm install -g @anthropic-ai/claude-code")
        print("\nIf already installed, ensure npm's global directory is in your PATH:")
        try:
            npm_prefix = subprocess.run(['npm', 'config', 'get', 'prefix'], capture_output=True, text=True)
            if npm_prefix.returncode == 0:
                print(f"  Add to PATH: {npm_prefix.stdout.strip()}")
        except FileNotFoundError:
            print("  Note: npm command not found. Ensure Node.js is installed and in PATH.")
        return False
    
    if 'CLAUDE_CODE_GIT_BASH_PATH' in os.environ:
        return True
        
    # Find Git Bash
    git_bash_paths = [
        r'C:\Program Files\Git\bin\bash.exe',
        r'C:\Program Files (x86)\Git\bin\bash.exe',
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Git', 'bin', 'bash.exe'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Git', 'bin', 'bash.exe'),
    ]
    
    git_bash = None
    for path in git_bash_paths:
        if os.path.exists(path):
            git_bash = path
            break
    
    if not git_bash:
        print("Error: Git Bash not found. Please install Git for Windows from https://git-scm.com/download/win")
        return False
    
    # Set the environment variable for the current session
    os.environ['CLAUDE_CODE_GIT_BASH_PATH'] = git_bash
    
    # Try to set it permanently for the user
    try:
        subprocess.run([
            'powershell', '-Command',
            f'[Environment]::SetEnvironmentVariable("CLAUDE_CODE_GIT_BASH_PATH", "{git_bash}", "User")'
        ], capture_output=True)
        print(f"Set CLAUDE_CODE_GIT_BASH_PATH to: {git_bash}")
        print("Note: You may need to restart your terminal for the permanent setting to take effect.")
    except:
        pass
    
    return True


def get_claude_command():
    """Get the correct claude command to use."""
    logger = setup_logger('cc_enhancer.claude')
    logger.debug("Getting Claude command")
    
    commands_to_try = ['claude', 'claude-code']
    
    # On Windows, also try with .cmd extension and full npm path
    if platform.system() == "Windows":
        npm_path = os.path.expanduser(r"~\AppData\Roaming\npm")
        commands_to_try.extend([
            'claude.cmd',
            'claude-code.cmd',
            os.path.join(npm_path, 'claude.cmd'),
            os.path.join(npm_path, 'claude-code.cmd')
        ])
    
    for cmd in commands_to_try:
        try:
            # Try with shell=True on Windows to handle .cmd files properly
            shell = platform.system() == "Windows" and cmd.endswith('.cmd')
            logger.debug(f"Checking command availability: {cmd} (shell={shell})")
            result = subprocess.run(
                [cmd, '--version'] if not shell else f'"{cmd}" --version',
                capture_output=True,
                text=True,
                shell=shell
            )
            if result.returncode == 0:
                logger.info(f"Using Claude command: {cmd}")
                return cmd
            else:
                logger.debug(f"Command {cmd} failed with return code {result.returncode}")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            logger.debug(f"Command {cmd} not available: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error with command {cmd}: {e}")
            continue
    
    logger.error("No working Claude command found")
    return None


def create_log_file():
    """Create a log file with timestamp in the filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"claude_output_{timestamp}.txt"
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_filename)
    return log_path


def handle_interactive_prompts(process, output_queue, output_lines, log_file, timeout, logger):
    """Handle interactive prompts from Claude CLI with comprehensive prompt detection."""
    start_time = time.time()
    last_output_time = time.time()
    no_output_count = 0
    
    # Comprehensive prompt patterns with appropriate responses
    prompt_patterns = [
        # Question patterns
        ("?", None),  # Any question mark - determine response based on context
        ("y/n", "y"),
        ("yes/no", "yes"),
        ("continue", ""),  # Just Enter
        ("press enter", ""),
        ("press any key", ""),
        # Permission patterns
        ("permission", "1"),
        ("allow", "1"),
        ("do you want", "1"),
        ("would you like", "1"),
        # Confirmation patterns
        ("confirm", "y"),
        ("proceed", "y"),
        ("are you sure", "y"),
        # Pause patterns
        ("paused", ""),
        ("waiting", ""),
        ("[more]", ""),
        ("--more--", ""),
        # Auth patterns
        ("password:", ""),
        ("api key:", ""),
        ("authenticate", ""),
    ]
    
    while True:
        # Check timeout
        if time.time() - start_time > timeout:
            logger.warning(f"Timeout after {timeout} seconds")
            process.terminate()
            return False
        
        # Check if process has finished
        if process.poll() is not None:
            return True
        
        # Read output with timeout
        try:
            line = output_queue.get(timeout=0.5)
            output_lines.append(line)
            last_output_time = time.time()
            no_output_count = 0
            
            # Write to log file
            log_file.write(line)
            log_file.flush()
            
            # Check for prompts using multiple patterns
            line_lower = line.lower().strip()
            for pattern, response in prompt_patterns:
                if pattern in line_lower:
                    logger.info(f"Detected prompt pattern '{pattern}' in: {line.strip()}")
                    print(f"Detected prompt pattern '{pattern}' in: {line.strip()}")
                    
                    if response is None:
                        # Try to determine appropriate response
                        if "y/n" in line_lower or "yes/no" in line_lower:
                            response = "y"
                        elif "continue" in line_lower or "press" in line_lower:
                            response = ""
                        elif "1)" in line or "option" in line_lower:
                            response = "1"  # Default to option 1
                        else:
                            response = ""  # Default to Enter
                    
                    print(f"Auto-responding with: '{response}' + Enter")
                    logger.info(f"Sending response: '{response}' + Enter")
                    try:
                        process.stdin.write(f"{response}\n")
                        process.stdin.flush()
                    except Exception as e:
                        logger.error(f"Failed to send response: {e}")
                    break
                
        except queue.Empty:
            # No output received
            no_output_count += 1
            
            # Progressive intervention based on no output duration
            time_since_output = time.time() - last_output_time
            
            if time_since_output > 10.0 and no_output_count % 20 == 0:  # Every 10 seconds
                logger.info(f"No output for {int(time_since_output)} seconds, sending Enter key...")
                print(f"No output detected for {int(time_since_output)} seconds, sending Enter...")
                try:
                    process.stdin.write("\n")
                    process.stdin.flush()
                except:
                    pass
            
            elif time_since_output > 30.0 and no_output_count % 60 == 0:  # Every 30 seconds
                logger.warning(f"No output for {int(time_since_output)} seconds, trying 'y' + Enter...")
                print(f"No output for {int(time_since_output)} seconds, sending 'y' + Enter...")
                try:
                    process.stdin.write("y\n")
                    process.stdin.flush()
                except:
                    pass
            
            elif time_since_output > 60.0:  # After 60 seconds
                logger.error("No output for over 60 seconds, process may be stuck")
                print("WARNING: No output for over 60 seconds, process appears stuck")
                # Don't terminate yet, give it more time
                
            continue
            
        except Exception as e:
            logger.error(f"Error reading output: {e}")
            print(f"Error reading output: {e}")
            return False

def run_claude_windows(prompt, skip_permissions=False, timeout=300):
    """Run Claude on Windows with interactive prompt handling."""
    logger = setup_logger('cc_enhancer.claude')
    logger.info("=" * 60)
    logger.info("Starting Claude execution on Windows")
    logger.info(f"Skip permissions: {skip_permissions}")
    logger.info(f"Timeout: {timeout}s")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"PATH: {os.environ.get('PATH', 'Not set')}")
    logger.info(f"Prompt length: {len(prompt)} characters")
    logger.info("=" * 60)
    
    # Ensure environment is set up
    if not setup_claude_environment():
        logger.error("Failed to set up Claude environment")
        return "", -1
    
    # Get the correct claude command
    claude_cmd = get_claude_command()
    if not claude_cmd:
        logger.error("CRITICAL: No Claude command found - this is likely the MODULE_NOT_FOUND issue")
        logger.error("Check that Claude Code is installed: npm install -g @anthropic-ai/claude-code")
        return "", -2
    
    # Create individual session log file (in addition to cc_app.log)
    log_path = create_log_file()
    print(f"Logging Claude output to: {log_path}")
    logger.info(f"Creating session log file: {log_path}")
    
    # Build command - use stdin for long prompts
    cmd = [claude_cmd, '--print']
    if skip_permissions:
        cmd.append('--dangerously-skip-permissions')
    
    # Check if prompt is too long for command line (Windows limit ~8000 chars)
    use_stdin = len(prompt) > 4000 or platform.system() == "Windows"
    
    if not use_stdin:
        cmd.append(prompt)
    
    try:
        # Create a copy of the environment with the Git Bash path
        env = os.environ.copy()
        
        # Log environment details
        logger.debug(f"Environment variables: COMSPEC={env.get('COMSPEC', 'Not set')}")
        logger.debug(f"Environment variables: PATHEXT={env.get('PATHEXT', 'Not set')}")
        
        # Ensure Git Bash path is set in the environment
        if 'CLAUDE_CODE_GIT_BASH_PATH' in env:
            print(f"Using Git Bash at: {env['CLAUDE_CODE_GIT_BASH_PATH']}")
            logger.info(f"Git Bash path configured: {env['CLAUDE_CODE_GIT_BASH_PATH']}")
        
        # Use Popen for interactive handling
        # Use shell=True for .cmd files on Windows
        use_shell = platform.system() == "Windows" and claude_cmd.endswith('.cmd')
        logger.info(f"Executing Claude with shell={use_shell}, stdin={use_stdin}")
        logger.debug(f"Full command: {' '.join(cmd)}")
        
        if use_stdin:
            # When using stdin, we need to use a different approach
            cmd_str = ' '.join(f'"{c}"' if ' ' in c else c for c in cmd) if use_shell else cmd
            logger.debug(f"Command string for shell: {cmd_str}")
            process = subprocess.Popen(
                cmd_str,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True,
                shell=use_shell
            )
            
            # Send the prompt via stdin but DON'T close it for interactive handling
            process.stdin.write(prompt)
            process.stdin.flush()  # Flush instead of close to keep stdin open
        else:
            process = subprocess.Popen(
                ' '.join(f'"{c}"' if ' ' in c else c for c in cmd) if use_shell else cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True,
                shell=use_shell
            )
        
        # Collect output
        output_lines = []
        output_queue = queue.Queue()
        
        # Open log file for writing
        log_file = open(log_path, 'w', encoding='utf-8')
        log_file.write(f"Claude session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Prompt: {prompt}\n")
        log_file.write("=" * 80 + "\n\n")
        log_file.flush()
        
        def read_output(pipe, queue):
            """Read output from pipe and put in queue."""
            try:
                for line in iter(pipe.readline, ''):
                    if line:
                        queue.put(line)
                pipe.close()
            except:
                pass
        
        # Start threads to read stdout and stderr
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, output_queue))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, output_queue))
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()
        
        # Use the helper function to handle interactive prompts
        success = handle_interactive_prompts(process, output_queue, output_lines, log_file, timeout, logger)
        if not success and process.poll() is None:
            # Timeout occurred
            return "", -1
        
        # Wait for threads to finish
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)
        
        # Get remaining output
        while not output_queue.empty():
            try:
                output_lines.append(output_queue.get_nowait())
            except queue.Empty:
                break
        
        # Get return code
        returncode = process.poll()
        output = ''.join(output_lines)
        
        # Close log file
        log_file.write("\n" + "=" * 80 + "\n")
        log_file.write(f"Claude session ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Return code: {returncode}\n")
        log_file.close()
        
        # Check if claude command was not found
        if returncode == 127 or "not found" in output.lower():
            logger.error(f"Claude command not found (return code: {returncode})")
            logger.error(f"Output contained: {output[:200]}")
            return "", -2
        
        # Check for the specific MODULE_NOT_FOUND error
        if "MODULE_NOT_FOUND" in output or "Cannot find module" in output:
            logger.error("CRITICAL: MODULE_NOT_FOUND error detected!")
            logger.error(f"Full error output: {output}")
            logger.error("This indicates Claude CLI is not properly installed or npm modules are corrupted")
        
        logger.info(f"Claude process completed with return code: {returncode}")
        return output, returncode
        
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError when running Claude: {e}")
        log_exception(logger, e, "run_claude_windows")
        return "", -2
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Unexpected error in run_claude_windows: {type(e).__name__}: {e}")
        log_exception(logger, e, "run_claude_windows")
        return "", -3


def run_claude_unix(prompt, skip_permissions=False, timeout=300):
    """Run Claude on Unix-like systems with interactive prompt handling."""
    logger = setup_logger('cc_enhancer.claude')
    logger.info("Starting Claude execution on Unix")
    
    # Get the correct claude command
    claude_cmd = get_claude_command()
    if not claude_cmd:
        logger.error("No Claude command found on Unix system")
        return "", -2
    
    # Create individual session log file (in addition to cc_app.log)
    log_path = create_log_file()
    print(f"Logging Claude output to: {log_path}")
    logger.info(f"Creating session log file: {log_path}")
        
    cmd = [claude_cmd, '--print']
    if skip_permissions:
        cmd.append('--dangerously-skip-permissions')
    
    # Check if prompt is too long for command line
    use_stdin = len(prompt) > 4000
    
    if not use_stdin:
        cmd.append(prompt)
    
    try:
        # Use Popen for interactive handling
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Send prompt via stdin if needed
        if use_stdin:
            process.stdin.write(prompt)
            process.stdin.flush()  # Flush instead of close to keep stdin open for interactive handling
        
        # Collect output
        output_lines = []
        output_queue = queue.Queue()
        
        # Open log file for writing
        log_file = open(log_path, 'w', encoding='utf-8')
        log_file.write(f"Claude session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Prompt: {prompt}\n")
        log_file.write("=" * 80 + "\n\n")
        log_file.flush()
        
        def read_output(pipe, queue):
            """Read output from pipe and put in queue."""
            try:
                for line in iter(pipe.readline, ''):
                    if line:
                        queue.put(line)
                pipe.close()
            except:
                pass
        
        # Start threads to read stdout and stderr
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, output_queue))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, output_queue))
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()
        
        # Use the helper function to handle interactive prompts
        success = handle_interactive_prompts(process, output_queue, output_lines, log_file, timeout, logger)
        if not success and process.poll() is None:
            # Timeout occurred
            return "", -1
        
        # Wait for threads to finish
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)
        
        # Get remaining output
        while not output_queue.empty():
            try:
                output_lines.append(output_queue.get_nowait())
            except queue.Empty:
                break
        
        # Get return code
        returncode = process.poll()
        output = ''.join(output_lines)
        
        # Close log file
        log_file.write("\n" + "=" * 80 + "\n")
        log_file.write(f"Claude session ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Return code: {returncode}\n")
        log_file.close()
        
        # Check if claude command was not found
        if returncode == 127 or "not found" in output.lower():
            return "", -2
        
        return output, returncode
        
    except FileNotFoundError:
        return "", -2
    except Exception:
        return "", -3


def get_git_diff():
    """Get the diff between the last commit and the previous one."""
    try:
        result = subprocess.run(
            ['python', 'git_diff_last_commit.py'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running git_diff_last_commit.py: {e}", file=sys.stderr)
        return "Error retrieving git diff"


def load_prompts_from_xml(role):
    """Load prompts from prompt_library.xml for the given role."""
    try:
        tree = ET.parse('prompt_library.xml')
        root = tree.getroot()
        
        # Extract prompts from XML
        claude_pre_prompt = root.find(".//prompt[@key='claude pre prompt']").text
        pre_git_diff = root.find(".//prompt[@key='pre git diff']").text
        
        # Find role-specific prompt
        role_prompt_element = root.find(f".//roles/prompt[@key='{role}']")
        
        if role_prompt_element is None:
            available_roles = [elem.get('key') for elem in root.findall(".//roles/prompt")]
            print(f"Error: Role '{role}' not found in prompt_library.xml", file=sys.stderr)
            print(f"Available roles: {', '.join(available_roles)}")
            return None, None, None, available_roles
            
        role_prompt = role_prompt_element.text
        available_roles = [elem.get('key') for elem in root.findall(".//roles/prompt")]
        
        return claude_pre_prompt, pre_git_diff, role_prompt, available_roles
    except Exception as e:
        print(f"Error parsing prompt_library.xml: {e}", file=sys.stderr)
        return None, None, None, []


def main():
    """Main function to run Claude with a prompt and print the response."""
    logger = setup_logger('cc_enhancer.claude')
    logger.info("run_claude.py started")
    logger.info(f"Arguments: {sys.argv}")
    
    # Default values
    prompt = "tell me about this project"
    skip_permissions = False
    use_role = False
    role = None
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    # Check for permission flags first
    if '--skip-permissions' in sys.argv or '--force-permissions' in sys.argv or '--dangerously-skip-permissions' in sys.argv:
        skip_permissions = True
        # Remove the flag from args
        args = [arg for arg in args if arg not in ['--skip-permissions', '--force-permissions', '--dangerously-skip-permissions']]
    
    # Check for role usage (first arg is role)
    if len(args) >= 2 and not args[0].startswith('--'):
        # Role mode: python run_claude.py <role> <prompt>
        use_role = True
        role = args[0]
        prompt = ' '.join(args[1:])
    elif len(args) >= 1:
        # Normal mode: python run_claude.py <prompt>
        prompt = ' '.join(args)
    
    # If using role mode, build the combined prompt
    if use_role:
        claude_pre_prompt, pre_git_diff, role_prompt, available_roles = load_prompts_from_xml(role)
        
        if role_prompt is None:
            print("\nUsage: python run_claude.py <role> <prompt>")
            print("   or: python run_claude.py <prompt>")
            sys.exit(1)
        
        # Get git diff
        git_diff_output = get_git_diff()
        
        # Build combined prompt
        prompt = f"{claude_pre_prompt}: {prompt}\n\n{pre_git_diff}:\n{git_diff_output}\n\n{role_prompt}"
        
        print(f"Running Claude with role '{role}'")
        print(f"User prompt: {' '.join(args[1:])[:50]}{'...' if len(' '.join(args[1:])) > 50 else ''}")
    else:
        print(f"Running Claude with prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
    
    print("Waiting for Claude's response...")
    
    # Run Claude based on platform
    logger.info(f"Running on platform: {platform.system()}")
    if platform.system() == "Windows":
        output, code = run_claude_windows(prompt, skip_permissions)
    else:
        output, code = run_claude_unix(prompt, skip_permissions)
    
    if code == 0:
        print("\n" + "="*60)
        print("Claude's Response:")
        print("="*60)
        print(output)
        print("="*60)
        logger.info("Claude execution completed successfully")
    else:
        print(f"\nClaude failed with return code: {code}")
        logger.error(f"Claude execution failed with code: {code}")
        if output:
            print(f"Output: {output}")
            logger.error(f"Error output: {output[:500]}")
        if code == -1:
            print("Timeout occurred - Claude took too long to respond")
        elif code == -2:
            print("Claude command not found - ensure Claude Code is installed")
        elif code == -3:
            print("An unexpected error occurred")
        elif code == 1:
            print("\nTroubleshooting:")
            print("1. The CLAUDE_CODE_GIT_BASH_PATH environment variable has been set.")
            print("2. Try opening a new terminal window and running this script again.")
            print("3. Or run Claude directly: claude --print \"your prompt\"")
            print("4. If it still doesn't work, try running from Git Bash directly.")
            if use_role:
                print("\nUsage: python run_claude.py <role> <prompt>")
                print("   or: python run_claude.py <prompt>")
    
    # Exit with appropriate code
    logger.info(f"run_claude.py exiting with code: {code if code >= 0 else 1}")
    sys.exit(code if code >= 0 else 1)


if __name__ == "__main__":
    main()