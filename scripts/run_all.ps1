<#
One-click runner for Windows (PowerShell).

What it does:
- Validates repo root by checking core files (app.py and ui/avatar/index.html)
- Creates a Python virtualenv at .venv if missing
- Installs requirements.txt into the venv (unless -NoInstall is passed)
- Starts run_backend.py in a new PowerShell window if it exists
- Starts a local static HTTP server (python -m http.server 8000) in a new PowerShell window
- Starts the desktop app (app.py) in a new PowerShell window
- Opens the avatar UI in the default browser

Usage (from repository root, PowerShell):
    .\scripts\run_all.ps1        # default: installs deps and launches services
    .\scripts\run_all.ps1 -NoInstall  # skip pip installs (faster)

Edge-cases handled:
- Missing Python on PATH -> abort with descriptive message
- Venv creation failures -> abort and show error
- Missing requirements.txt -> skip install and continue
- Missing run_backend.py -> warn and continue (UI fallback is local)
- Port collisions for 8000 -> warns and still attempts to start (user can change port manually)
- Uses explicit venv python/pip to avoid modifying global environment
#>

param(
    [switch]$NoInstall
)

$ErrorActionPreference = 'Stop'

try {
    $repo = (Get-Location).Path

    # Ensure we're at the repo root by checking expected files
    $mustExist = @('app.py', 'ui\avatar\index.html')
    foreach ($f in $mustExist) {
        if (-not (Test-Path (Join-Path $repo $f))) {
            Write-Error "Missing required file: $f. Please run this script from the repository root."
            exit 2
        }
    }

    # Find python
    $pythonCmd = $null
    try {
        $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
    } catch { }
    if (-not $pythonCmd) {
        try { $pythonCmd = (Get-Command py -ErrorAction SilentlyContinue).Source } catch { }
    }
    if (-not $pythonCmd) {
        Write-Error "Python not found on PATH. Please install Python 3.8+ and re-run."
        exit 3
    }

    Write-Host "Using Python: $pythonCmd"

    $venvPath = Join-Path $repo '.venv'
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating virtualenv at $venvPath..."
        & $pythonCmd -m venv $venvPath
    } else {
        Write-Host "Virtualenv already exists at $venvPath"
    }

    $venvPython = Join-Path $venvPath 'Scripts\python.exe'
    $venvPip = Join-Path $venvPath 'Scripts\pip.exe'
    if (-not (Test-Path $venvPython)) {
        Write-Error "Virtualenv python not found at $venvPython. Virtualenv creation likely failed."
        exit 4
    }

    if (-not $NoInstall) {
        Write-Host "Upgrading pip and installing requirements (this may take a moment)..."
        & $venvPip install --upgrade pip setuptools wheel
        if (Test-Path (Join-Path $repo 'requirements.txt')) {
            & $venvPip install -r (Join-Path $repo 'requirements.txt')
        } else {
            Write-Warning "requirements.txt not found. Skipping pip install."
        }

        # Ensure PySide6 for desktop app
        try {
            & $venvPip show PySide6 > $null 2>&1
        } catch {
            # pip show exits non-zero if not installed; attempt install
        }
        $pysideInstalled = (& $venvPip show PySide6 2>$null) -ne $null
        if (-not $pysideInstalled) {
            Write-Host "Installing PySide6 into virtualenv (desktop GUI dependency)..."
            & $venvPip install PySide6
        }
    } else {
        Write-Host "Skipping pip installs because -NoInstall was provided."
    }

    # Start backend if available
    $backendScript = Join-Path $repo 'run_backend.py'
    if (Test-Path $backendScript) {
        Write-Host "Starting backend in a new PowerShell window..."
        Start-Process -FilePath powershell -ArgumentList '-NoExit','-Command',"& `"$venvPython`" `"$backendScript`"" -WorkingDirectory $repo
    } else {
        Write-Warning "No run_backend.py present. Avatar UI will use local fallback behavior."
    }

    # Start static HTTP server for the UI
    $port = 8000
    Write-Host "Starting static HTTP server at http://127.0.0.1:$port in a new PowerShell window..."

    # Check if port is in use (best-effort)
    $portBusy = $false
    try {
        $netstat = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($netstat) { $portBusy = $true }
    } catch { }
    if ($portBusy) { Write-Warning "Port $port appears in use. The HTTP server may fail to start. You can change the port in the script." }

    Start-Process -FilePath powershell -ArgumentList '-NoExit','-Command',"& `"$venvPython`" -m http.server $port" -WorkingDirectory $repo

    # Launch desktop app
    Write-Host "Launching desktop application (app.py) in a new PowerShell window..."
    Start-Process -FilePath powershell -ArgumentList '-NoExit','-Command',"& `"$venvPython`" `"$(Join-Path $repo 'app.py')`"" -WorkingDirectory $repo

    # Open avatar UI in default browser
    Start-Sleep -Seconds 1
    $uiUrl = "http://127.0.0.1:$port/ui/avatar/index.html"
    Write-Host "Opening $uiUrl in your default browser..."
    Start-Process "explorer.exe" $uiUrl

    Write-Host "All processes launched. Check the newly opened PowerShell windows for output/logs." -ForegroundColor Green
    exit 0
} catch {
    Write-Error "An error occurred while running the script: $_"
    exit 10
}
