import subprocess
import sys
import xml.etree.ElementTree as ET
import argparse
import time
import os
import json

def get_git_diff_last_commit():
    """Get the diff by calling the external git_diff_last_commit.py script."""
    try:
        # Run the external script
        result = subprocess.run(
            ['python', 'git_diff_last_commit.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False
        )
        
        if result.returncode == 0 and result.stdout:
            # Extract just the diff part from the output
            lines = result.stdout.split('\n')
            diff_started = False
            diff_lines = []
            
            for line in lines:
                if line.startswith("Differences between the last commit"):
                    diff_started = True
                    continue
                elif diff_started and line.startswith("-" * 80):
                    continue  # Skip the separator line
                elif diff_started:
                    diff_lines.append(line)
            
            if diff_lines:
                # Remove empty lines at the end
                while diff_lines and not diff_lines[-1].strip():
                    diff_lines.pop()
                
                diff_content = '\n'.join(diff_lines)
                return f"\n\n# Git Diff (Uncommitted Changes):\n{diff_content}"
            else:
                return "\n\n# Git Diff: No uncommitted changes found."
        else:
            return "\n\n# Git Diff: Failed to get diff information."
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "\n\n# Git Diff: Could not run git_diff_last_commit.py"
    except Exception as e:
        return f"\n\n# Git Diff: Error - {type(e).__name__}: {e}"

def parse_prompt_library(xml_file):
    """Parse the prompt library XML and extract role prompts with severity levels."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    role_prompts = {}
    roles_element = root.find('roles')
    
    if roles_element is not None:
        for prompt in roles_element.findall('prompt'):
            key = prompt.get('key')
            if key:
                role_prompts[key] = {}
                # Extract severity levels
                for severity in ['critical', 'standard', 'best_practice']:
                    severity_elem = prompt.find(severity)
                    if severity_elem is not None and severity_elem.text:
                        role_prompts[key][severity] = severity_elem.text.strip()
    
    return role_prompts

def load_roles_config(config_file):
    """Load roles configuration from JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)

def build_role_prompt(role_name, role_prompts, severities):
    """Build a concatenated prompt for a role based on enabled severities."""
    if role_name not in role_prompts:
        return None
    
    prompt_parts = []
    severity_order = ['critical', 'standard', 'best_practice']
    
    for severity in severity_order:
        if severities.get(severity, False) and severity in role_prompts[role_name]:
            prompt_parts.append(f"[{severity.upper()}] {role_prompts[role_name][severity]}")
    
    return "\n\n".join(prompt_parts) if prompt_parts else None

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
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        # Print the output
        if result.stdout:
            try:
                print(result.stdout)
            except UnicodeEncodeError:
                print(result.stdout.encode('ascii', 'replace').decode('ascii'))
        
        if result.stderr:
            try:
                print(f"Error output: {result.stderr}", file=sys.stderr)
            except UnicodeEncodeError:
                print(f"Error output: {result.stderr.encode('ascii', 'replace').decode('ascii')}", file=sys.stderr)
        
        if result.returncode != 0:
            print(f"Command failed with return code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Run Claude with different role-based prompts from config',
        epilog='Example: python run_roles.py --additional-context "Focus on the new API endpoints"'
    )
    parser.add_argument('--config', default='roles_config.json', help='Path to roles configuration JSON file')
    parser.add_argument('--prompt-library', default='prompt_library.xml', help='Path to prompt library XML file')
    parser.add_argument('--delay', type=int, default=2, help='Delay in seconds between each role execution')
    parser.add_argument('--additional-context', type=str, default='', help='Additional context to append to ALL active roles (roles are configured in roles_config.json)')
    parser.add_argument('--prompt', type=str, default='', dest='additional_context', help='(DEPRECATED: use --additional-context) Additional context to append to all roles')
    
    args = parser.parse_args()
    
    # Show deprecation warning if --prompt was used
    if '--prompt' in sys.argv:
        print("WARNING: --prompt is deprecated. Please use --additional-context instead.", file=sys.stderr)
        print()
    
    # Load roles configuration
    try:
        config = load_roles_config(args.config)
        roles_config = config.get('roles', {})
    except Exception as e:
        print(f"Error loading roles configuration: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse the prompt library
    try:
        role_prompts = parse_prompt_library(args.prompt_library)
    except Exception as e:
        print(f"Error parsing prompt library: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get active roles from config
    active_roles = []
    for role_name, severities in roles_config.items():
        # Check if any severity is enabled for this role
        if any(severities.values()):
            active_roles.append((role_name, severities))
    
    if not active_roles:
        print("No roles are enabled in the configuration file.")
        sys.exit(0)
    
    # Run Claude for each active role
    print(f"Running Claude with {len(active_roles)} active role(s) from config...")
    
    for i, (role_name, severities) in enumerate(active_roles):
        print(f"\n{'#'*60}")
        print(f"# Role {i+1}/{len(active_roles)}: {role_name}")
        enabled_severities = [sev for sev, enabled in severities.items() if enabled]
        print(f"# Enabled severities: {', '.join(enabled_severities)}")
        print(f"{'#'*60}")
        
        # Build the role prompt from enabled severities
        role_prompt = build_role_prompt(role_name, role_prompts, severities)
        
        if not role_prompt:
            print(f"\nWarning: No prompts found for role '{role_name}'. Skipping...")
            continue
        
        # Get the git diff to show what will be included
        git_diff = get_git_diff_last_commit()
        full_prompt = role_prompt + args.additional_context + git_diff
        
        print(f"\n## Full prompt being sent to Claude:")
        print(f"{'-'*60}")
        try:
            print(full_prompt)
        except UnicodeEncodeError:
            # Fallback for Windows console encoding issues
            print(full_prompt.encode('ascii', 'replace').decode('ascii'))
        print(f"{'-'*60}\n")
        
        success = run_claude_with_role(role_prompt, args.additional_context)
        
        if not success:
            print(f"\nWarning: Role '{role_name}' execution failed")
        
        # Add delay between executions (except for the last one)
        if i < len(active_roles) - 1:
            print(f"\nWaiting {args.delay} seconds before next role...")
            time.sleep(args.delay)
    
    print(f"\n{'='*60}")
    print("All roles completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()