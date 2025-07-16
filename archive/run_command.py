import subprocess
import sys

# Run the exact command
command = ['python', 'run_claude.py', 'lOkk at my snake game, is it safe to run?', '--dangerously-skip-permissions']

try:
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)
except Exception as e:
    print(f"Error running command: {e}", file=sys.stderr)
    sys.exit(1)