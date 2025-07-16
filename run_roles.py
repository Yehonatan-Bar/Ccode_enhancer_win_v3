import subprocess
import sys
import xml.etree.ElementTree as ET
import argparse
import time
import os

def get_git_diff_last_commit():
    """Get the diff between the last commit and the previous one."""
    try:
        # Check if we're in a git repository
        subprocess.run(['git', 'rev-parse', '--git-dir'], capture_output=True, check=True)
        
        # Get the diff between HEAD and HEAD~1
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout:
            return f"\n\n# Git Diff from Last Commit:\n{result.stdout}"
        elif "ambiguous argument 'HEAD~1'" in result.stderr:
            return "\n\n# Git Diff: This appears to be the first commit (no previous commit exists)."
        else:
            return ""
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    except Exception:
        return ""

def parse_prompt_library(xml_file):
    """Parse the prompt library XML and extract role prompts."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    role_prompts = {}
    roles_element = root.find('roles')
    
    if roles_element is not None:
        for prompt in roles_element.findall('prompt'):
            key = prompt.get('key')
            text = prompt.text
            if key and text:
                role_prompts[key] = text
    
    return role_prompts

def run_claude_with_role(role_prompt, additional_prompt=""):
    """Run the claude command with the given role prompt."""
    # Get git diff from last commit
    git_diff = get_git_diff_last_commit()
    
    # Append additional prompt and git diff to the role prompt
    enhanced_prompt = role_prompt + additional_prompt + git_diff
    
    command = ['python', 'run_claude.py', enhanced_prompt, '--dangerously-skip-permissions']
    
    try:
        print(f"\n{'='*60}")
        print(f"Running Claude with role prompt...")
        print(f"{'='*60}\n")
        
        # Run the command and wait for it to complete
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(f"Error output: {result.stderr}", file=sys.stderr)
        
        if result.returncode != 0:
            print(f"Command failed with return code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Run Claude with different role-based prompts')
    parser.add_argument('roles', nargs='+', help='List of roles to use (e.g., "error handling" "security review")')
    parser.add_argument('--prompt-library', default='prompt_library.xml', help='Path to prompt library XML file')
    parser.add_argument('--delay', type=int, default=2, help='Delay in seconds between each role execution')
    parser.add_argument('--prompt', type=str, default='', help='Additional prompt string to concatenate with role prompts')
    
    args = parser.parse_args()
    
    # Parse the prompt library
    try:
        role_prompts = parse_prompt_library(args.prompt_library)
    except Exception as e:
        print(f"Error parsing prompt library: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate that all requested roles exist
    invalid_roles = [role for role in args.roles if role not in role_prompts]
    if invalid_roles:
        print(f"Error: The following roles were not found in the prompt library:")
        for role in invalid_roles:
            print(f"  - {role}")
        print(f"\nAvailable roles:")
        for role in sorted(role_prompts.keys()):
            print(f"  - {role}")
        sys.exit(1)
    
    # Run Claude for each role
    print(f"Running Claude with {len(args.roles)} role(s)...")
    
    for i, role in enumerate(args.roles):
        print(f"\n{'#'*60}")
        print(f"# Role {i+1}/{len(args.roles)}: {role}")
        print(f"{'#'*60}")
        
        # Get the git diff to show what will be included
        git_diff = get_git_diff_last_commit()
        full_prompt = role_prompts[role] + args.prompt + git_diff
        
        print(f"\n## Full prompt being sent to Claude:")
        print(f"{'-'*60}")
        print(full_prompt)
        print(f"{'-'*60}\n")
        
        success = run_claude_with_role(role_prompts[role], args.prompt)
        
        if not success:
            print(f"\nWarning: Role '{role}' execution failed")
        
        # Add delay between executions (except for the last one)
        if i < len(args.roles) - 1:
            print(f"\nWaiting {args.delay} seconds before next role...")
            time.sleep(args.delay)
    
    print(f"\n{'='*60}")
    print("All roles completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()