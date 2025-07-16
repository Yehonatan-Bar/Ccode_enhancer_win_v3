import subprocess
import sys
import xml.etree.ElementTree as ET
import argparse
import time

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

def run_claude_with_role(role_prompt):
    """Run the claude command with the given role prompt."""
    command = ['python', 'run_claude.py', role_prompt, '--dangerously-skip-permissions']
    
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
        print(f"# Prompt: {role_prompts[role][:50]}...")
        print(f"{'#'*60}")
        
        success = run_claude_with_role(role_prompts[role])
        
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