# Code Review Script Documentation

## Overview

The Code Review Script is an automated system that runs Claude AI with different role-based prompts to perform comprehensive code reviews. It analyzes recent git commits through multiple specialized lenses, each focusing on specific aspects of code quality and safety.

## Components

### 1. `run_roles.py` - Main Orchestrator
The primary script that coordinates the entire review process.

**Key Features:**
- Loads role configurations from JSON
- Parses prompt templates from XML
- Automatically includes git diff from the last commit
- Executes Claude AI with different role-based prompts sequentially
- Supports configurable delays between role executions

**Command Line Arguments:**
- `--config`: Path to roles configuration JSON (default: `roles_config.json`)
- `--prompt-library`: Path to prompt library XML (default: `prompt_library.xml`)
- `--delay`: Seconds between role executions (default: 2)
- `--additional-context`: Additional context to append to ALL active roles (roles are configured in roles_config.json)

**Usage Example:**
```bash
python run_roles.py --delay 5 --additional-context "Focus on the new API endpoints"
```

### 2. `prompt_library.xml` - Role Prompt Templates
Contains the structured prompts for each review role with three severity levels:
- **Critical**: Must-fix issues that could cause immediate failures
- **Standard**: Common issues that should be addressed
- **Best Practice**: Optimization and enhancement opportunities

**Available Roles:**
1. **Error Handling**: Reviews exception handling and error recovery
2. **Security Review**: Identifies vulnerabilities and security risks
3. **Performance Review**: Analyzes performance bottlenecks
4. **Code Quality**: Evaluates maintainability and code structure
5. **Testing Coverage**: Assesses test completeness
6. **Dependency Audit**: Reviews third-party dependencies
7. **API Design**: Evaluates API consistency and design
8. **Logging Monitoring**: Reviews logging and observability
9. **Data Validation**: Checks input validation and sanitization
10. **Concurrency Review**: Identifies race conditions and deadlocks
11. **Deployment Readiness**: Verifies production readiness
12. **Accessibility Compliance**: Checks WCAG compliance
13. **Logging Implementation**: Ensures logging consistency
14. **Requirement Fulfillment**: Verifies implementation matches requirements
15. **Integration Compatibility**: Checks system integration points
16. **State and Data Flow**: Reviews data flow and state management

### 3. `roles_config.json` - Role Configuration
Controls which roles are active and which severity levels to include.

**Structure:**
```json
{
  "roles": {
    "role_name": {
      "critical": true/false,
      "standard": true/false,
      "best_practice": true/false
    }
  }
}
```

**Currently Active Roles (based on provided config):**
- Error Handling (critical + standard)
- Logging Monitoring (critical + standard)
- Data Validation (critical only)
- Requirement Fulfillment (all severities)
- Integration Compatibility (all severities)
- State and Data Flow (all severities)

### 4. `git_diff_last_commit.py` - Standalone Git Diff Utility
A helper script that shows differences between the last commit and the previous one.

**Features:**
- Displays commit information for the last two commits
- Shows full diff between HEAD and HEAD~1
- Handles edge cases (first commit, git not installed)
- Can be run independently for quick diff viewing

**Usage:**
```bash
python git_diff_last_commit.py
```

### 5. `run_roles_wrapper.py` - Windows Environment Wrapper
A wrapper script that ensures proper environment setup for running Claude CLI on Windows.

**Purpose:**
- Automatically sets required environment variables for Claude CLI execution
- Handles Windows-specific command execution issues
- Ensures compatibility across different shell environments (PowerShell, Git Bash, cmd)

**Features:**
- Sets `CLAUDE_CODE_GIT_BASH_PATH` for Claude to find Git Bash
- Sets `COMSPEC` for proper Windows .cmd file execution
- Passes all command-line arguments to `run_roles.py`
- Cross-platform compatible (only applies fixes on Windows)

**Usage:**
```bash
python run_roles_wrapper.py --additional-context "Your context here"
```

## How It Works

1. **Initialization**: 
   - `run_roles.py` loads the configuration files
   - Identifies which roles are enabled with their severity levels

2. **Git Integration**:
   - Automatically captures the diff from the last commit
   - Appends this diff to each role prompt for context

3. **Role Execution**:
   - For each enabled role, constructs a prompt combining:
     - Role-specific prompts for enabled severity levels
     - Any additional user-provided context
     - Git diff from the last commit
   - Executes `run_claude.py` with the constructed prompt

4. **Output**:
   - Displays the full prompt being sent to Claude
   - Shows Claude's analysis for each role
   - Waits between role executions (configurable delay)

## Typical Workflow

1. **Make code changes** and commit them to git
2. **Configure roles** in `roles_config.json` based on review needs
3. **Run the review**:
   ```bash
   # Recommended for Windows users:
   python run_roles_wrapper.py
   
   # Or with direct environment setup:
   python run_roles.py
   ```
4. **Review output** from each role and address identified issues

## Advanced Usage

### Custom Role Combinations
Enable different severity levels for targeted reviews:
```json
{
  "security review": {
    "critical": true,    // Only critical security issues
    "standard": false,
    "best_practice": false
  }
}
```

### Adding Context
Provide additional context for all roles:
```bash
# Using the wrapper (recommended for Windows):
python run_roles_wrapper.py --additional-context "This code will handle financial transactions"

# Or directly:
python run_roles.py --additional-context "This code will handle financial transactions"
```

### Adjusting Timing
Increase delay for more time to review each output:
```bash
python run_roles.py --delay 10
```

## Benefits

1. **Comprehensive Coverage**: Multiple specialized perspectives on code changes
2. **Configurable Depth**: Choose between critical-only or full analysis
3. **Automated Context**: Git diff automatically included for relevance
4. **Consistent Reviews**: Same review criteria applied every time
5. **Flexible Focus**: Enable only the roles relevant to your changes

## Troubleshooting

### Windows Environment Issues
If you encounter "Claude CLI is not installed or not in PATH" errors when running from certain environments (e.g., Git Bash, WSL):

**Problem:** Different shell environments may have different PATH or environment variable configurations.

**Solution 1 (Recommended):** Use the wrapper script:
```bash
python run_roles_wrapper.py --additional-context "Your context"
```

**Solution 2:** Set environment variables manually:
```bash
export CLAUDE_CODE_GIT_BASH_PATH="C:\\Program Files\\Git\\bin\\bash.exe"
export COMSPEC="C:\\Windows\\System32\\cmd.exe"
python run_roles.py --additional-context "Your context"
```

**Root Cause:** 
- Claude CLI requires Git Bash on Windows (`CLAUDE_CODE_GIT_BASH_PATH`)
- Windows .cmd files require proper `COMSPEC` setting
- Different shells (PowerShell vs Git Bash) handle these differently

## Notes

- The script requires `run_claude.py` to be present in the same directory
- Git must be initialized and have at least one commit
- Output encoding is handled for Windows compatibility
- Each role runs independently with its own Claude instance
- On Windows, use `run_roles_wrapper.py` for best compatibility