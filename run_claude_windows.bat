@echo off
setlocal enabledelayedexpansion

REM Set the Git Bash path for Claude
set "CLAUDE_CODE_GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe"

REM Check if claude is available
where claude.cmd >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: claude.cmd not found in PATH.
    echo Please ensure Claude Code is installed: npm install -g @anthropic-ai/claude-code
    echo And that npm's global directory is in your PATH.
    exit /b 1
)

REM Parse arguments - check if first arg is a role
set "role="
set "prompt="
set "args="

if "%~1"=="" (
    echo Usage: run_claude_windows.bat [role] "prompt"
    echo   or: run_claude_windows.bat "prompt"
    exit /b 1
)

REM Check if first argument might be a role (doesn't start with -)
set "first_arg=%~1"
if not "%first_arg:~0,1%"=="-" if not "%~2"=="" (
    REM Role mode
    set "role=%~1"
    shift
    set "prompt=%~1"
    shift
) else (
    REM Simple mode
    set "prompt=%~1"
    shift
)

REM Collect remaining arguments
:collect_args
if not "%~1"=="" (
    set "args=!args! %1"
    shift
    goto collect_args
)

REM Run Python script with proper arguments
if defined role (
    echo Running Claude with role '%role%'
    echo User prompt: %prompt%
    python "%~dp0run_claude.py" "%role%" "%prompt%" %args%
) else (
    echo Running Claude with prompt: %prompt%
    python "%~dp0run_claude.py" "%prompt%" %args%
)

exit /b %errorlevel%