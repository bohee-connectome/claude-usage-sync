# Setup Windows Task Scheduler for automatic daily sync
# Run this script as Administrator

$TaskName = "ClaudeUsageAutoSync"
$ScriptPath = "$env:USERPROFILE\claude-usage-tracker\scripts\auto_sync.py"
$PythonPath = (Get-Command python).Source
$LogPath = "$env:USERPROFILE\claude-usage-tracker\logs"

# Create logs directory
New-Item -ItemType Directory -Force -Path $LogPath | Out-Null

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "Setting up automatic daily sync for Claude Usage Tracker" -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create action
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument $ScriptPath `
    -WorkingDirectory "$env:USERPROFILE\claude-usage-tracker"

# Create trigger (daily at 11:59 PM)
$Trigger = New-ScheduledTaskTrigger -Daily -At "23:59"

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Automatically sync Claude usage statistics to Git repository" `
    -User $env:USERNAME

Write-Host ""
Write-Host "Task created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Task Details:" -ForegroundColor Cyan
Write-Host "  Name:     $TaskName"
Write-Host "  Schedule: Daily at 11:59 PM"
Write-Host "  Script:   $ScriptPath"
Write-Host "  Logs:     $LogPath"
Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""
Write-Host "You can also run the sync manually with:" -ForegroundColor Yellow
Write-Host "  ccusage-auto-sync" -ForegroundColor White
Write-Host ""
Write-Host "To check the task status:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host ""
Write-Host "To run the task immediately:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host ""
Write-Host "To disable the task:" -ForegroundColor Yellow
Write-Host "  Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
