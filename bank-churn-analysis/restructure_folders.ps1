# Folder Restructuring Script
# Run this from PowerShell after closing VS Code

$desktop = "$env:USERPROFILE\Desktop"

# Step 1: Rename main folders
Rename-Item -Path "$desktop\VS_Code" -NewName "Dev-Workspace"
Write-Host "Renamed VS_Code -> Dev-Workspace"

Rename-Item -Path "$desktop\Dev-Workspace\Python" -NewName "Data-Science"
Write-Host "Renamed Python -> Data-Science"

Rename-Item -Path "$desktop\Dev-Workspace\Data-Science\Churn_analysis" -NewName "bank-churn-analysis"
Write-Host "Renamed Churn_analysis -> bank-churn-analysis"

# Step 2: Create subfolders
$projectPath = "$desktop\Dev-Workspace\Data-Science\bank-churn-analysis"
New-Item -ItemType Directory -Path "$projectPath\data" -Force | Out-Null
New-Item -ItemType Directory -Path "$projectPath\scripts" -Force | Out-Null
Write-Host "Created data/ and scripts/ folders"

# Step 3: Move files to appropriate locations
# CSVs -> data/
Move-Item -Path "$projectPath\*.csv" -Destination "$projectPath\data\" -Force
Write-Host "Moved CSV files to data/"

# Python scripts -> scripts/
Move-Item -Path "$projectPath\*.py" -Destination "$projectPath\scripts\" -Force
Write-Host "Moved Python scripts to scripts/"

# Visualizations folder -> data/visualizations
if (Test-Path "$projectPath\visualizations") {
    Move-Item -Path "$projectPath\visualizations" -Destination "$projectPath\data\" -Force
    Write-Host "Moved visualizations folder to data/"
}

# TXT files -> data/
Move-Item -Path "$projectPath\*.txt" -Destination "$projectPath\data\" -Force -ErrorAction SilentlyContinue

Write-Host "`nRestructuring complete! New structure:"
Get-ChildItem -Path $projectPath -Recurse -Depth 1 | Select-Object FullName
