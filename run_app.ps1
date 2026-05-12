$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (!(Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating local virtual environment at .venv ..."
    python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -m streamlit run ui/streamlit_app.py
