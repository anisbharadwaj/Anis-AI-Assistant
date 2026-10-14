# PowerShell setup script for Windows development environment
param()

Write-Host "Setting up ANIS AI development environment..."

# Create virtual environment
python -m venv .venv

# Activate and install requirements
Write-Host "Installing Python packages (this may take a few minutes)..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Install Playwright browsers
Write-Host "Installing Playwright browsers..."
.\.venv\Scripts\python.exe -m playwright install

Write-Host "Setup complete. To run the app:"
Write-Host "> .\\.venv\\Scripts\\Activate.ps1"
Write-Host "> python app.py"
