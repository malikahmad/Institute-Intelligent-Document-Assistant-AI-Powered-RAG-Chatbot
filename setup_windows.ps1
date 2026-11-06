$ErrorActionPreference = "Stop"
if (Get-Command python -ErrorAction SilentlyContinue) { $Python = "python" }
elseif (Get-Command python3 -ErrorAction SilentlyContinue) { $Python = "python3" }
else { throw "Python not found. Install Python 3.11/3.12 and enable Add Python to PATH." }
& $Python --version
if (-not (Test-Path ".venv")) { & $Python -m venv .venv }
$Vpy = Join-Path (Get-Location) ".venv\Scripts\python.exe"
& $Vpy -m pip install --upgrade pip
& $Vpy -m pip install -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
New-Item -ItemType Directory -Force uploads,vector_db | Out-Null
Write-Host "Setup complete. Run .\.venv\Scripts\python.exe app.py"
