# Activate the existing virtual environment
$venvActivateScript = ".\.venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvActivateScript)) {
    Write-Host "Virtual environment activation script not found at $venvActivateScript"
    exit 1
}

. $venvActivateScript

# Set local development environment variables (current session only)
$env:ALLOW_ACTOR_OVERRIDE = "true"
$env:APP_DATA_DIR = ".\data"

# Launch the FastAPI development server
python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000